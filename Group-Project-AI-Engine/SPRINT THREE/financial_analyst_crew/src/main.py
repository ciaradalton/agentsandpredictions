import os
import sys 
print(sys.path)
from dotenv import load_dotenv
load_dotenv()

from crew import FinancialAnalystCrew

def run():
    try:
        
        crew = FinancialAnalystCrew(
            job_id="test_run",
            asset_name = "NVDA",
            llm_choice="groq"  
        )
        
       
        crew.setup_crew()
        
       
        result = crew.kickoff()
        
        print(result)
    except Exception as e:
        print(f"Error occurred: {str(e)}")

if __name__ == "__main__":
    run()
