from crewai import Task

from agents.writer_agent import writer_agent
from tasks.analysis_task import analysis_task

writing_task = Task(
    description=(
        """
        Transform the analyzed research into a clear, accurate, and well-structured response that directly answers the user's query.

        Writing Guidelines:

        - Always answer the user's actual question first. Do not include unnecessary background information unless it improves understanding.
        - Adapt the response length intelligently based on the user's request:
          - If the user asks a simple or direct question, provide a concise but complete answer.
          - If the user requests a detailed explanation, guide, comparison, tutorial, report, or explicitly asks for more detail, provide a comprehensive response.
          - Let the complexity of the question determine the length rather than always producing long outputs.
        - Ensure every response is complete enough that the user does not need to ask obvious follow-up questions.
        - Use clear headings, bullet points, or numbered lists whenever they improve readability.
        - Avoid repetition, filler text, and generic statements.
        - Present factual information naturally instead of forcing every possible detail into the response.
        - If multiple viewpoints or options exist, briefly compare them and recommend the most suitable one when appropriate.
        - Maintain a professional, natural, and easy-to-read writing style.

        Actionable Guidance:

        - Whenever the user asks:
          - how to do something,
          - what to do,
          - what should I do,
          - how can I,
          - what is the best way,
          - asks for recommendations, planning, troubleshooting, or decision-making,

        include a separate section titled:

         ## What You Should Do

        - This section should contain practical, step-by-step actions the user can follow immediately.
        - Prioritize actionable advice over theory.
        - If there are important precautions, prerequisites, or common mistakes, mention them briefly.

        Quality Requirements:

        - Ensure factual accuracy and consistency with the research provided by previous agents.
        - Remove duplicate information.
        - Do not invent facts or unsupported claims.
        - Write in fluent, natural English.
        - Produce an answer that is informative, readable, and appropriately sized for the user's request rather than aiming for a fixed word count.
        """
    ),

    expected_output=(
        """

        Write the final response as if it is being presented to a curious reader with limited time and an average human attention span.

        Guidelines:
        First of all, never be too detailed or repetitive. And never give long outputs unless specially asked for. Give answers in section and concise paragraphs.

        1. Start with a **Quick Answer** (2–4 sentences) that directly answers the user's question before providing background.

        2. Structure the response using meaningful headings. Present the most important information first and progressively add supporting details.

        3. Adapt the response length intelligently:
            - Short question → concise answer.
            - Complex topic → detailed explanation.
            - Explicit word/page requirements → follow them exactly.
            Never make the response longer than necessary.

        4. Write in a conversational but professional tone. Avoid sounding like an academic report unless the user specifically requests one.

        5. Break up long paragraphs into smaller ones. Use bullet points, numbered lists, tables, or callout boxes whenever they improve readability.

        6. Remove repetitive information. Explain each concept once, then build upon it instead of restating it.

        7. Use concrete facts, statistics, dates, and examples whenever available. Avoid vague phrases like "significant increase" if exact figures are known.

        8. Highlight the most important insights using bold text sparingly so readers can quickly scan the response.

        9. If the user asks for advice, recommendations, troubleshooting, planning, or decision-making, include a dedicated section titled:

        ## What You Should Do

        Provide practical, prioritized, step-by-step actions the user can follow immediately. And also tell about it in different situation but in a concise manner like in 10-15 words.

        10. End with a concise **Key Takeaways** section summarizing the 3–5 most important points. The length of the key points should be concise like around 10-15 words.

        11. Never add filler, generic conclusions, or unnecessary introductions. Every paragraph should provide new value.

        12. Ensure the response is factually accurate, logically organized, engaging to read, and complete enough that the user rarely needs obvious follow-up questions.
        """
    ),

    agent=writer_agent,

    context=[analysis_task]
)