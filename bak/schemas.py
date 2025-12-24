from pydantic import BaseModel
from typing import Optional, Dict, Any

# This defines the structure of the data we expect from the Webhook
class WebhookPayload(BaseModel):
    source: str         # e.g., "whatsapp", "telegram"
    sender_id: str      # The user's phone number
    text: str           # The message content
    raw_data: Optional[Dict[str, Any]] = None # Full original JSON (optional)

# This defines what our API sends back as a response
class WebhookResponse(BaseModel):
    status: str
    message: str