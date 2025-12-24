import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Load environment variables (so we don't hardcode passwords)
load_dotenv()

# Get the Database URL from .env file, or fall back to a default for local testing
# Format: postgresql://user:password@host:port/database_name
# DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost/order_db")
DATABASE_URL = os.getenv("DATABASE_URL") 

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()