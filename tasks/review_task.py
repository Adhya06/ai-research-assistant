from crewai import Task

from agents.qa_agent import qa_agent
from tasks.writing_task import writing_task

review_task = Task(
    description=(
        """
        If the report is already good:

        Return it unchanged.

        Only edit when necessary.

        Never paraphrase for style alone.

        Never change structure unless required.

        Never add new information.        """
    ),

    expected_output=(
        """
        Return the corrected final response.

        It should be:

        - accurate
        - concise
        - well formatted
        - free of repetition
        - grammatically correct
        """
    ),
    
    agent=qa_agent,

    context=[writing_task]
)