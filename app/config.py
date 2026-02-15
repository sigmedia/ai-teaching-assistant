from dotenv import load_dotenv
import os

if not os.getenv('AZURE'):  # This only exists in Azure env
    load_dotenv()

class Settings:
    ENVIRONMENT = os.getenv("ENVIRONMENT", "prod")
    BOT_NAME = os.getenv("BOT_NAME", "AI teaching assistant")
    COURSE_NAME = os.getenv("COURSE_NAME", "your course")
    GLOBAL_USERNAME = os.getenv("GLOBAL_USERNAME", "")
    AGREEMENT_PART_1_VERSION=os.getenv("AGREEMENT_PART_1_VERSION", "")
    AGREEMENT_PART_2_VERSION=os.getenv("AGREEMENT_PART_2_VERSION", "")
    MIDDLEWARE_SECRET = os.getenv("MIDDLEWARE_SECRET", "")
    GLOBAL_PASSWORD = os.getenv("GLOBAL_PASSWORD", "")
    CHAT_API_ENDPOINT = os.getenv("CHAT_API_ENDPOINT", "")
    CHAT_API_KEY = os.getenv("CHAT_API_KEY", "")
    DB_CONN_STR = os.getenv("DB_CONN_STR","")
    SCHEDULER_FREQ_MINS = os.getenv("SCHEDULER_FREQ_MINS",120)
    MAX_INTERACTIONS_HISTORY = os.getenv("MAX_INTERACTIONS_HISTORY",10)
    MAX_INACTIVE_TIME_MINS = os.getenv("MAX_INACTIVE_TIME_MINS",60)
    REQUEST_TIMEOUT_SECS = os.getenv("REQUEST_TIMEOUT_SECS",45)

settings = Settings()