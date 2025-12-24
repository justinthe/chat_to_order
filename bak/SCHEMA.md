# Database Schema Strategy

## 1. Table: `raw_logs`
*Purpose: Audit trail. Never delete anything from here.*
* `id`: UUID (Primary Key)
* `source`: String (e.g., "whatsapp", "telegram")
* `payload`: JSONB (The full webhook data)
* `created_at`: Timestamp

## 2. Table: `customers` (Optional but recommended)
*Purpose: To remember repeat clients.*
* `id`: Integer (Primary Key)
* `name`: String
* `phone_number`: String (Unique, Indexed)
* `default_address`: Text

## 3. Table: `orders`
*Purpose: The core business logic.*
* `id`: Integer (Primary Key, Auto-increment - serves as Order #)
* `raw_log_id`: UUID (Foreign Key to `raw_logs`)
* `customer_id`: Integer (Foreign Key to `customers`, nullable)
* `items_summary`: Text (e.g., "2x Cheesecake, 1x Brownie")
* `total_price`: Decimal(10, 2)
* `delivery_address`: Text
* `due_datetime`: Timestamp
* `calendar_event_id`: String (Stores the Google Calendar Event ID so we can delete it later)
* `status`: Enum ('ACTIVE', 'CANCELLED', 'COMPLETED')
* `created_at`: Timestamp