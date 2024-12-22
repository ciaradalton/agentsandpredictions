from typing import Dict, List, Optional
from datetime import datetime
import uuid
from crew import FinancialAnalystCrew
from PricePredictions import PricePredictions
from database import Database
import logging

class TimeFrameConfig:
    VALID_TIMEFRAMES = {
        "1W": 7,
        "2W": 14,
        "1M": 30,
        "3M": 90,
        "6M": 180,
        "1Y": 365
    }
    DEFAULT_TIMEFRAME = "1M"

class FinancialInterface:
    def __init__(self):
        self.price_predictions = PricePredictions()
        self.db = Database()
        self.supported_timeframes = TimeFrameConfig.VALID_TIMEFRAMES

    def request_analysis(self, asset_name: str, llm_choice: str, client_type: str) -> Dict:
        """Request a new analysis following the collection structure"""
        try:
            if client_type != 'mobile':
                raise ValueError("Analysis only available for mobile clients")

            job_id = str(uuid.uuid4())
            logging.info(f"Starting analysis for job {job_id}, asset: {asset_name}")
            
            crew = FinancialAnalystCrew(job_id=job_id, asset_name=asset_name, llm_choice=llm_choice)
            crew.setup_crew()
            analysis_result = crew.kickoff()

            if analysis_result.get('status') != 'success':
                raise ValueError(f"Analysis failed: {analysis_result.get('message', 'Unknown error')}")

            full_analysis_report = {
                'asset_name': asset_name,
                'timestamp': datetime.now().isoformat(),
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
                'research_findings': analysis_result.get('data', {}).get('research_findings', {}),
                'final_report': {
                    'executive_summary': analysis_result.get('data', {}).get('executive_summary', ''),
                    'sections': analysis_result.get('data', {}).get('sections', {})
                }
            }

            logging.info(f"Storing analysis report for {asset_name}")
            report_id = self.db.store_analysis_report(asset_name, full_analysis_report)
            
            if not report_id or report_id.startswith('Error'):
                raise Exception(f"Failed to store report: {report_id}")

            return {
                "status": "success",
                "report_id": report_id,
                "final_report": full_analysis_report['final_report']
            }
        except Exception as e:
            logging.error(f"Error in request_analysis: {str(e)}", exc_info=True)
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


def _generate_prediction(self, asset_name: str, days_ahead: int) -> Dict:
        """Generate prediction for specific asset and timeframe"""
        try:
            prediction_result = self.price_predictions.predictions(
                asset=asset_name,
                prediction_timeframe=days_ahead
            )
            
            if prediction_result is None:
                return None

            return {
                'values': prediction_result['Predictions'].tolist(),
                'dates': [d.strftime('%Y-%m-%d') for d in prediction_result['Dates']],
                'confidence_intervals': self._calculate_confidence_intervals(prediction_result)
            }
        except Exception as e:
            logging.error(f"Error generating prediction: {str(e)}", exc_info=True)
            return None

def get_single_prediction(
        self, 
        asset_name: str, 
        timeframe: str = "1M",
        include_all_timeframes: bool = False
    ) -> Dict:
        """Get price prediction for a single asset"""
        try:
            if timeframe not in self.supported_timeframes:
                raise ValueError(f"Invalid timeframe. Supported timeframes: {list(self.supported_timeframes.keys())}")

            days_ahead = self.supported_timeframes[timeframe]
            
            if include_all_timeframes:
                predictions = {}
                for tf, days in self.supported_timeframes.items():
                    prediction_result = self._generate_prediction(asset_name, days)
                    if prediction_result:
                        predictions[tf] = prediction_result
            else:
                prediction_result = self._generate_prediction(asset_name, days_ahead)
                predictions = {timeframe: prediction_result} if prediction_result else {}

            if not predictions:
                return {}

            
            prediction_data = {
                'predictions': predictions,
                'metadata': {
                    'timeframes': list(predictions.keys()),
                    'generated_at': datetime.now().isoformat(),
                    'model_version': self.price_predictions.get_model_version()
                }
            }
            
            prediction_id = self.db.store_price_predictions(
                asset_name=asset_name,
                predictions=prediction_data,
                timeframe=timeframe
            )

            return {
                "asset_name": asset_name,
                "prediction_id": prediction_id,
                "timestamp": datetime.now().isoformat(),
                "timeframe": timeframe,
                "predictions": predictions,
                "metadata": prediction_data['metadata']
            }
        except Exception as e:
            logging.error(f"Failed to get prediction for {asset_name}: {str(e)}", exc_info=True)
            raise


    def get_multiple_predictions(
        self, 
        asset_list: List[str], 
        timeframe: str = "1M",
        include_all_timeframes: bool = False
    ) -> Dict:
        """Get predictions for multiple assets"""
        try:
            predictions = {}
            for asset in asset_list:
                prediction = self.get_single_prediction(
                    asset, 
                    timeframe,
                    include_all_timeframes
                )
                if prediction:
                    predictions[asset] = prediction

            
            market_analysis = self._generate_market_analysis(predictions)

            result = {
                "timestamp": datetime.now().isoformat(),
                "timeframe": timeframe,
                "predictions": predictions,
                "market_analysis": market_analysis,
                "metadata": {
                    "assets_analyzed": len(predictions),
                    "success_rate": len(predictions) / len(asset_list) if asset_list else 0,
                    "timeframes_included": ["1M"] if not include_all_timeframes else list(self.supported_timeframes.keys())
                }
            }

            
            self.db.store_multiple_predictions(result, timeframe)

            return result
        except Exception as e:
            logging.error(f"Failed to get multiple predictions: {str(e)}", exc_info=True)
            raise
