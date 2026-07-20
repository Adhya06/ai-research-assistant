import os

from crewai import Agent, LLM
from crewai_tools import SerperDevTool
from tools.pdf_reader import read_pdf

research_llm = LLM(
    model=os.getenv("RESEARCH_AGENT_LLM"),
    api_key=os.getenv("GROQ_API_KEY"),
    temperature = float(os.getenv("RESEARCH_AGENT_TEMPERATURE")),
    max_tokens=800
)

research_agent = Agent(
    role="Senior Research Specialist",

    goal=(
        "Collect the most relevant, reliable and recent information. "
        "Prioritize authoritative sources. "
        "Focus only on information needed to answer the user's request. "
        "Avoid collecting duplicate facts." 
        "Do not repeat information already stated unless it is essential."
        "Avoid generic introductions and conclusions."
        "Focus on unique, high-value information."
    ),

    backstory=(
         "You are a professional research analyst who gathers high-quality "
        "information efficiently. You identify key facts, trends, statistics, "
        "and differing viewpoints while filtering out irrelevant details."
    ),
    tools=[SerperDevTool(),read_pdf],
    max_iter=2,

    llm=research_llm,

    verbose=True
)
