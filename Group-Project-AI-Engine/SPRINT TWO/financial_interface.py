from financial_analyst_crew.crew import FinancialAnalystCrew
from database import Database
from PricePredictions import PricePredictions 

class FinancialInterface:
    def __init__(self):
        self.db_manager = Database()
        self.predictor = PricePredictions()


    def request_analysis(self, asset_name: str) -> dict:
        try:
            financial_crew = FinancialAnalystCrew(asset_name)
            financial_crew.setup_crew()
            analysis_results = financial_crew.kickoff()

            report_id = self.db_manager.store_analysis_report(
                asset_name = asset_name,
                report = analysis_results
            )

            return {
                'status': 'success',
                'report_id': report_id,
                'asset_name': asset_name
            }

        except Exception as e:
            return {
                'status': 'error',
                'message': str(e),
                'asset_name': asset_name
            }


    def request_prediction(self, asset_name: str, timeframe: int = 30) -> dict:
        try:
            prediction_results = self.predictor.predictions(asset_name, timeframe)
            if prediction_results:
                prediciton_id = self.db_manager.store_price_predictions(
                    asset_name = asset_name,
                    prediction = {
                        'timeframe': timeframe,
                        'predictions': prediction_results['Predictions'].tolist(),
                        'dates': [str(date) for date in prediction_results['Dates']]
                    })

                return {
                        'status': 'success',
                        'prediction_id': prediciton_id,
                        'asset_name': asset_name
                    }
                

        except Exception as e:
            return {
                'status': 'error',
                'message': str(e),
                'asset_name': asset_name
            }


    def get_analysis(self, report_id:str) -> dict:
        return self.db_manager.get_analysis_report(report_id)

    def get_predictions(self, prediction_id: str) -> dict:
        return self.db_manager.get_price_predictions(prediction_id)

