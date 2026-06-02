import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/progress_tracker")
    JWT_SECRET = os.getenv("JWT_SECRET", "changeme")
    DEBUG = os.getenv("FLASK_DEBUG", "False") == "True"
