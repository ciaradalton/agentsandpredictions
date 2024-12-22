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
@log_request
def request_analysis():
    """Endpoint to request a new financial analysis"""
    try:
        data = request.json
        if not data:
            raise APIError("No JSON data provided", HTTPStatus.BAD_REQUEST)
        
        logger.debug(f"Analysis request received for data: {data}")
        
        if 'asset_name' not in data:
            raise APIError("Missing asset_name in request", HTTPStatus.BAD_REQUEST)
        
        client_type = request.args.get('client_type')
        if not client_type in ['mobile', 'web']:
            raise APIError('Invalid client type', HTTPStatus.BAD_REQUEST)
            
        if client_type == 'web':
            raise APIError('Analysis not available for web clients', HTTPStatus.FORBIDDEN)
            
        llm_choice = data.get('llm_choice', 'groq')
        
        result = interface.request_analysis(
            asset_name=data['asset_name'],
            llm_choice=llm_choice,
            client_type=client_type
        )
        
        logger.info(f"Analysis completed successfully for asset: {data['asset_name']}")
        return jsonify(result), HTTPStatus.OK
    
    except Exception as e:
        logger.error(f"Error in analysis request: {str(e)}", exc_info=True)
        raise APIError(str(e), HTTPStatus.INTERNAL_SERVER_ERROR)

@app.route('/api/analysis/<report_id>', methods=['GET'])
@log_request
def get_analysis_report(report_id):
    """Endpoint to retrieve analysis report (mobile only, final report only)"""
    try:
        client_type = request.headers.get('X-Client-Type')
        logger.debug(f"Report request received for ID: {report_id}, Client: {client_type}")
        
        if not client_type or client_type not in ['mobile', 'web']:
            raise APIError("Invalid client type", HTTPStatus.BAD_REQUEST)
        
        if client_type == 'web':
            raise APIError("Analysis not available for web clients", HTTPStatus.FORBIDDEN)
        
        result = interface.get_analysis_report(report_id, client_type)
        if result['status'] == 'error':
            raise APIError(result['message'], HTTPStatus.NOT_FOUND)
            
        logger.info(f"Report retrieved successfully for ID: {report_id}")
        return jsonify({
            "status": "success",
            "report_id": result['report_id'],
            "final_report": result['final_report']
        }), HTTPStatus.OK
        
    except Exception as e:
        logger.error(f"Error retrieving report {report_id}: {str(e)}", exc_info=True)
        raise APIError(str(e), HTTPStatus.INTERNAL_SERVER_ERROR)

@app.route('/api/predictions/<asset_name>', methods=['GET'])
@log_request
def get_prediction(asset_name):
    """Endpoint for single asset prediction"""
    try:
        timeframe = request.args.get('timeframe', default="1M")
        include_all_timeframes = request.args.get('include_all_timeframes', 
                                                default='false').lower() == 'true'
        
        logger.debug(f"Prediction request for asset: {asset_name}, "
                    f"timeframe: {timeframe}, all_timeframes: {include_all_timeframes}")
        
        prediction = interface.get_single_prediction(
            asset_name, 
            timeframe=timeframe,
            include_all_timeframes=include_all_timeframes
        )
        
        if prediction is None:
            raise APIError(f"No prediction available for {asset_name}", 
                         HTTPStatus.NOT_FOUND)
        
        logger.info(f"Prediction completed for asset: {asset_name}")
        return jsonify(prediction), HTTPStatus.OK
        
    except Exception as e:
        logger.error(f"Error in prediction for {asset_name}: {str(e)}", 
                    exc_info=True)
        raise APIError(str(e), HTTPStatus.INTERNAL_SERVER_ERROR)
        
@app.route('/api/predictions/multiple', methods=['POST'])
@log_request
def get_multiple_predictions():
    """Endpoint for multiple asset predictions"""
    try:
        data = request.get_json()
        if not data or 'assets' not in data:
            raise APIError('Missing assets list', HTTPStatus.BAD_REQUEST)
        
        timeframe = data.get('timeframe', "1M")
        include_all_timeframes = data.get('include_all_timeframes', False)
        
        logger.debug(f"Multiple predictions request received for assets: {data['assets']}, "
                    f"timeframe: {timeframe}, all_timeframes: {include_all_timeframes}")
        
        predictions = interface.get_multiple_predictions(
            assets=data['assets'],
            timeframe=timeframe,
            include_all_timeframes=include_all_timeframes
        )
        
        logger.info(f"Multiple predictions completed for {len(data['assets'])} assets")
        return jsonify(predictions), HTTPStatus.OK
        
    except Exception as e:
        logger.error(f"Error in multiple predictions: {str(e)}", exc_info=True)
        raise APIError(str(e), HTTPStatus.INTERNAL_SERVER_ERROR)

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

