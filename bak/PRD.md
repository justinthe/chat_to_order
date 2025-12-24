# PRD: Home Business Chat Order Manager

## 1. Executive Summary
A middleware application that automates order tracking for home-based business owners. It ingests raw order text from chat apps (WhatsApp/Telegram), parses structured data (items, price, address), saves it to a database, and creates a Google Calendar event for the delivery/pickup time.

## 2. User Stories
* **Ingestion:** As a business owner, I can forward a customer's chat message to the bot.
* **Parsing:** The system automatically extracts: Customer Name, Items Ordered, Total Price, Delivery Address, and Date/Time.
* **Confirmation:** The bot replies with a summary: "Order #101 created for [Name]. Delivery on [Date]. Value: $[Price]."
* **Calendar Sync:** The system adds an event to my Google Calendar: "Deliver Order #101 ([Items]) to [Address]" at the specified time.
* **Cancellation:** As a business owner, I can reply "Cancel Order #101", and the system will:
    1.  Mark the database record as 'Cancelled'.
    2.  Remove or update the Google Calendar event.
    3.  Confirm cancellation via chat.

## 3. Functional Requirements
### A. Input (Chat Webhook)
* Accept text via Webhook (initially simulating WhatsApp/Telegram payloads).
* Log raw text immediately for audit.

### B. The Brain (LLM Parser)
* Since order formats vary (e.g., "I want 2 cakes for next Friday" vs "Order: 2x Chocolate Cake, $50, Send to 123 Main St, Dec 25th"), we will use an LLM (e.g., OpenAI API or local equivalent) to extract structured JSON.
* **Required Fields to Extract:**
    * `customer_name` (String)
    * `order_items` (String/List)
    * `total_price` (Decimal/Float)
    * `delivery_address` (String)
    * `due_datetime` (ISO 8601 Timestamp)

### C. Database (Order Management)
* Must store orders with a unique, human-readable ID (e.g., #100, #101).
* Must track status: `ACTIVE`, `CANCELLED`, `COMPLETED`.

### D. Calendar Integration
* Create event on `due_datetime`.
* Description must include the full order details.
* If status changes to `CANCELLED`, delete the calendar event.