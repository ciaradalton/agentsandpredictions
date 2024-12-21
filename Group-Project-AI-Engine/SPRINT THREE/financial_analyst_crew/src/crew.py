import os
import traceback
from crewai import Crew, Process
from langchain_groq import ChatGroq
from langchain_ollama import OllamaLLM
from langchain_openai import ChatOpenAI
from agents import FinancialAgents
from tasks import FinancialTasks

class FinancialAnalystCrew:
    def __init__(self, job_id: str, asset_name: str, llm_choice: str = 'groq'):
        os.environ["USER_AGENT"] = "FinancialAnalystCrew/1.0"

        self.job_id = job_id
        self.asset_name = asset_name
        self.llm_choice = llm_choice.lower()
        self.crew = None
        self.llm_provider = self._setup_llm_provider()

    def _setup_llm_provider(self):
        """Initialize the LLM provider based on user choice."""
        if self.llm_choice == 'groq':
            return 'groq/llama3-8b-8192'
        elif self.llm_choice == 'gpt':
            return ChatOpenAI(model="gpt-3.5-turbo", temperature=0.0)
        elif self.llm_choice == 'ollama_llama2':
            return OllamaLLM(model="llama2")
        elif self.llm_choice == 'ollama_mistral':
            return OllamaLLM(model="mistral")
        else:
            raise ValueError(f"Invalid LLM choice: {self.llm_choice}")

    def setup_crew(self):
        """Set up the crew with initialized LLM provider."""
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

    def kickoff(self):
        """Kick off the crew process."""
        if not self.crew:
            return {"status": "error", "message": "CREW NOT SET UP"}

        try:
            print(f"RUNNING CREW {self.job_id} with {self.llm_choice.upper()} LLM")
            results = self.crew.kickoff()

           
            structured_output = self.restructure_analysis_result(results)

            return structured_output

        except Exception as e:
            print(traceback.format_exc())
            return {"status": "error", "message": str(e)}

    def restructure_analysis_result(self, results):
        """Reorganize the results from the crew tasks into a structured format."""
        structured_output = {
            "status": "success",
            "data": {}
        }

       
        print("Raw Results from Crew:", results)

       
        if isinstance(results, dict) and results.get("status") == "success":
           
            crew_output = results.get("unknown_type", None)

            if crew_output:
              
                try:
                    raw_content = crew_output.raw if hasattr(crew_output, 'raw') else None
                    
                    if raw_content:
                       
                        structured_output['data'] = {
                           
                            "research_findings": {
                                "data_sources": raw_content.get('data_sources', []),
                                "price_data": raw_content.get('price_data', {}),
                                
                            },
                           
                        }
                except Exception as e:
                    print(f"Error parsing crew output: {str(e)}")
                    structured_output['status'] = 'error'
                    structured_output['message'] = 'Failed to parse crew output.'

        return structured_output
