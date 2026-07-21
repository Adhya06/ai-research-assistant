# AI Research Assistant

A multi-agent research tool built with [CrewAI](https://github.com/crewAIInc/crewAI). Give it a topic, and a crew of four LLM agents — researcher, analyst, writer, and QA reviewer — work together sequentially to produce a polished research report, exportable as Markdown and PDF. Comes with both a CLI and a Streamlit web UI.

## How it works

The crew runs as a sequential pipeline (`crew.py`), where each agent's output feeds the next:

1. **Research Agent** (`agents/research_agent.py`) — gathers relevant, reliable, and recent information using web search (Serper) and can pull context from an uploaded PDF.
2. **Analyst Agent** (`agents/analyst_agent.py`) — interprets the raw research, surfacing patterns, contradictions, risks, and opportunities rather than just summarizing.
3. **Writer Agent** (`agents/writer_agent.py`) — drafts a clear, well-formatted report, choosing the right structure (paragraphs, bullets, tables) for the request.
4. **QA Agent** (`agents/qa_agent.py`) — reviews and polishes the final draft for accuracy, clarity, and flow.

Each agent runs on its own configurable Groq-hosted LLM and temperature, set via environment variables.

## Features

- 🔍 Automated multi-agent research pipeline (CrewAI + Groq)
- 📄 Optional PDF upload for additional reference context
- 📝 Reports saved as timestamped Markdown files
- 📑 One-click PDF export (via ReportLab)
- 🖥️ Streamlit UI with research history, live activity timeline, and download buttons
- ⌨️ Simple CLI entry point for scripted/headless use

## Project structure

```
ai-research-assistant/
├── agents/
│   ├── research_agent.py     # Gathers information
│   ├── analyst_agent.py      # Extracts insights
│   ├── writer_agent.py       # Drafts the report
│   └── qa_agent.py           # Reviews and polishes
├── tasks/
│   ├── research_task.py
│   ├── analysis_task.py
│   ├── writing_task.py
│   └── review_task.py
├── tools/
│   ├── pdf_reader.py         # Extracts text from uploaded PDFs
│   └── pdf_exporter.py       # Exports the final report to PDF
├── crew.py                   # Wires agents + tasks into the CrewAI pipeline
├── main.py                   # CLI entry point
├── app.py                    # Streamlit web app
├── logger.py                 # Shared logging setup
├── requirements.txt
└── .env.example
```

## Getting started

### Prerequisites

- Python 3.10+
- A [Groq](https://console.groq.com/) API key
- A [Serper](https://serper.dev/) API key (for web search)

### Installation

```bash
git clone https://github.com/Adhya06/ai-research-assistant.git
cd ai-research-assistant
python -m venv venv
source venv/bin/activate   # on Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Configuration

Copy the example environment file and fill in your keys:

```bash
cp .env.example .env
```

```env
GROQ_API_KEY=your_groq_api_key
SERPER_API_KEY=your_serper_api_key

RESEARCH_AGENT_LLM=groq/llama-3.3-70b-versatile
ANALYST_AGENT_LLM=groq/llama-3.3-70b-versatile
WRITER_AGENT_LLM=groq/llama-3.3-70b-versatile
QA_AGENT_LLM=groq/llama-3.3-70b-versatile

RESEARCH_AGENT_TEMPERATURE=0.1
ANALYST_AGENT_TEMPERATURE=0.2
WRITER_AGENT_TEMPERATURE=0.3
QA_AGENT_TEMPERATURE=0.4
```

Each agent's model and temperature can be tuned independently, so you can, for example, keep the researcher deterministic while giving the writer more creative freedom.

## Usage

### CLI

```bash
python main.py
```

You'll be prompted to enter a research topic. The crew runs, and the report is saved to `outputs/` as both a Markdown file and a PDF.

### Web UI

```bash
streamlit run app.py
```

Opens a browser-based interface where you can:
- Enter a topic (and optionally attach a reference PDF)
- Watch a live activity timeline as the agents work
- Browse past research sessions in the sidebar
- Download the report as Markdown or PDF

## Output

Every run produces a timestamped report in `outputs/`, e.g.:

```
outputs/research_2026-07-21_14-30-00.md
outputs/research_2026-07-21_14-30-00.pdf
```

## Tech stack

- [CrewAI](https://github.com/crewAIInc/crewAI) — multi-agent orchestration
- [Groq](https://groq.com/) — fast LLM inference (Llama 3.3 70B by default)
- [Serper](https://serper.dev/) — Google search API for the research agent
- [Streamlit](https://streamlit.io/) — web interface
- [ReportLab](https://www.reportlab.com/) — PDF generation
- [pypdf](https://pypi.org/project/pypdf/) — PDF text extraction




