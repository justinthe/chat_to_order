from fastapi import FastAPI, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from datetime import datetime
import models
import schemas
import database

# Initialize the App
app = FastAPI(title="Home Business Order Bot")

# Dependency to get the database session
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 1. Health Check Endpoint (To see if the server is alive)
@app.get("/")
def read_root():
    return {"status": "online", "time": datetime.now()}

# 2. The Webhook Endpoint (Where Chat Apps send data)
@app.post("/webhook", response_model=schemas.WebhookResponse)
def receive_message(payload: schemas.WebhookPayload, db: Session = Depends(get_db)):
    """
    Receives a message, saves it to RawLog, and returns success.
    """
    try:
        print(f"📩 Received message from {payload.source}: {payload.text}")

        # Create a new RawLog entry
        new_log = models.RawLog(
            source=payload.source,
            payload={
                "sender": payload.sender_id,
                "text": payload.text,
                "original_data": payload.raw_data
            }
        )

        # Save to Database
        db.add(new_log)
        db.commit()
        db.refresh(new_log)

        return {"status": "success", "message": "Message logged successfully"}

    except Exception as e:
        print(f"❌ Error saving message: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")