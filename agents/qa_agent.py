import os

from crewai import Agent

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

    llm=os.getenv("QA_AGENT_LLM"),

    verbose=True
)