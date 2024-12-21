from firebase_admin import credentials, firestore, initialize_app
from datetime import datetime
import logging
from typing import Dict, Optional,  Any


class Database:
    def __init__(self):
        creds = credentials.Certificate('')
        initialize_app(creds)
        self.db = firestore.client()

    def store_analysis_report(self, asset_name: str, report: dict) -> str:
        try:
            doc_ref = self.db.collection('analysis_reports').document()
            report.update({
                'asset_name': asset_name,
                'timestamp': datetime.now().isoformat(),
                'report_id': doc_ref.id
            })
            doc_ref.set(report)
            logging.info(f'Stored analysis report for {asset_name} with ID: {doc_ref.id}')
            return doc_ref.id
        except Exception as e:
            logging.error(f'Error storing analysis report for {asset_name}: {str(e)}')
            return 'Error storing analysis'

    def store_price_predictions(self, asset_name: str, prediction: dict) -> str:
        try:
            doc_ref = self.db.collection('price_predictions').document()
            prediction.update({
                'asset_name': asset_name,
                'timestamp': datetime.now().isoformat(),
                'prediction_id': doc_ref.id
            })
            doc_ref.set(prediction)
            logging.info(f'Stored price predictions for {asset_name} with ID: {doc_ref.id}')
            return doc_ref.id
        except Exception as e:
            logging.error(f'Error storing price predictions for {asset_name}: {str(e)}')
            return 'Error storing price predictions'

    def get_historical_data(self, asset_name: str, limit: int = 100) -> list:
        try:
            docs = (self.db.collection('historical_data')
                    .where('asset_name', '==', asset_name)
                    .order_by('timestamp', direction='desc')
                    .limit(limit)
                    .stream())
            return [doc.to_dict() for doc in docs]
        except Exception as e:
            logging.error(f'Error getting historical data for {asset_name}: {str(e)}')
            return []

    def _get_document(self, collection_name: str, document_id: str) -> Optional[Dict[str, Any]]:
        """Utility function to retrieve a document from a Firestore collection."""
        try:
            doc = self.db.collection(collection_name).document(document_id).get()
            if doc.exists:
                return doc.to_dict()  # Return a dictionary
            else:
                logging.warning(f'No document found in {collection_name} with ID: {document_id}')
                return None  
        except Exception as e:
            logging.error(f'Error retrieving document from {collection_name} with ID {document_id}: {str(e)}')
            return None  

    def get_analysis_report(self, report_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve an analysis report by its ID."""
        document_data = self._get_document('analysis_reports', report_id)
        if document_data:
            return document_data
        else:
            logging.info(f'No analysis report found with ID: {report_id}')
            return None  


    def get_price_predictions(self, prediction_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve price predictions by its ID."""
        document_data=  self._get_document('price_predictions', prediction_id)
        if document_data:  # Ensure we got valid document data
            return document_data
        else:
            logging.info(f'No analysis report found with ID: {prediction_id}')
            return None # Explicitly returning None if not found
