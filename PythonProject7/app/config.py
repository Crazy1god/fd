import os
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv("FSTR_DB_HOST", "localhost")
DB_PORT = int(os.getenv("FSTR_DB_PORT", "5432"))  # Преобразуем в int
DB_USER = os.getenv("FSTR_DB_LOGIN", "postgres")
DB_PASS = os.getenv("FSTR_DB_PASS", "")
DB_NAME = os.getenv("FSTR_DB_NAME", "fstr")

DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"