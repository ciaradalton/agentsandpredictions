from crewai import Agent
from pathlib import Path
import yaml

class FinancialAgents:
    def __init__(self, llm):
        self.llm = llm
        
        current_dir = Path(__file__).parent.parent
        config_path = current_dir / "config" / "agents.yaml"

        with open(config_path, 'r') as file:
            self.config = yaml.safe_load(file)

    def _create_base_agent(self, agent_type: str):
        if not self.llm:
            raise ValueError(f"LLM is not initialized for agent type: {agent_type}")

        print(f"Creating agent: {agent_type}")
        
        return Agent(
            role=self.config[agent_type]['role'],
            goal=self.config[agent_type]['goal'],
            backstory=self.config[agent_type]['backstory'],
            llm=self.llm,
            verbose=True,
            allow_delegation=False
        )

    def researcher(self) -> Agent:
        return self._create_base_agent('researcher')

    def accountant(self) -> Agent:
        return self._create_base_agent('accountant')

    def recommender(self) -> Agent:
        return self._create_base_agent('recommender')

    def blogger(self) -> Agent:
        return self._create_base_agent('blogger')
