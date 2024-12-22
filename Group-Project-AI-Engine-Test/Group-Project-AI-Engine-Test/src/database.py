from firebase_admin import credentials, firestore, initialize_app
from datetime import datetime
import logging
from typing import Dict, Optional,  Any


class Database:
    def __init__(self):
        try:
            cred_path = '/etc/secrets/act-database-2e605-firebase-adminsdk-cb68g-047843c94b.json'
            logging.info(f"Attempting to initialize Firebase with credentials from: {cred_path}")
            creds = credentials.Certificate(cred_path)
            initialize_app(creds)
            self.db = firestore.client()
            logging.info("Firebase initialization successful")
        except Exception as e:
            logging.error(f"Failed to initialize Firebase: {str(e)}")
            raise

    def store_analysis_report(self, asset_name: str, report: dict) -> str:
        try:
            doc_ref = self.db.collection('analysis_reports').document()
            logging.info(f"Attempting to store report for {asset_name} with ID: {doc_ref.id}")
            logging.debug(f"Report content: {report}")  # Be careful with sensitive data
            
            report.update({
                'asset_name': asset_name,
                'timestamp': datetime.now().isoformat(),
                'report_id': doc_ref.id
            })
            doc_ref.set(report)
            logging.info(f'Successfully stored analysis report for {asset_name} with ID: {doc_ref.id}')
            return doc_ref.id
        except Exception as e:
            logging.error(f'Error storing analysis report for {asset_name}: {str(e)}')
            raise  # Change this to raise the exception instead of returning a string

def store_price_predictions(
        self, 
        asset_name: str, 
        predictions: dict,
        timeframe: str = "1M"
    ) -> str:
        try:
            doc_ref = self.db.collection('price_predictions').document()
            
           
            prediction_data = {
                'asset_name': asset_name,
                'timestamp': datetime.now().isoformat(),
                'prediction_id': doc_ref.id,
                'timeframe': timeframe,
                'predictions': predictions,
                'metadata': {
                    'last_updated': datetime.now().isoformat(),
                    'status': 'active'
                }
            }
            
            doc_ref.set(prediction_data)
            logging.info(f'Stored price predictions for {asset_name} with ID: {doc_ref.id}')
            return doc_ref.id
        except Exception as e:
            logging.error(f'Error storing price predictions for {asset_name}: {str(e)}')
            raise

def store_multiple_predictions(
        self, 
        predictions: Dict[str, dict],
        timeframe: str = "1M"
    ) -> str:
        try:
            doc_ref = self.db.collection('multiple_predictions').document()
            
            
            prediction_data = {
                'prediction_id': doc_ref.id,
                'timestamp': datetime.now().isoformat(),
                'timeframe': timeframe,
                'predictions': predictions,
                'metadata': {
                    'asset_count': len(predictions),
                    'last_updated': datetime.now().isoformat(),
                    'status': 'active'
                }
            }
            
            doc_ref.set(prediction_data)
            logging.info(f'Stored multiple predictions with ID: {doc_ref.id}')
            return doc_ref.id
        except Exception as e:
            logging.error(f'Error storing multiple predictions: {str(e)}')
            raise

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

    def test_connection(self):
        """Test Firebase connection and write permissions"""
        try:
            test_ref = self.db.collection('test').document()
            test_ref.set({
                'timestamp': datetime.now().isoformat(),
                'test': True
            })
            test_ref.delete()  # Clean up after test
            logging.info("Firebase connection test successful")
            return True
        except Exception as e:
            logging.error(f"Firebase connection test failed: {str(e)}")
            return False

    def get_latest_prediction(
        self, 
        asset_name: str,
        timeframe: str = "1M"
    ) -> Optional[Dict[str, Any]]:
        """Get the most recent prediction for an asset."""
        try:
           
            docs = (self.db.collection('price_predictions')
                   .where('asset_name', '==', asset_name)
                   .where('timeframe', '==', timeframe)
                   .order_by('timestamp', direction='desc')
                   .limit(1)
                   .stream())
            
            for doc in docs:
                return doc.to_dict()
            
            return None
        except Exception as e:
            logging.error(f'Error getting latest prediction for {asset_name}: {str(e)}')
            return None

def get_multiple_predictions_by_id(
        self, 
        prediction_id: str
    ) -> Optional[Dict[str, Any]]:
        """Retrieve multiple predictions by ID."""
        try:
            return self._get_document('multiple_predictions', prediction_id)
        except Exception as e:
            logging.error(f'Error retrieving multiple predictions with ID {prediction_id}: {str(e)}')
            return None

    def get_predictions_by_timeframe(
        self,
        asset_name: str,
        timeframe: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get historical predictions for a specific timeframe."""
        try:
            docs = (self.db.collection('price_predictions')
                   .where('asset_name', '==', asset_name)
                   .where('timeframe', '==', timeframe)
                   .order_by('timestamp', direction='desc')
                   .limit(limit)
                   .stream())
            
            return [doc.to_dict() for doc in docs]
        except Exception as e:
            logging.error(f'Error getting predictions for {asset_name}: {str(e)}')
            return []
