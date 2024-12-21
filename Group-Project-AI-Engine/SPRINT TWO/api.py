from flask import Flask, jsonify, request, abort
from flask_cors import CORS
from financial_interface import FinancialInterface
import logging

logger = logging.getLogger(__name__)
app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

interface = FinancialInterface()

@app.route('/api/analysis', methods=['POST'])
def request_analysis():
    """Endpoint to request a new analysis"""
    data = request.json
    if not data or 'asset_name' not in data:
        abort(400, description="Missing asset_name in request")
        
    result = interface.request_analysis(data['asset_name'])
    return jsonify(result), 200 if result['status'] == 'success' else 500

@app.route('/api/analysis/<report_id>', methods=['GET'])
def get_analysis(report_id):
    """Endpoint to retrieve a stored analysis"""
    result = interface.get_analysis(report_id)
    if result is None:
        abort(404, description="Analysis report not found")
    return jsonify(result)

@app.route('/api/prediction', methods=['POST'])
def request_prediction():
    """Endpoint to request new price predictions"""
    data = request.json
    if not data or 'asset_name' not in data:
        abort(400, description="Missing asset_name in request")
        
    timeframe = data.get('timeframe', 30)  # Default 30 days if not specified
    result = interface.request_prediction(data['asset_name'], timeframe)
    return jsonify(result), 200 if result['status'] == 'success' else 500

@app.route('/api/prediction/<prediction_id>', methods=['GET'])
def get_prediction(prediction_id):
    """Endpoint to retrieve stored predictions"""
    result = interface.get_predictions(prediction_id)
    if result is None:
        abort(404, description="Prediction not found")
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True, port=3001)





