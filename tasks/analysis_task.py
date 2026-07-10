from crewai import Task

from agents.analyst_agent import analyst_agent
from tasks.research_task import research_task

analysis_task = Task(
    description=(
        """
        Analyze the research findings provided by the Research Specialist.

        Your analysis should:

        - Organize the information logically
        - Identify key trends and patterns
        - Highlight the most important insights
        - Remove repetitive information
        - Explain the significance of the findings
        - Identify any challenges or limitations

        Do not introduce new information.
        Base your analysis only on the research findings.
        """
    ),

    expected_output=(
        """
        A structured analysis in Markdown containing:

        - Executive Summary
        - Key Insights
        - Major Trends
        - Challenges
        - Future Opportunities
        """
    ),

    agent=analyst_agent,

    context=[research_task]
)