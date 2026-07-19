import streamlit as st
import threading
import time
import uuid
import json
import logging
import traceback
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
import os
from tools.pdf_exporter import PDFExporterTool
from tools.pdf_reader import extract_pdf_text

from logger import logger
from crew import research_crew

load_dotenv()

if "GROQ" in os.environ and "GROQ_API_KEY" not in os.environ:
    os.environ["GROQ_API_KEY"] = os.environ["GROQ"]

import litellm


def clean_messages(messages):
    if not messages:
        return messages
    cleaned = []
    for msg in messages:
        if isinstance(msg, dict):
            msg_copy = msg.copy()
            msg_copy.pop("cache_breakpoint", None)
            cleaned.append(msg_copy)
        else:
            cleaned.append(msg)
    return cleaned


if not getattr(litellm.completion, "_is_patched", False):
    original_completion = litellm.completion


    def patched_completion(*args, **kwargs):
        if "messages" in kwargs:
            kwargs["messages"] = clean_messages(kwargs["messages"])
        elif len(args) > 1:
            args = list(args)
            args[1] = clean_messages(args[1])
            args = tuple(args)
        return original_completion(*args, **kwargs)


    patched_completion._is_patched = True
    litellm.completion = patched_completion

# Page configuration
st.set_page_config(page_title="AI Research Assistant", layout="wide")

# Thread infrastructure — stored in st.session_state so the same dict persists
# across Streamlit reruns. Previously used globals() which failed because
# Streamlit re-executes the script in a fresh namespace each rerun, so the
# worker thread wrote to one dict while the poller read from a new empty one.
if "THREAD_RESULTS" not in st.session_state:
    st.session_state.THREAD_RESULTS = {}
if "thread_parent_map" not in st.session_state:
    st.session_state.thread_parent_map = {}
if "thread_parent_map_lock" not in st.session_state:
    st.session_state.thread_parent_map_lock = threading.Lock()
if "thread_to_logs" not in st.session_state:
    st.session_state.thread_to_logs = {}
if "thread_to_start_time" not in st.session_state:
    st.session_state.thread_to_start_time = {}
if "thread_logs_lock" not in st.session_state:
    st.session_state.thread_logs_lock = threading.Lock()

THREAD_RESULTS = st.session_state.THREAD_RESULTS
thread_parent_map = st.session_state.thread_parent_map
thread_parent_map_lock = st.session_state.thread_parent_map_lock
thread_to_logs = st.session_state.thread_to_logs
thread_to_start_time = st.session_state.thread_to_start_time
thread_logs_lock = st.session_state.thread_logs_lock

thread_local = threading.local()

if not getattr(threading.Thread.start, "_is_patched", False):
    original_thread_start = threading.Thread.start


    def patched_thread_start(self, *args, **kwargs):
        parent_id = threading.get_ident()
        original_run = self.run

        def patched_run(*run_args, **run_kwargs):
            child_id = threading.get_ident()
            with thread_parent_map_lock:
                thread_parent_map[child_id] = parent_id
            try:
                return original_run(*run_args, **run_kwargs)
            finally:
                with thread_parent_map_lock:
                    thread_parent_map.pop(child_id, None)

        self.run = patched_run
        return original_thread_start(self, *args, **kwargs)


    patched_thread_start._is_patched = True
    threading.Thread.start = patched_thread_start


def setup_logging_for_thread(logs_list, start_time):
    thread_local.logs = logs_list
    thread_local.start_time = start_time
    tid = threading.get_ident()
    with thread_logs_lock:
        thread_to_logs[tid] = logs_list
        thread_to_start_time[tid] = start_time


def get_logs_for_current_thread():
    tid = threading.get_ident()
    visited = {tid}
    while tid is not None:
        with thread_logs_lock:
            if tid in thread_to_logs:
                return thread_to_logs[tid], thread_to_start_time.get(tid)
        with thread_parent_map_lock:
            tid = thread_parent_map.get(tid)
        if tid in visited:
            break
        if tid is not None:
            visited.add(tid)
    return None, None


class ThreadSafeLogHandler(logging.Handler):
    def emit(self, record):
        logs_list, start_time = get_logs_for_current_thread()
        if logs_list is not None:
            st_time = start_time if start_time is not None else record.created
            elapsed = record.created - st_time
            logs_list.append({
                "timestamp": record.created,
                "message": record.getMessage(),
                "level": record.levelname,
                "elapsed": elapsed,
                "type": "log",
            })


handler_exists = any(isinstance(h, ThreadSafeLogHandler) for h in logger.handlers)
if not handler_exists:
    logger.addHandler(ThreadSafeLogHandler())

root_logger = logging.getLogger()
root_handler_exists = any(isinstance(h, ThreadSafeLogHandler) for h in root_logger.handlers)
if not root_handler_exists:
    root_logger.addHandler(ThreadSafeLogHandler())

OUTPUT_DIR = Path("outputs")
OUTPUT_DIR.mkdir(exist_ok=True)
pdf_exporter = PDFExporterTool()


def save_report(report: str):
    filename = datetime.now().strftime("research_%Y-%m-%d_%H-%M-%S.md")
    report_path = OUTPUT_DIR / filename
    with open(report_path, "w", encoding="utf-8") as file:
        file.write(report)
    logger.info(f"Report saved to {report_path}")
    return report_path


# ── Output formatting ──────────────────────────────────────────────────────────


def format_research_output(response):
    if response is None:
        return ""

    text = ""

    if hasattr(response, "raw") and getattr(response, "raw"):
        text = str(response.raw)
    elif isinstance(response, dict):
        if "raw" in response:
            text = str(response["raw"])
        elif "result" in response:
            text = str(response["result"])
        elif "output" in response:
            text = str(response["output"])
        else:
            text = json.dumps(response, indent=2)
    elif isinstance(response, str):
        trimmed = response.strip()
        if (trimmed.startswith("{") and trimmed.endswith("}")) or (
                trimmed.startswith("[") and trimmed.endswith("]")
        ):
            try:
                parsed = json.loads(trimmed)
                if isinstance(parsed, dict):
                    text = str(
                        parsed.get("raw", parsed.get("result", parsed.get("output", json.dumps(parsed, indent=2)))))
                else:
                    text = str(parsed)
            except Exception:
                text = response
        else:
            text = response
    else:
        text = str(response)

    if isinstance(text, str) and "\\n" in text:
        text = text.replace("\\n", "\n")

    if isinstance(text, str) and text.startswith('"') and text.endswith('"') and len(text) > 1:
        try:
            text = json.loads(text)
        except Exception:
            pass

    return text.strip() if isinstance(text, str) else str(text)


# ── Session state ──────────────────────────────────────────────────────────────


def initialize_session_state():
    st.session_state.setdefault("research_history", [])
    st.session_state.setdefault("selected_history_index", None)
    st.session_state.setdefault("current_output", None)
    st.session_state.setdefault("current_topic", "")
    st.session_state.setdefault("research_completed", False)
    st.session_state.setdefault("research_error", None)
    st.session_state.setdefault("running", False)
    st.session_state.setdefault("session_uuid", None)


# ── Sidebar ────────────────────────────────────────────────────────────────────


def display_history_sidebar():
    st.sidebar.markdown("## 📚 Research History")
    history = st.session_state.research_history

    if not history:
        st.sidebar.info("No research sessions yet.")
    else:
        for idx, session in enumerate(history):
            topic = session.get("topic", "Unknown")
            timestamp = session.get("timestamp", "")
            duration = session.get("duration", 0)
            is_selected = st.session_state.selected_history_index == idx

            button_label = f"{'🟢' if is_selected else '🌍'} {topic}"
            if st.sidebar.button(button_label, key=f"history_{idx}", use_container_width=True):
                st.session_state.selected_history_index = idx
                st.rerun()

            st.sidebar.caption(f"{timestamp}  ·  {duration:.1f}s")

    st.sidebar.markdown("---")
    display_activity_logs()


def display_activity_logs():
    st.sidebar.markdown("## 🕒 Activity Timeline")
    history = st.session_state.research_history
    idx = st.session_state.selected_history_index

    if idx is None or idx >= len(history):
        st.sidebar.info("Select a research session to view its activity log.")
        return

    session = history[idx]
    logs = session.get("logs", [])

    if not logs:
        st.sidebar.info("No activity logs for this session.")
        return

    for entry in logs:
        elapsed = entry.get("elapsed", 0)
        message = entry.get("message", "")
        level = entry.get("level", "INFO")
        entry_type = entry.get("type", "log")

        if level == "ERROR":
            icon = "❌"
        elif entry_type == "stdout":
            icon = "🔵"
        elif "started" in message.lower() or "start" in message.lower():
            icon = "🟢"
        elif "completed" in message.lower() or "success" in message.lower():
            icon = "✅"
        elif "working" in message.lower() or "agent" in message.lower():
            icon = "🔍"
        elif "report" in message.lower() or "saved" in message.lower():
            icon = "📊"
        elif "final" in message.lower() or "output" in message.lower():
            icon = "✨"
        else:
            icon = "📝"

        st.sidebar.markdown(f"{icon} **{elapsed:05.2f}s** — {message}")


# ── Main area ──────────────────────────────────────────────────────────────────


def display_chat_output():
    idx = st.session_state.selected_history_index
    history = st.session_state.research_history

    if idx is not None and idx < len(history):
        session = history[idx]
        topic = session.get("topic", "")
        output = session.get("output", "")
        timestamp = session.get("timestamp", "")
        duration = session.get("duration", 0)

        st.markdown("### 🤖 AI Research Assistant")
        st.markdown("---")

        with st.chat_message("user"):
            st.markdown(topic)

        with st.chat_message("assistant"):
            st.markdown(f"**{topic}**")
            st.caption(f"📅 {timestamp}  ·  ⏱ {duration:.1f}s")
            st.markdown(output)

        if output:
            st.download_button(
                "📥 Download Report",
                data=output,
                file_name=f"research_{topic[:40].replace(' ', '_')}.md",
                mime="text/markdown",
            )
            pdf_path = session.get("pdf_path")

            if pdf_path and Path(pdf_path).exists():
                with open(pdf_path, "rb") as f:
                    st.download_button(
                        "📄 Download PDF",
                        data=f,
                        file_name=Path(pdf_path).name,
                        mime="application/pdf",
                    )

    elif st.session_state.get("research_error"):
        st.error(f"❌ Research failed\n\n{st.session_state.research_error}")
    else:
        st.markdown("### 🤖 AI Research Assistant")
        st.info("Enter a research topic above to begin.")


# ── Research execution ─────────────────────────────────────────────────────────


def run_research_target(topic, run_id, pdf_context=""):
    logs_list = []
    start_time = time.time()
    setup_logging_for_thread(logs_list, start_time)
    THREAD_RESULTS[run_id] = {"status": "running", "logs": logs_list, "start_time": start_time}

    logger.info("Research started")
    logger.info(f"Topic: {topic}")

    full_topic = topic
    if pdf_context:  # ADD
        full_topic += f"\n\nReference material from an uploaded PDF:\n{pdf_context}"

    result = None
    try:
        logger.info("CrewAI workflow started")
        result = research_crew.kickoff(inputs={"topic": full_topic})
        logger.info("Research agents working")
    except Exception as exc:
        tb = traceback.format_exc()
        logger.error(f"CrewAI execution failed: {exc}")
        logger.error(tb)
        elapsed = time.time() - start_time
        THREAD_RESULTS[run_id].update({
            "status": "error",
            "error": str(exc),
            "traceback": tb,
            "logs": logs_list,
            "duration": elapsed,
        })
        return

    formatted_result = ""
    try:
        formatted_result = format_research_output(result)
        logger.info("Final output generated")
    except Exception as exc:
        tb = traceback.format_exc()
        logger.error(f"Output formatting failed: {exc}")
        logger.error(tb)
        formatted_result = str(result) if result is not None else ""

    markdown_path = None
    pdf_path = None

    try:
        markdown_path = save_report(formatted_result)

        pdf_path = None

        try:
            logger.info("Generating PDF report...")

            pdf_filename = datetime.now().strftime("research_%Y-%m-%d_%H-%M-%S.pdf")
            pdf_file_path = OUTPUT_DIR / pdf_filename

            pdf_path = pdf_exporter._run(
                content=formatted_result,
                file_path=str(pdf_file_path),
                title=topic,
            )

            if pdf_path.startswith("Error"):
                logger.error(pdf_path)
                pdf_path = None
            else:
                logger.info(f"PDF saved at {pdf_path}")

        except Exception as e:
            logger.error(f"PDF generation failed: {e}")
            pdf_path = None
    except Exception as exc:
        tb = traceback.format_exc()
        logger.error(f"Report save failed: {exc}")
        logger.error(tb)

    elapsed = time.time() - start_time
    logger.info("Research completed successfully")
    THREAD_RESULTS[run_id].update({
        "status": "success",
        "result": formatted_result,
        "report_path": str(markdown_path) if markdown_path else None,
        "pdf_path": str(pdf_path) if pdf_path else None,
        "logs": logs_list,
        "duration": elapsed,
    })


# ── Page ───────────────────────────────────────────────────────────────────────


def main_page():
    initialize_session_state()

    st.markdown("### 🤖 AI Research Assistant")

    with st.form("research_form"):
        topic = st.text_input(
            "Enter research topic:",
            placeholder="e.g. Impact of Quantum Computing on Modern Cryptography (2026)",
        )
        uploaded_pdf = st.file_uploader("Attach a PDF (optional)", type=["pdf"])
        submitted = st.form_submit_button("Start Research")

    if submitted and topic.strip():
        pdf_context = ""
        if uploaded_pdf is not None:
            pdf_path = OUTPUT_DIR / f"{uuid.uuid4()}_{uploaded_pdf.name}"
            pdf_path.write_bytes(uploaded_pdf.read())
            extracted = extract_pdf_text(str(pdf_path))
            if not extracted.startswith("Error:"):
                MAX_CHARS = 4000  # cap to control token cost
                pdf_context = extracted[:MAX_CHARS]
            else:
                st.warning(extracted)

        run_id = str(uuid.uuid4())
        st.session_state.session_uuid = run_id
        st.session_state.current_topic = topic.strip()
        st.session_state.running = True
        st.session_state.research_error = None
        st.session_state.research_completed = False
        threading.Thread(target=run_research_target, args=(topic.strip(), run_id, pdf_context), daemon=True).start()
        st.rerun()

    if st.session_state.running:
        run_id = st.session_state.get("session_uuid")
        res = THREAD_RESULTS.get(run_id)
        if res is None or res.get("status") == "running":
            st.info(f"⏳ Research in progress for: **{st.session_state.current_topic}**")
            time.sleep(0.8)
            st.rerun()
        else:
            st.session_state.running = False
            if res.get("status") == "success":
                duration = res.get("duration", 0)
                result_text = res.get("result", "")
                session = {
                    "id": str(uuid.uuid4()),
                    "topic": st.session_state.current_topic,
                    "output": result_text,
                    "timestamp": datetime.now().strftime("%b %d, %Y · %I:%M %p"),
                    "duration": duration,
                    "logs": res.get("logs", []),
                    "pdf_path": res.get("pdf_path"),
                }
                st.session_state.research_history.append(session)
                st.session_state.selected_history_index = len(st.session_state.research_history) - 1
                st.session_state.current_output = result_text
                st.session_state.research_completed = True
                st.rerun()
            else:
                error_msg = res.get("error", "Unknown error")
                st.session_state.research_error = error_msg
                duration = res.get("duration", 0)
                session = {
                    "id": str(uuid.uuid4()),
                    "topic": st.session_state.current_topic,
                    "output": f"❌ Research failed: {error_msg}",
                    "timestamp": datetime.now().strftime("%b %d, %Y · %I:%M %p"),
                    "duration": duration,
                    "logs": res.get("logs", []),
                }
                st.session_state.research_history.append(session)
                st.session_state.selected_history_index = len(st.session_state.research_history) - 1

    display_chat_output()


if __name__ == "__main__":
    initialize_session_state()
    display_history_sidebar()
    main_page()