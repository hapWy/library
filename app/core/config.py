import os
from dotenv import load_dotenv

load_dotenv()

# DATABASE_URL = "postgresql+asyncpg://postgres:1@localhost:5432/library"
DATABASE_URL = os.getenv("DATABASE_URL")

