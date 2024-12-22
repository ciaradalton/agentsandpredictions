from flask import Flask, jsonify, request, abort
from flask_cors import CORS
from financial_interface import FinancialInterface
from http import HTTPStatus
import logging
import os
import time
from functools import wraps


logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app, resources={
    r"/*": {  # This will apply to all routes, including /health
        "origins": "*",
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Accept", "X-Client-Type"],
        "expose_headers": ["Content-Type", "X-Client-Type"]
    }
})

interface = FinancialInterface()

class APIError(Exception):
    def __init__(self, message, status_code):
        super().__init__()
        self.message = message
        self.status_code = status_code

def log_request(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        start_time = time.time()
        logger.info(f"Request started: {request.method} {request.path}")
        
        try:
            response = f(*args, **kwargs)
            duration = time.time() - start_time
            logger.info(f"Request completed: {request.method} {request.path} - Duration: {duration:.2f}s")
            return response
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"Request failed: {request.method} {request.path} - Duration: {duration:.2f}s - Error: {str(e)}")
            raise
    
    return decorated_function

@app.errorhandler(APIError)
def handle_api_error(error):
    logger.error(f"API Error: {error.message} (Status: {error.status_code})")
    response = jsonify({'error': error.message})
    response.status_code = error.status_code
    return response

@app.errorhandler(Exception)
def handle_unexpected_error(error):
    logger.error(f"Unexpected error: {str(error)}", exc_info=True)
    response = jsonify({'error': 'An unexpected error occurred'})
    response.status_code = HTTPStatus.INTERNAL_SERVER_ERROR
    return response

@app.route('/health')
def health_check():
    """Health check endpoint for Render"""
    try:
        # Add any critical service checks here
        return jsonify({
            'status': 'healthy',
            'timestamp': time.time(),
            'environment': os.environ.get('FLASK_ENV', 'production')
        }), HTTPStatus.OK
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return jsonify({'status': 'unhealthy'}), HTTPStatus.SERVICE_UNAVAILABLE

@app.route('/api/analysis', methods=['POST'])
def request_analysis():
    """Endpoint to request analysis."""
    try:
        data = request.get_json()
        asset_name = data.get("asset_name")
        llm_choice = data.get("llm_choice")
        client_type = data.get("client_type")

        result = financial_interface.request_analysis(asset_name, llm_choice, client_type)
        return jsonify(result), 200 if result["status"] == "success" else 400
    except Exception as e:
        logging.error(f"Error in request_analysis: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/get_analysis_report/<report_id>', methods=['GET'])
def get_analysis_report(report_id):
    """Endpoint to retrieve analysis report."""
    client_type = request.args.get('client_type', 'mobile')  # Example usage
    result = financial_interface.get_analysis_report(report_id, client_type)
    return jsonify(result), 200 if result["status"] == "success" else 400

@app.route('/api/predictions/single/<asset_name>', methods=['GET'])
def get_single_prediction(asset_name):
    """Endpoint to get price prediction for a single asset."""
    timeframe = request.args.get('timeframe', '1M')
    include_all_timeframes = request.args.get('include_all_timeframes', 'false').lower() == 'true'
    result = financial_interface.get_single_prediction(asset_name, timeframe, include_all_timeframes)
    return jsonify(result), 200 if result else 400

@app.route('/api/predictions/multiple', methods=['POST'])
def get_multiple_predictions():
    """Endpoint to get predictions for multiple assets."""
    data = request.get_json()
    asset_list = data.get('assets', [])
    timeframe = data.get('timeframe', '1M')
    include_all_timeframes = data.get('include_all_timeframes', False)
    result = financial_interface.get_multiple_predictions(asset_list, timeframe, include_all_timeframes)
    return jsonify(result), 200 if result else 400

@app.route('/api/predictions/timeframes', methods=['GET'])
@log_request
def get_available_timeframes():
    """Endpoint to get supported prediction timeframes"""
    try:
        timeframes = TimeFrame.get_supported_timeframes()
        return jsonify({
            'status': 'success',
            'timeframes': {
                key: {
                    'days': value,
                    'description': f"{key} prediction"
                } for key, value in timeframes.items()
            }
        }), HTTPStatus.OK
    except Exception as e:
        logger.error(f"Error getting timeframes: {str(e)}", exc_info=True)
        raise APIError(str(e), HTTPStatus.INTERNAL_SERVER_ERROR)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))  
    logger.info(f"Starting application on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)

