import os

from crewai import Agent, LLM

analysis_llm = LLM(
    model=os.getenv("ANALYST_AGENT_LLM"),
    api_key=os.getenv("GROQ_API_KEY"),
    temperature = float(os.getenv("ANALYST_AGENT_TEMPERATURE")),
    max_tokens=700
)

analyst_agent = Agent(
    role= "Research Analyst",

    goal=(
        "Interpret the research rather than summarizing it. "
        "Identify patterns, contradictions, trends, risks, opportunities, "
        "and practical insights. "
        "Connect related ideas into a coherent explanation."
        "Do not repeat information already stated unless it is essential."
        "Avoid generic introductions and conclusions."
        "Focus on unique, high-value information."
    ),

    backstory=(
        "You specialize in extracting insights from raw research. "
        "You explain why findings matter instead of merely repeating them."
    ),

    llm=analysis_llm,
    
    verbose=True
)
