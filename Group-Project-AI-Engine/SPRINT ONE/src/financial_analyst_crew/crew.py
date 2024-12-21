import yaml
from typing import Dict, Any
from crewai import Agent, Crew, Process, Task
from langchain_groq import ChatGroq
from crewai_tools import WebsiteSearchTool
from pydantic import SecretStr
import os
from pathlib import Path

class FinancialAnalystCrew:
    """FinancialAnalystCrew for financial analysis tasks"""

    def __init__(self) -> None:
        current_dir = Path(__file__).parent
        self.agents_config_path = current_dir / "config" / "agents.yaml"
        self.tasks_config_path = current_dir / "config" / "tasks.yaml"

        self.agents_config: Dict[str, Any] = {}
        self.tasks_config: Dict[str, Any] = {}

        api_key = os.getenv("GROQ_API_KEY")
        if api_key is not None:
            api_key = SecretStr(api_key)

        self.groq_llm = ChatGroq(
            temperature=0,
            stop_sequences=["\n", "END", "<END>", "STOP"],
            api_key=api_key
        )

        try:
            with open(self.agents_config_path, 'r') as file:
                self.agents_config = yaml.safe_load(file)
            with open(self.tasks_config_path, 'r') as file:
                self.tasks_config = yaml.safe_load(file)
        except FileNotFoundError as e:
            print(f"Configuration file not found: {e}")
            raise
        except yaml.YAMLError as e:
            print(f"Error parsing YAML configuration: {e}")
            raise

        self.website_search_tool = WebsiteSearchTool(
            config={
                "request_timeout": 30,
                "max_retries": 3,
                "user_agent": "Mozilla/5.0",
                "ssl_verify": True
            }
        )

    def researcher(self) -> Agent:
        return Agent(
            role=self.agents_config['researcher']['role'],
            goal=self.agents_config['researcher']['goal'],
            backstory=self.agents_config['researcher']['backstory'],
            llm=self.groq_llm,
            tools=[self.website_search_tool],
            verbose=True,
            allow_delegation=False
        )

    def accountant(self) -> Agent:
        return Agent(
            role=self.agents_config['accountant']['role'],
            goal=self.agents_config['accountant']['goal'],
            backstory=self.agents_config['accountant']['backstory'],
            llm=self.groq_llm,
            tools=[self.website_search_tool],
            verbose=True,
            allow_delegation=False
        )

    def recommender(self) -> Agent:
        return Agent(
            role=self.agents_config['recommender']['role'],
            goal=self.agents_config['recommender']['goal'],
            backstory=self.agents_config['recommender']['backstory'],
            llm=self.groq_llm,
            tools=[self.website_search_tool],
            verbose=True,
            allow_delegation=False
        )

    def blogger(self) -> Agent:
        return Agent(
            role=self.agents_config['blogger']['role'],
            goal=self.agents_config['blogger']['goal'],
            backstory=self.agents_config['blogger']['backstory'],
            llm=self.groq_llm,
            tools=[self.website_search_tool],
            verbose=True,
            allow_delegation=False
        )

    def analyze_stock_task(self) -> Task:
        """Creates the stock analysis task"""
        researcher = self.researcher()
        return Task(
            description=self.tasks_config['analyze_stock_task']['description'],
            expected_output=self.tasks_config['analyze_stock_task']['expected_output'],
            agent=researcher,
            context=[{
                "description": "Analyze stock data and metrics",
                "expected_output": "Comprehensive analysis report",
                "tools": ["website_search"],
                "data_sources": ["coinmarketcap.com", "coingecko.com", "tradingview.com"],
                "agent": researcher
            }]
        )

    def research_stock_task(self) -> Task:
        """Creates the stock research task"""
        accountant = self.accountant()
        return Task(
            description=self.tasks_config['research_stock_task']['description'],
            expected_output=self.tasks_config['research_stock_task']['expected_output'],
            agent=accountant,
            context=[{
                "description": "Research financial metrics",
                "expected_output": "Financial metrics analysis",
                "tools": ["website_search"],
                "agent": accountant
            }]
        )

    def make_decision_task(self) -> Task:
        """Creates the decision making task"""
        recommender = self.recommender()
        return Task(
            description=self.tasks_config['make_decision_task']['description'],
            expected_output=self.tasks_config['make_decision_task']['expected_output'],
            agent=recommender,
            context=[{
                "description": "Make investment recommendation",
                "expected_output": "Investment decision with rationale",
                "tools": ["website_search"],
                "agent": recommender
            }]
        )

    def output_task(self) -> Task:
        """Creates the output task"""
        blogger = self.blogger()
        return Task(
            description=self.tasks_config['output_task']['description'],
            expected_output=self.tasks_config['output_task']['expected_output'],
            agent=blogger,
            context=[{
                "description": "Create final report",
                "expected_output": "Comprehensive investment report",
                "tools": ["website_search"],
                "agent": blogger
            }]
        )

    def crew(self) -> Crew:
        """Creates the FinancialAnalystCrew"""
        return Crew(
            agents=[
                self.researcher(),
                self.accountant(),
                self.recommender(),
                self.blogger()
            ],
            tasks=[
                self.analyze_stock_task(),
                self.research_stock_task(),
                self.make_decision_task(),
                self.output_task()
            ],
            process=Process.sequential,
            verbose=True
        )