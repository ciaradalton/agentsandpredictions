import os
import traceback
import yaml
from crewai import Crew, Process
from langchain_groq import ChatGroq
from langchain_ollama import OllamaLLM
from langchain_openai import ChatOpenAI
from agents import FinancialAgents
from tasks import FinancialTasks
from utils import get_config_path
from time import sleep
from litellm import RateLimitError

class FinancialAnalystCrew:
    def __init__(self, job_id: str, asset_name: str, primary_llm: str = 'groq', backup_llm: str = 'gpt'):
        os.environ["USER_AGENT"] = "FinancialAnalystCrew/1.0"

        self.job_id = job_id
        self.asset_name = asset_name
        self.primary_llm = primary_llm.lower()
        self.backup_llm = backup_llm.lower()
        self.current_llm = self.primary_llm
        self.crew = None
        self.llm_provider = None
        
        # Load configurations
        with open(get_config_path('agents.yaml'), 'r') as f:
            self.agents_config = yaml.safe_load(f)
        
        with open(get_config_path('tasks.yaml'), 'r') as f:
            self.tasks_config = yaml.safe_load(f)
            
        self.setup_crew()

    def _setup_llm_provider(self):
        """Initialize the LLM provider based on current choice."""
        try:
            groq_key = os.getenv('GROQ_API_KEY')
            openai_key = os.getenv('OPENAI_API_KEY')
            
            print(f"Using {self.current_llm} provider")  # Debug line
            
            if self.current_llm == 'groq':
                if not groq_key:
                    print("GROQ API key not found")
                    return None
                return ChatGroq(
                    model_name="groq/llama3-8b-8192",
                    groq_api_key=groq_key
                )
            elif self.current_llm == 'gpt':
                if not openai_key:
                    print("OpenAI API key not found")
                    return None
                return ChatOpenAI(
                    model="gpt-3.5-turbo",
                    temperature=0.0,
                    openai_api_key=openai_key
                )
            else:
                raise ValueError(f"Invalid LLM choice: {self.current_llm}")
        except Exception as e:
            print(f"Error in _setup_llm_provider: {str(e)}")
            return None

    def switch_llm(self):
        """Switch between primary and backup LLM providers."""
        print(f"Switching from {self.current_llm} to {self.backup_llm}")
        self.current_llm = self.backup_llm if self.current_llm == self.primary_llm else self.primary_llm
        self.llm_provider = self._setup_llm_provider()
        self.setup_crew()

    def setup_crew(self):
        """Set up the crew with initialized LLM provider."""
        try:
            self.llm_provider = self._setup_llm_provider()
            agents = FinancialAgents(self.llm_provider)
            tasks = FinancialTasks(agents, self.asset_name)

            self.crew = Crew(
                agents=[
                    agents.researcher(),
                    agents.accountant(),
                    agents.recommender(),
                    agents.blogger()
                ],
                tasks=[
                    tasks.research_stock(),
                    tasks.analyze_stock(),
                    tasks.make_decision(),
                    tasks.output_report()
                ],
                process=Process.sequential,
                verbose=True
            )
        except Exception as e:
            print(f"Error setting up {self.current_llm}: {str(e)}")
            self.switch_llm()

    def kickoff(self):
        """Kick off the crew process with fallback and retry logic."""
        if not self.crew:
            return {"status": "error", "message": "CREW NOT SET UP"}

        max_retries = 3
        base_delay = 2

        for attempt in range(max_retries):
            try:
                print(f"RUNNING CREW {self.job_id} with {self.current_llm.upper()} LLM")
                results = self.crew.kickoff()
                structured_output = self.restructure_analysis_result(results)
                return structured_output

            except RateLimitError as e:
                print(f"Rate limit hit on {self.current_llm}")
                if attempt < max_retries - 1:
                    self.switch_llm()
                else:
                    delay = base_delay * (2 ** attempt)
                    print(f"All providers rate limited. Waiting {delay} seconds...")
                    sleep(delay)
            except Exception as e:
                print(traceback.format_exc())
                return {"status": "error", "message": str(e)}

        return {"status": "error", "message": "Max retries exceeded on all providers"}

    def restructure_analysis_result(self, results):
        """Reorganize the results from the crew tasks into a structured format."""
        try:
            # Initialize Firebase client (assuming you have it set up in database.py)
            from database import Database
            db = Database()
            
            # Structure the data according to your Firebase schema
            analysis_data = {
                "agent_processing": {
                    "researcher_complete": True,
                    "accountant_complete": True,
                    "recommender_complete": True,
                    "blogger_complete": True
                },
                "asset_name": self.asset_name,
                "final_report": {
                    "disclaimers": [
                        "This analysis is for informational purposes only",
                        "Past performance does not guarantee future results"
                    ],
                    "executive_summary": results.get("executive_summary", ""),
                    "sections": {
                        "overview": results.get("overview", ""),
                        "financial_analysis": results.get("financial_summary", ""),
                        "recommendations": results.get("recommendation", {}).get("rationale", ""),
                        "research_findings": results.get("research_summary", "")
                    }
                },
                "metadata": {
                    "analysis_type": "full_analysis",
                    "llm_used": self.current_llm,
                    "tools_used": ["YahooFinance", "WebSearch"]
                }
            }

            # Store in Firebase and get the document ID
            doc_id = db.store_analysis_report(self.asset_name, analysis_data)
            
            return {
                "status": "success",
                "report_id": doc_id,
                "data": analysis_data
            }

        except Exception as e:
            print(f"Error storing analysis in Firebase: {str(e)}")
            return {
                "status": "error",
                "message": "Failed to store analysis in Firebase"
            }
