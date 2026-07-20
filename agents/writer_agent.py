import os

from crewai import Agent, LLM

writer_llm = LLM(
    model=os.getenv("WRITER_AGENT_LLM"),
    api_key=os.getenv("GROQ_API_KEY"),
    temperature = float(os.getenv("WRITER_AGENT_TEMPERATURE")),
    max_tokens=900
)

writer_agent = Agent(
    role="Technical Report Writer",

    goal=(
        "Choose the most appropriate response format for the user's request. "
        "Use paragraphs for direct questions, bullet points for comparisons, "
        "tables when comparing multiple items, and detailed reports only for "
        "research tasks."
        "Do not repeat information already stated unless it is essential."
        "Avoid generic introductions and conclusions."
        "Focus on unique, high-value information."

    ),

    backstory=(
       "Create professional, readable responses."
    ),

    llm=writer_llm,

    verbose=True
)