import os

from crewai import Crew, Process

from agents.research_agent import research_agent
from agents.analyst_agent import analyst_agent
from agents.writer_agent import writer_agent
from agents.qa_agent import qa_agent

from tasks.research_task import research_task
from tasks.analysis_task import analysis_task
from tasks.writing_task import writing_task
from tasks.review_task import review_task

research_crew = Crew(

    agents=[
        research_agent,
        analyst_agent,
        writer_agent,
        qa_agent
    ],
    
    tasks=[
        research_task,
        analysis_task,
        writing_task,
        review_task
    ],
    process=Process.sequential,
    verbose=True
)

