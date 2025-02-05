from dotenv import load_dotenv
import os
load_dotenv()

class Settings:
    DATABASE_URI: str = os.getenv("DATABASE_URI")

settings = Settings()

