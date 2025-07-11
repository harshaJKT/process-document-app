import os
from dotenv import load_dotenv


load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads") 

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is missing in .env")
