import os 
from dotenv import load_dotenv 
load_dotenv()

from financial_analyst_crew.crew import FinancialAnalystCrew  # Adjust this based on what you're importing


def run():
    inputs = {
        'asset_name': 'Bitcoin'
    }

    FinancialAnalystCrew().crew().kickoff(inputs = inputs)

if __name__ == "__main__":
    run()

