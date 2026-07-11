from crewai import Task

from agents.qa_agent import qa_agent
from tasks.writing_task import writing_task

review_task = Task(
    description=(
        """
        Review the research report.

        Ensure that:

        - Grammar is correct.
        - Markdown formatting is clean.
        - Information flows logically.
        - No sections are repeated.
        - No important sections are missing.
        - The writing is professional.
        - The report is easy to understand.

        Improve the report wherever necessary.
        """
    ),

    expected_output=(
        """
        A final polished Markdown research report ready for delivery.
        """
    ),

    agent=qa_agent,

    context=[writing_task]
)