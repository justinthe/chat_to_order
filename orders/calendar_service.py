import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
from datetime import timedelta

# We look for the file in the same folder as manage.py
SCOPES = ['https://www.googleapis.com/auth/calendar']
SERVICE_ACCOUNT_FILE = 'service_account.json'

def create_calendar_event(order):

    # --- DEBUG PRINTS ---
    target_calendar = os.environ.get('CALENDAR_ID')
    print(f"DEBUG: .env variable CALENDAR_ID is: '{target_calendar}'")
    
    if not target_calendar:
        print("WARNING: No CALENDAR_ID found. Defaulting to 'primary' (The Bot's Calendar).")
        calendar_id = 'primary'
    else:
        calendar_id = target_calendar
    # --------------------

    """
    Takes an Order object and adds it to Google Calendar.
    """
    # 1. Authenticate
    if not os.path.exists(SERVICE_ACCOUNT_FILE):
        print("Error: service_account.json not found.")
        return False

    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )
    service = build('calendar', 'v3', credentials=creds)

    # 2. Prepare Event Details
    # Default to 1 hour duration
    start_time = order.due_date
    end_time = start_time + timedelta(hours=1)
    
    summary = f"Order: {order.quantity}x {order.item_description}"
    description = f"""
    Client: {order.client_name}
    Item: {order.item_description}
    Qty: {order.quantity}
    Price: Rp {order.price:,}
    """

    event = {
        # 'summary': summary,
        'summary': f"{order.client_name} - {order.item_description}",
        'description': description,
        'start': {
            'dateTime': start_time.isoformat(),
            'timeZone': 'Asia/Jakarta', # Adjust to your timezone
        },
        'end': {
            'dateTime': end_time.isoformat(),
            'timeZone': 'Asia/Jakarta',
        },
    }

    try:
        # # 3. Insert Event (using 'primary' calendar of the account shared with)
        # # We assume the user shared THEIR primary calendar with this service account
        # # In that case, we actually need to target the USER'S email calendar ID, 
        # # or easier: Put the User's Email in .env as CALENDAR_ID
        # calendar_id = os.environ.get('CALENDAR_ID', 'primary')
        
        # event = service.events().insert(calendarId=calendar_id, body=event).execute()
        # print(f"Event created: {event.get('htmlLink')}")
        # return True
        
        service = build('calendar', 'v3', credentials=creds)
        
        # Execute and GET the result
        created_event = service.events().insert(calendarId=CALENDAR_ID, body=event).execute()
        
        print(f"Event created: {created_event.get('htmlLink')}")
        
        # --- RETURN THE ID ---
        return created_event.get('id') 
        # ---------------------
        
    
    except Exception as e:
        print(f"Calendar Error: {e}")
        return False

def delete_calendar_event(event_id):
    if not event_id:
        return

    # ... Setup service (same as create) ...
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )
    service = build('calendar', 'v3', credentials=creds)
    CALENDAR_ID = os.environ.get('CALENDAR_ID', 'primary')

    try:
        service.events().delete(calendarId=CALENDAR_ID, eventId=event_id).execute()
        print(f"✅ Successfully deleted event {event_id}")
    except Exception as e:
        print(f"❌ Failed to delete event: {e}")