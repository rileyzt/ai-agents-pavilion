#!/usr/bin/env python
import sys
import warnings

from datetime import datetime

from engineering_team.crew import EngineeringTeam

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

requirements = """
Design an AI-powered HR agent that analyzes a batch of resumes to select or reject candidates based on their skill sets, knowledge, and internship experiences. The agent should review each resume, compare qualifications, and make objective decisions about which candidates best fit the job requirements. For every selected candidate, the agent must write a concise 4-line paragraph explaining why this resume was chosen over others, highlighting the key strengths and differentiators. Ensure the process is fair, transparent, and focused on relevant competencies and experiences.
"""

module_name = "accounts.py" 
class_name = "Account"



def run():
    """
    Run the crew.
    """
    inputs = {
        'requirements': requirements,
        'module_name': module_name,
        'class_name': class_name

    }
    
    try:
        EngineeringTeam().crew().kickoff(inputs=inputs)
    except Exception as e:
        raise Exception(f"An error occurred while running the crew: {e}")


