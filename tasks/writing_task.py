from crewai import Task

from agents.writer_agent import writer_agent
from tasks.analysis_task import analysis_task

writing_task = Task(
    description=(
        """
        Write a comprehensive research report based on the provided analysis.

        The report should contain:

        - Title
        - Executive Summary
        - Introduction
        - Key Findings
        - Trend Analysis
        - Challenges
        - Future Outlook
        - Conclusion

        Use professional language and proper Markdown formatting.
        """
    ),

    expected_output=(
        """
        A polished Markdown research report that is ready for the user.
        """
    ),

    agent=writer_agent,

    context=[analysis_task]
)