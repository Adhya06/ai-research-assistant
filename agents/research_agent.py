import os

from crewai import Agent
from crewai_tools import SerperDevTool

# Search tool used by this agent
search_tool = SerperDevTool()

research_agent = Agent(
    role="Senior Research Specialist",

    goal=(
        "Conduct comprehensive and accurate research on the given topic "
        "using reliable online sources."
    ),

    backstory=(
        "You are an experienced research specialist skilled at gathering "
        "up-to-date information from trusted sources. "
        "Your responsibility is to collect factual information, statistics, "
        "recent developments, and references while avoiding unsupported claims."
    ),

    tools=[search_tool],

    llm=os.getenv("RESEARCH_AGENT_LLM"),

    verbose=True
)
