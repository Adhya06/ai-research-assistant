from crewai import Task

from agents.analyst_agent import analyst_agent
from tasks.research_task import research_task

analysis_task = Task(
    description=(
        """
        Analyze the research.

        Your job is NOT to summarize.

        Instead:

        • Explain WHY the evidence matters.

        • Rank the most important findings.

        • Identify relationships.

        • Identify contradictions.

        • Explain root causes.

        • Remove weak or redundant information.

        If there is nothing meaningful to analyze,
        state that directly.        """
    ),

    expected_output=(
        """
        Return ONLY:

        ## Insights

        - Top 5 findings

        ## Trends

        - Top 3 trends

        ## Risks

        - Top 3 risks

        ## Opportunities

        - Top 3 opportunities

        Maximum 250 words.
        """
    ),

    agent=analyst_agent,

    context=[research_task]
)