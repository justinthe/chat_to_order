import json
import os
# import google.generativeai as genai
from openai import OpenAI
from django.utils import timezone

# 1. Configure Gemini
# genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))

# 1. Configure Client for DeepSeek
client = OpenAI(
    api_key=os.environ.get("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"  # <--- This connects to DeepSeek
)

# ... imports (same as before) ...
# ... client configuration (same as before) ...

def parse_order_with_ai(text_message):
    current_time = timezone.now().strftime("%Y-%m-%d %H:%M")
    
    system_prompt = f"""
    You are an Order Management Assistant.
    Current Time: {current_time}
    
    Classify the user's intent:
    1. NEW_ORDER: User is buying (e.g. "Bella pesan...", "Order 2...", "Beli...").
    2. CONFIRM: User agrees (e.g. "Ok", "Ya", "Ok 15").
    3. CANCEL: User cancels specific item (e.g. "Batal 12", "Cancel #5").
    4. LIST_ORDERS: User wants to see list (e.g. "Cek order", "List hari ini").
    5. UNKNOWN: Anything else.
    
    Structure:
    {{
        "intent": "NEW_ORDER" | "CONFIRM" | "CANCEL" | "LIST_ORDERS" | "UNKNOWN",
        "items": [
            {{ 
                "description": "kue cubit", 
                "quantity": 1, 
                "price": 100000, 
                "client_name": "Bella" 
            }}
        ],
        "due_date": "2025-12-26 09:00:00",
        "order_id": integer
    }}
    
    CRITICAL RULES:
    1. "items" MUST be a list of OBJECTS. Do NOT return a list of strings like ["kue cubit"].
    2. Client Name Extraction:
       - "Bella pesan 1 kue" -> client_name: "Bella"
       - "Pesan 1 kue buat Budi" -> client_name: "Budi"
       - If no name found, use "Owner".
    3. Price: "100k" = 100000.
    """
    try:
        # 3. Call DeepSeek
        response = client.chat.completions.create(
            model="deepseek-chat",  # This is their main V3 model
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text_message}
            ],
            temperature=0.1,
            stream=False
        )
        
        # 4. Parse Response
        ai_content = response.choices[0].message.content
        
        # Safety cleanup: sometimes AI adds ```json at the start
        clean_json = ai_content.replace("```json", "").replace("```", "").strip()
        
        parsed_data = json.loads(clean_json)
        return parsed_data

    except Exception as e:
        print(f"DeepSeek Error: {e}")
        return None

def parse_order_with_ai_gemini(text_message):
    """
    Sends the text to Google Gemini and returns a JSON object with order details.
    """
    current_time = timezone.now().strftime("%Y-%m-%d %H:%M")

    # 2. Select Model (Gemini 1.5 Flash is fast and cheap)
    # We enforce JSON output using generation_config
    model = genai.GenerativeModel(
        # "gemini-1.5-flash-001",
        "gemini-2.0-flash-001",
        generation_config={"response_mime_type": "application/json"}
    )

    # 3. The Prompt
    prompt = f"""
    You are an Order Management Assistant for a catering in Indonesia.
    Current Time: {current_time}
    
    Analyze this message: "{text_message}"
    
    Extract the order details into this JSON structure:
    {{
        "intent": "NEW_ORDER" or "CANCEL" or "UNKNOWN",
        "items": [
            {{
                "description": "item name", 
                "quantity": integer, 
                "price": integer (null if not found)
            }}
        ],
        "due_date": "YYYY-MM-DD HH:MM:SS" (Convert relative dates like 'besok' to ISO format),
        "confidence": float (0.0 to 1.0)
    }}
    
    Notes:
    - If price is in text (e.g., '50rb', '50k'), convert to number (50000).
    - If no specific time is given for a date, default to 09:00:00.
    """

    try:
        # 4. Generate Content
        response = model.generate_content(prompt)
        
        # 5. Parse Response
        # Gemini returns the text directly as JSON string
        parsed_data = json.loads(response.text)
        return parsed_data

    except Exception as e:
        print(f"Gemini Error: {e}")
        return None