from crewai import Crew, Process
from langchain_groq import ChatGroq
from crewai_tools import WebsiteSearchTool
from pydantic import SecretStr
import os
from job_manager import append_event
from financial_analyst_crew.agents import FinancialAgents
from financial_analyst_crew.tasks import FinancialTasks

class FinancialAnalystCrew:
    def __init__(self, job_id: str):
        self.job_id = job_id
        self.crew = None
        self.llm = self._setup_llm()
        self.website_search_tool = self._setup_search_tool()
        
    def _setup_llm(self):
        api_key = os.getenv("GROQ_API_KEY")
        if api_key is not None:
            api_key = SecretStr(api_key)
        
        return ChatGroq(
            temperature=0,
            stop_sequences=["\n", "END", "<END>", "STOP"],
            api_key=api_key
        )
    
    def _setup_search_tool(self):
        return WebsiteSearchTool(
            config={
                "request_timeout": 30,
                "max_retries": 3,
                "user_agent": "Mozilla/5.0",
                "ssl_verify": True
            }
        )

    def setup_crew(self):
        agents = FinancialAgents(self.llm, self.website_search_tool)
        tasks = FinancialTasks(agents)
    
        self.crew = Crew(
        agents=[
            agents.researcher(), 
            agents.accountant(),  
            agents.recommender(),  
            agents.blogger()      
        ],
        tasks=[
            tasks.analyze_stock(),    
            tasks.research_stock(),   
            tasks.make_decision(),    
            tasks.output_report()    
        ],
        process=Process.sequential,
        verbose=True
    )

    def kickoff(self):
        if not self.crew:
            append_event(self.job_id, "CREW NOT SET UP")
            return "CREW NOT SET UP"

        append_event(self.job_id, "CREW STARTED")

        try:
            print(f"RUNNING CREW {self.job_id}")
            results = self.crew.kickoff()
            append_event(self.job_id, "CREW COMPLETED")
            return results

        except Exception as e:
            append_event(self.job_id, f"CREW ERROR {e}")
            return str(e)