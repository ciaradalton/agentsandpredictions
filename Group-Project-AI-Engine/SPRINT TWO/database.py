from firebase_admin import credentials, firestore, initialize_app
from datetime import datetime
import json

class Database:
    def __init__(self):
        creds = credentials.Certificate('')
        initialize_app(creds)
        self.db = firestore.client()

    def store_analysis_report(self, asset_name: str, report: dict) ->str:
        try:
            doc = self.db.collection('analyisis_reports').document()
            report.update({
                'asset_name': asset_name,
                'timestamp': datetime.now(),
                'report_id': doc.id
            })
            doc.set(report)
            return doc.id
        except Exception as e:
           return f'Error storing analysis {e}'

    def store_price_predictions(self,asset_name:str, prediction: dict) -> str:
        try:
            doc = self.db.collection('price_predictions').document()
            prediction.update({
                'asset_name': asset_name,
                'timestamp': datetime.now(),
                'prediction_id': doc.id
            })
            doc.set(prediction)
            return doc.id
        except Exception as e:
            return f'Error storing price predicitons {e}'


    def get_historical_data(self, asset_name: str, limit: int = 100) -> list:
        try:
            docs = (self.db.collection('historical_data')
                   .where('asset_name', '==', asset_name)
                   .order_by('timestamp', direction='desc')
                   .limit(limit)
                   .stream())
            return [doc.to_dict() for doc in docs]

        except Exception as e:
            print(f'Error getting historical data {e}')
            return []


    def get_analysis_report(self, report_id:str) -> dict:
        try:
            doc = self.db.collection('analysis_reports').document(report_id).get()
            return doc.to_dict() if doc.exists else {}

        except Exception as e:
            print(f'Error retrieving analysis report {e}')
            return {}

    def get_price_predictions(self, prediction_id:str) -> dict:
        try:
            doc = self.db.collection('price_predictions').document(prediction_id).get()
            return doc.to_dict() if doc.exists else {}

        except Exception as e:
            print(f'Error retrieving price predictions {e}')
            return {}


    

            

