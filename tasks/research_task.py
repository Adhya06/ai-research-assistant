from crewai import Task

from agents.research_agent import research_agent

research_task = Task(
    description=(
        """
        Research the topic: {{topic}}

        Understand the user's actual intent.

        Gather only the information necessary to answer the question.

        Prioritize:
        - authoritative sources
        - recent information
        - concrete evidence
        - useful statistics

        Skip sections that are not relevant.

        If the question is simple,
        return concise research.

        If the question is broad,
        return comprehensive research.

        Do not organize into a fixed template.
        """
    ),

    expected_output=(
        """
       Return ONLY this Markdown:

        ## Research Notes

        ### Key Facts
        - Maximum 8 bullet points

        ### Statistics
        - Maximum 5 bullet points

        ### Recent Developments
        - Maximum 5 bullet points

        ### Challenges
        - Maximum 3 bullet points

        ### Sources
        - Maximum 5 sources

        Maximum 450 words.

        """
    ),

    agent=research_agent
)