from crewai import Task

from agents.qa_agent import qa_agent
from tasks.writing_task import writing_task

review_task = Task(
    description=(
        """
        You may call the search tool ONLY ONCE.
        Create a single comprehensive search query that covers all required aspects.
        Do not perform multiple searches.
        Review the drafted response for accuracy, completeness, clarity, structure, and overall quality before it is presented to the user.

        Your responsibilities are:

        - Verify that every part of the user's query has been fully answered.
        - Check all facts, statistics, dates, names, and technical information for consistency with the research and analysis provided by previous agents.
        - Remove unsupported claims, speculation, hallucinations, contradictions, and misleading information.
        - Correct grammatical, spelling, punctuation, formatting, and readability issues.
        - Eliminate repetitive or redundant content while preserving important information.
        - Ensure the response follows a logical flow, with the most important information appearing first.
        - Verify that headings, bullet points, tables, and formatting improve readability and are used appropriately.
        - Ensure the response length is appropriate for the user's request:
            - Keep answers concise by default.
            - Expand only when the user explicitly requests detailed explanations or when the topic requires it.
            - Do not add unnecessary filler or generic introductions/conclusions.
        - Ensure the tone is professional, natural, engaging, and easy to understand.
        - Verify that examples, comparisons, and statistics are relevant and correctly placed.
        - If the user requested recommendations, planning, troubleshooting, or asked what they should do, ensure the response contains a dedicated **'What You Should Do'** section with practical, prioritized, step-by-step guidance.
        - Ensure the response ends with concise key takeaways whenever appropriate.
        - Preserve all valuable information while improving quality. Do not remove useful content simply to shorten the response.
        - Produce only the final polished version without review notes, comments, explanations, or revision history.
        """
    ),

    expected_output=(
        """
        A final publication-ready response that is:

        - Factually accurate and free from unsupported claims.
        - Complete, directly answering every aspect of the user's request.
        - Appropriately sized according to the user's requested level of detail.
        - Well-structured with clear headings and logical organization.
        - Easy to read using concise paragraphs, bullet points, numbered lists, or tables where beneficial.
        - Free of grammar, spelling, punctuation, formatting, and consistency errors.
        - Free from repetition, unnecessary filler, and irrelevant information.
        - Optimized for readability, allowing readers to quickly identify the most important information.
        - Written in a natural, professional, and engaging tone.
        - Includes a **'What You Should Do'** section whenever the user asks for recommendations, planning, troubleshooting, or actionable guidance.
        - Includes concise **Key Takeaways** when appropriate.
        - Suitable for direct presentation to the user without requiring any additional editing.
        """
    ),
    
    agent=qa_agent,

    context=[writing_task]
)