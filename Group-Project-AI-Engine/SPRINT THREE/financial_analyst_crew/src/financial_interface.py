from typing import Dict, List, Optional
from datetime import datetime
import uuid
from crew import FinancialAnalystCrew
from PricePredictions import PricePredictions
from database import Database

class FinancialInterface:
    def __init__(self):
        self.price_predictions = PricePredictions()
        self.db = Database()

    def request_analysis(self, asset_name: str, llm_choice: str, client_type: str) -> Dict:
        """Request a new analysis following the collection structure"""
        try:
            if client_type != 'mobile':
                raise ValueError("Analysis only available for mobile clients")

            
            job_id = str(uuid.uuid4())
            crew = FinancialAnalystCrew(job_id=job_id, asset_name=asset_name, llm_choice=llm_choice)
            crew.setup_crew()
            analysis_result = crew.kickoff()

           
            full_analysis_report = {
                'asset_name': asset_name,
                'timestamp': datetime.now(),
                'metadata': {
                    'llm_used': llm_choice,
                    'tools_used': ['YahooFinance', 'WebSearch'],
                    'analysis_type': 'full_analysis'
                },
                'agent_processing': {
                    'researcher_complete': True,
                    'accountant_complete': True,
                    'recommender_complete': True,
                    'blogger_complete': True
                },
                'research_findings': analysis_result.get('research', {}),
                'financial_analysis': analysis_result.get('financial', {}),
                'recommendation': analysis_result.get('recommendation', {}),
                'final_report': {
                    'executive_summary': analysis_result.get('executive_summary', ''),
                    'sections': {
                        'overview': analysis_result.get('overview', ''),
                        'research_findings': analysis_result.get('research_summary', ''),
                        'financial_analysis': analysis_result.get('financial_summary', ''),
                        'recommendation': analysis_result.get('recommendation_summary', '')
                    },
                    'disclaimers': analysis_result.get('disclaimers', [])
                }
            }

           
            report_id = self.db.store_analysis_report(asset_name, full_analysis_report)
            
           
            return {
                "status": "success",
                "report_id": report_id,
                "final_report": full_analysis_report['final_report']
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def get_analysis_report(self, report_id: str, client_type: str) -> Dict:
        """Retrieve analysis report"""
        try:
            if client_type != 'mobile':
                raise ValueError("Analysis only available for mobile clients")

            report = self.db.get_analysis_report(report_id)
            if not report:
                return {"status": "error", "message": "Report not found"}

            #
            return {
                "status": "success",
                "report_id": report_id,
                "final_report": report.get('final_report', {})
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def get_single_prediction(self, asset_name: str, timeframe: int = 30) -> Dict:
        """Get price prediction for a single asset"""
        try:
            
            prediction_result = self.price_predictions.predictions(
                asset=asset_name,
                prediction_timeframe=timeframe
            )
            
            if prediction_result is None:
                return {}

           
            prediction_data = {
                'predictions': prediction_result['Predictions'].tolist(),
                'dates': [d.strftime('%Y-%m-%d') for d in prediction_result['Dates']],
                'timeframe': timeframe,
                'timestamp': datetime.now()
            }
            
           
            prediction_id = self.db.store_price_predictions(
                asset_name=asset_name,
                prediction=prediction_data
            )

            return {
                "asset_name": asset_name,
                "prediction_id": prediction_id,
                "timestamp": datetime.now().isoformat(),
                "timeframe": timeframe,
                "predictions": prediction_result['Predictions'].tolist(),
                "dates": [d.strftime('%Y-%m-%d') for d in prediction_result['Dates']]
            }
        except Exception as e:
            raise Exception(f"Failed to get prediction for {asset_name}: {str(e)}")

    def get_multiple_predictions(self, asset_list: List[str], timeframe: int = 30) -> Dict:
        """Get predictions for multiple assets"""
        try:
            predictions = {}
            for asset in asset_list:
                prediction = self.get_single_prediction(asset, timeframe)
                if prediction:
                    predictions[asset] = prediction

            return {
                "timestamp": datetime.now().isoformat(),
                "timeframe": timeframe,
                "predictions": predictions
            }
        except Exception as e:
            raise Exception(f"Failed to get multiple predictions: {str(e)}")
