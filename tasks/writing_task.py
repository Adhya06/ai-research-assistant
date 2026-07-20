from crewai import Task

from agents.writer_agent import writer_agent
from tasks.analysis_task import analysis_task

writing_task = Task(
    description=(
        """
        Use ONLY the insights provided.

        Do not restate every research finding.

        Expand only where necessary.

        Answer the user's question directly.

        Maximum 800 words unless the user explicitly requests more.
        """
    ),

    expected_output=(
        """

        Write the best response for THIS question.

        Choose the format yourself.

        Examples

        Simple question
        → short paragraph

        Comparison
        → table

        Research
        → report

        Tutorial
        → step-by-step guide

        Opinion
        → balanced discussion

        Do not force headings unless they improve readability.

        Sound natural.        """
    ),

    agent=writer_agent,

    context=[analysis_task]
)