from crewai import Task
from pathlib import Path
import yaml
import os

class FinancialTasks:
    def __init__(self, agents, asset_name: str):
        self.agents = agents
        self.asset_name = asset_name
        
        current_dir = Path(__file__).parent.parent
        config_path = current_dir / "config" / "tasks.yaml"
       
        with open(config_path, 'r') as file:
            self.config = yaml.safe_load(file)

    def research_stock(self) -> Task:
        description = self.config['research_stock_task']['description'].format(
            asset_name=self.asset_name
        )
        return Task(
            description=description,
            expected_output=self.config['research_stock_task']['expected_output'],
            agent=self.agents.researcher()
        )

    def analyze_stock(self) -> Task:
        description = self.config['analyze_stock_task']['description'].format(
            asset_name=self.asset_name
        )
        return Task(
            description=description,
            expected_output=self.config['analyze_stock_task']['expected_output'],
            agent=self.agents.accountant()
        )

    def make_decision(self) -> Task:
        description = self.config['make_decision_task']['description'].format(
            asset_name=self.asset_name
        )
        return Task(
            description=description,
            expected_output=self.config['make_decision_task']['expected_output'],
            agent=self.agents.recommender()
        )

    def output_report(self) -> Task:
        description = self.config['output_task']['description'].format(
            asset_name=self.asset_name
        )
        return Task(
            description=description,
            expected_output=self.config['output_task']['expected_output'],
            agent=self.agents.blogger()
        )
