import re
from pathlib import Path
from typing import Type
from xml.sax.saxutils import escape

from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    ListFlowable,
    ListItem,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
)


class PDFExporterInput(BaseModel):
    content: str = Field(
        ...,
        description="""
        Export the provided text into a PDF.
        Pass only one argument:

        content: complete report text.
        """
    )
    file_path: str = Field(
        ...,
        description="Path (including filename.pdf) where the PDF should be saved."
    )
    title: str = Field(
        default="",
        description="Optional title placed at the top of the PDF."
    )


def _inline_markdown_to_reportlab(text: str) -> str:
    """
    Escape XML-special characters first (so stray '<', '>', '&' in the
    source text can never be mistaken for markup / break the parser),
    then convert a small set of inline Markdown patterns into ReportLab's
    paragraph markup.
    """
    text = escape(text)

    # bold: **text** or __text__
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"__(.+?)__", r"<b>\1</b>", text)

    # italic: *text* or _text_ (run after bold so ** isn't eaten by *)
    text = re.sub(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)", r"<i>\1</i>", text)
    text = re.sub(r"(?<!_)_(?!_)(.+?)(?<!_)_(?!_)", r"<i>\1</i>", text)

    # inline code: `code`
    text = re.sub(r"`(.+?)`", r'<font face="Courier">\1</font>', text)

    return text


def _build_styles():
    styles = getSampleStyleSheet()

    styles.add(ParagraphStyle(
        name="H1Custom", parent=styles["Heading1"],
        spaceBefore=16, spaceAfter=8,
    ))
    styles.add(ParagraphStyle(
        name="H2Custom", parent=styles["Heading2"],
        spaceBefore=13, spaceAfter=7,
    ))
    styles.add(ParagraphStyle(
        name="H3Custom", parent=styles["Heading3"],
        spaceBefore=11, spaceAfter=6,
    ))
    styles.add(ParagraphStyle(
        name="BodyCustom", parent=styles["BodyText"],
        spaceAfter=8, leading=15,
    ))
    styles.add(ParagraphStyle(
        name="BulletCustom", parent=styles["BodyText"],
        leftIndent=14, spaceAfter=4, leading=14,
    ))
    styles.add(ParagraphStyle(
        name="NumberedCustom", parent=styles["BodyText"],
        leftIndent=14, spaceAfter=4, leading=14,
    ))

    return styles


_HEADING_RE = re.compile(r"^(#{1,3})\s+(.*)")
_BULLET_RE = re.compile(r"^[-*]\s+(.*)")
_NUMBERED_RE = re.compile(r"^\d+[.)]\s+(.*)")


class PDFExporterTool(BaseTool):
    name: str = "PDF Exporter"

    description: str = (
        "Exports a Markdown research report into a formatted PDF file, "
        "converting headings, bold/italic text, and bullet/numbered lists "
        "into proper PDF formatting rather than dumping raw Markdown."
    )

    args_schema: Type[BaseModel] = PDFExporterInput

    def _run(self, content: str, file_path: str, title: str = "") -> str:
        try:
            Path(file_path).parent.mkdir(parents=True, exist_ok=True)

            styles = _build_styles()

            doc = SimpleDocTemplate(
                file_path,
                pagesize=letter,
                title=title or "Research Report",
                author="AI Research Assistant",
            )

            story = []

            if title:
                story.append(Paragraph(escape(title), styles["Title"]))
                story.append(Spacer(1, 16))

            story.extend(self._markdown_to_flowables(content, styles))

            if not story:
                story.append(Paragraph("(No content)", styles["BodyCustom"]))

            doc.build(story)
            return str(file_path)

        except Exception as e:
            return f"Error exporting PDF: {e}"

    def _markdown_to_flowables(self, content: str, styles) -> list:
        story = []
        bullet_buffer: list[str] = []
        paragraph_buffer: list[str] = []

        def flush_paragraph():
            if paragraph_buffer:
                text = " ".join(paragraph_buffer).strip()
                if text:
                    story.append(
                        Paragraph(_inline_markdown_to_reportlab(text), styles["BodyCustom"])
                    )
                paragraph_buffer.clear()

        def flush_bullets():
            if bullet_buffer:
                items = [
                    ListItem(
                        Paragraph(_inline_markdown_to_reportlab(item), styles["BulletCustom"]),
                        leftIndent=14,
                    )
                    for item in bullet_buffer
                ]
                story.append(
                    ListFlowable(items, bulletType="bullet", start="•")
                )
                story.append(Spacer(1, 8))
                bullet_buffer.clear()

        lines = content.replace("\r\n", "\n").split("\n")

        for raw_line in lines:
            line = raw_line.strip()

            if not line:
                flush_paragraph()
                flush_bullets()
                continue

            heading_match = _HEADING_RE.match(line)
            bullet_match = _BULLET_RE.match(line)
            numbered_match = _NUMBERED_RE.match(line)

            if heading_match:
                flush_paragraph()
                flush_bullets()
                level = len(heading_match.group(1))
                style_name = {1: "H1Custom", 2: "H2Custom", 3: "H3Custom"}[level]
                story.append(
                    Paragraph(_inline_markdown_to_reportlab(heading_match.group(2)), styles[style_name])
                )

            elif bullet_match:
                flush_paragraph()
                bullet_buffer.append(bullet_match.group(1))

            elif numbered_match:
                # Numbered items are rendered as their own indented paragraphs
                # (keeping the original "1. " text) rather than mixed into the
                # bullet ListFlowable, so numbering isn't lost or double-marked.
                flush_paragraph()
                flush_bullets()
                story.append(
                    Paragraph(_inline_markdown_to_reportlab(line), styles["NumberedCustom"])
                )

            else:
                flush_bullets()
                paragraph_buffer.append(line)

        flush_paragraph()
        flush_bullets()

        return story
