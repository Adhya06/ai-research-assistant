import os

from crewai import Agent, LLM

analysis_llm = LLM(
    model=os.getenv("ANALYST_AGENT_LLM"),
    api_key=os.getenv("GROQ_API_KEY"),
    temperature = float(os.getenv("ANALYST_AGENT_TEMPERATURE")),
    max_tokens=600
)

analyst_agent = Agent(
    role="Research Analyst",

    goal=(
        "Analyze research findings, identify important insights, "
        "recognize trends, compare information, and organize the "
        "research into a clear and logical structure."
    ),

    backstory=(
        "You are an experienced research analyst with strong analytical "
        "skills. Your responsibility is to transform raw research into "
        "meaningful insights by identifying patterns, comparing viewpoints, "
        "highlighting significant findings, and eliminating redundant information."
    ),

    llm=analysis_llm,
    
    verbose=True
)
