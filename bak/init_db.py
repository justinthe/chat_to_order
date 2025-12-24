from database import engine
from models import Base

def init_db():
    print("Connecting to PostgreSQL...")
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ Success! Tables (orders, customers, raw_logs) created.")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    init_db()