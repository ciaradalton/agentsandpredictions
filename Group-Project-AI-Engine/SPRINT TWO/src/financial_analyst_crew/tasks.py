from crewai import Task
from pathlib import Path
import yaml

class FinancialTasks:
    def __init__(self, agents):
        self.agents = agents
        
        
        current_dir = Path(__file__).parent
        config_path = current_dir / "config" / "tasks.yaml"
        
        with open(config_path, 'r') as file:
            self.config = yaml.safe_load(file)
    
    
    def analyze_stock(self) -> Task:
        return Task(
            description=self.config['analyze_stock_task']['description'],
            expected_output=self.config['analyze_stock_task']['expected_output'],
            agent=self.agents.researcher,
            context=[{
                "description": "Analyze stock data and metrics",
                "expected_output": "Comprehensive analysis report",
                "tools": ["website_search"],
                "data_sources": ["coinmarketcap.com", "coingecko.com", "tradingview.com"],
                "agent": self.agents.researcher
            }]
        )
    
    
    def research_stock(self) -> Task:
        return Task(
            description=self.config['research_stock_task']['description'],
            expected_output=self.config['research_stock_task']['expected_output'],
            agent=self.agents.accountant,
            context=[{
                "description": "Research financial metrics",
                "expected_output": "Financial metrics analysis",
                "tools": ["website_search"],
                "agent": self.agents.accountant
            }]
        )
    
    
    def make_decision(self) -> Task:
        return Task(
            description=self.config['make_decision_task']['description'],
            expected_output=self.config['make_decision_task']['expected_output'],
            agent=self.agents.recommender,
            context=[{
                "description": "Make investment recommendation",
                "expected_output": "Investment decision with rationale",
                "tools": ["website_search"],
                "agent": self.agents.recommender
            }]
        )
    
    
    def output_report(self) -> Task:
        return Task(
            description=self.config['output_task']['description'],
            expected_output=self.config['output_task']['expected_output'],
            agent=self.agents.blogger,
            context=[{
                "description": "Create final report",
                "expected_output": "Comprehensive investment report",
                "tools": ["website_search"],
                "agent": self.agents.blogger
            }]
        )