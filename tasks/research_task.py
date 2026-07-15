from crewai import Task

from agents.research_agent import research_agent

research_task = Task(
    description=(
        """
        Conduct comprehensive research on the topic: {topic}.

        Your research should include:

        - A clear overview of the topic
        - Key concepts and terminology
        - Recent developments and trends
        - Important statistics (if available)
        - Benefits and applications
        - Challenges and limitations
        - Future outlook

        Use reliable online sources and provide factual information.
        Search the web. Prefer three comprehensive search instead of many narrow searches.
        """
    ),

    expected_output=(
        """
        A well-structured research document in Markdown format containing:

        - Topic Overview
        - Key Concepts
        - Recent Developments
        - Statistics
        - Applications
        - Challenges
        - Future Outlook
        - References
        """
    ),

    agent=research_agent
)