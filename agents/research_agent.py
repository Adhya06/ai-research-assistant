import os

from crewai import Agent, LLM
from crewai_tools import SerperDevTool


research_llm = LLM(
    model=os.getenv("RESEARCH_AGENT_LLM"),
    api_key=os.getenv("GROQ_API_KEY"),
    temperature = float(os.getenv("RESEARCH_AGENT_TEMPERATURE")),
    max_tokens=1000
)

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
    tools=[SerperDevTool()],
    max_iter=3,

    llm=research_llm,

    verbose=True
)
