from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Ensure required environment variables are set
required_vars = [
    'GROQ_API_KEY',
    'OPENAI_API_KEY'
]

# Add check for Firebase credentials file
FIREBASE_CREDS_PATH = '/etc/secrets/act-database-2e605-firebase-adminsdk-cb68g-047843c94b.json'
if not os.path.exists(FIREBASE_CREDS_PATH):
    raise EnvironmentError(f"Missing Firebase credentials file at: {FIREBASE_CREDS_PATH}")

for var in required_vars:
    if not os.getenv(var):
        raise EnvironmentError(f"Missing required environment variable: {var}")
