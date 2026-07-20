import os

from crewai import Agent, LLM
from crewai_tools import SerperDevTool

qa_llm = LLM(
    model=os.getenv("QA_AGENT_LLM"),
    api_key=os.getenv("GROQ_API_KEY"),
    temperature = float(os.getenv("QA_AGENT_TEMPERATURE")),
    max_tokens=350
)

qa_agent = Agent(
    role="Quality Assurance Reviewer",

    goal=(
        "Improve the final report by correcting factual mistakes, removing "
        "repetition, improving readability, strengthening transitions, and "
        "ensuring every section directly answers the user's request."
        "Do not repeat information already stated unless it is essential."
        "Avoid generic introductions and conclusions."
        "Focus on unique, high-value information."

    ),

    backstory=(
        "You are a meticulous editor. You never rewrite everything unnecessarily. "
        "You remove redundancy, fix grammar, verify logical flow, and improve "
        "clarity while preserving technical accuracy." 
    ),

    llm=qa_llm,

    verbose=True
)