import os
from dotenv import load_dotenv


load_dotenv()

# Load environment variables from .env file and set default values if needed
class Settings(object):
    def __init__(self):
        self.ENV = os.getenv("ENV", "development")
        self.DEBUG = os.getenv("DEBUG", "False").lower() == "true"
        self.DOCKERIZED = os.getenv("DOCKERIZED", "False").lower() == "true"
        self.GOOGLE_GEMINI_TOKEN = os.getenv("GOOGLE_GEMINI_TOKEN")
        self.GOOGLE_GEMINI_MODEL = os.getenv("GOOGLE_GEMINI_MODEL", "gemini-2.0-flash")
        self.OPENAI_TOKEN = os.getenv("OPENAI_TOKEN")
        self.OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")


settings = Settings()
