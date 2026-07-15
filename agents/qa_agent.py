import os

from crewai import Agent, LLM
from crewai_tools import SerperDevTool

qa_llm = LLM(
    model=os.getenv("QA_AGENT_LLM"),
    api_key=os.getenv("GROQ_API_KEY"),
    temperature = float(os.getenv("QA_AGENT_TEMPERATURE")),
    max_tokens=600
)

qa_agent = Agent(
    role="Quality Assurance Reviewer",

    goal=(
        "Review the final report for clarity, accuracy, grammar, "
        "formatting, and completeness before delivering it."
    ),

    backstory=(
        "You are a senior editor responsible for reviewing technical "
        "documents. You ensure reports are accurate, well-formatted, "
        "free of repetition, and easy to read."
    ),

    llm=qa_llm,

    verbose=True
)