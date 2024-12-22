import os
import sys

# Add the src directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from dotenv import load_dotenv
load_dotenv()

from crew import FinancialAnalystCrew
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def index():
    return jsonify({
        "status": "online",
        "message": "Financial Analyst API is running"
    })

@app.route('/health')
def health():
    return jsonify({
        "status": "healthy",
        "version": "1.0"
    })

@app.route('/analyze/<symbol>')
def analyze(symbol):
    try:
        crew = FinancialAnalystCrew(
            job_id="test_run",
            asset_name=symbol,
            primary_llm="groq",
            backup_llm="gpt"
        )
        result = crew.kickoff()
        return jsonify(result)
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port, debug=True)
