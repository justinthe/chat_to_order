
### 1. User Requirements Document (URD)

**Project Name:** AI Order Manager (Telegram Edition)
**Target User:** Home Business Owner (Single User)

**1.1. Purpose**
To automate the administrative burden of recording food orders. The system acts as a virtual assistant that reads text messages from the business owner, extracts order details using AI, and automatically syncs confirmed orders to Google Calendar.

**1.2. Functional Requirements**

* **Input Channel:** The system must accept text messages via a private Telegram Bot.
* **Order Extraction (AI):** The system must use a Large Language Model (DeepSeek) to parse natural language (Indonesian) and extract:
* Item Description (e.g., "Black Forest")
* Quantity (e.g., 2)
* Price (e.g., "300rb" -> 300,000)
* Client Name (e.g., "buat Budi")
* Due Date/Time (e.g., "besok jam 5")


* **Data Storage:** All raw messages and structured orders must be saved in a PostgreSQL database for traceability.
* **Confirmation Workflow:**
* The system must not auto-book orders. It must reply with a summary and ask for confirmation.
* The user must reply "Ok" or "Yes" to finalize the order.


* **Calendar Sync:** Upon confirmation, the system must create an event in the owner's Google Calendar with the client name and order details.
* **Cancellation:** The user must be able to cancel pending orders via text.

**1.3. Non-Functional Requirements**

* **Security:** The system is for internal use only; external webhooks must be secured via token or ID checks (implicit in Telegram Bot ID).
* **Availability:** The system runs in a Docker container (local or server).
* **Performance:** AI processing should typically complete within 5-10 seconds.

---

### 2. Entity Relationship (ER) Diagram

This defines the structure of your PostgreSQL database.

**Description of Relationships:**

1. **Customer Table:** Stores the unique identity of the person chatting (in this case, mostly you, the Business Owner, or different staff members if you share the bot).
* *One Customer* can have *Many RawMessages*.
* *One Customer* can have *Many Orders*.


2. **RawMessage Table:** A log of every text sent to the bot.
* *One RawMessage* is linked to *One Customer*.


3. **Order Table:** The final processed data.
* *One Order* is linked to *One Customer*.
* *One Order* is linked to *One RawMessage* (the source text that created it).



---

### 3. Data Flow Diagram (DFD)

This illustrates the lifecycle of a message from your phone to the calendar.

**The "Confirmation Loop" Workflow:**

1. **Input:** Owner sends "Pesan 2 Kue for Budi" via Telegram.
2. **Process 1 (Ingest):** Django Webhook receives JSON -> Saves to `RawMessage` DB.
3. **Process 2 (Think):** Django sends text to **DeepSeek API**.
4. **Process 3 (Draft):** DeepSeek returns JSON -> Django creates `Order` (Status: PENDING).
5. **Output 1 (Verify):** Django sends Telegram Reply: "Confirm 2 Kue for Budi? (Yes/No)".
6. **Input 2:** Owner replies "Yes".
7. **Process 4 (Finalize):** Django detects "CONFIRM" intent -> Updates `Order` to CONFIRMED.
8. **Output 2 (Sync):** Django triggers **Google Calendar API** -> Event Created.

---

### 4. README.md

Create a file named `README.md` in the root of your project. This is the manual for you (or anyone else) to run the code.

```markdown
# AI Order Management System 🎂

A Django-based chatbot that helps home business owners manage food orders via Telegram. It uses DeepSeek LLM to parse natural language orders and syncs them to Google Calendar.

## 🏗 Tech Stack
- **Framework:** Django 5.0 (Python)
- **Database:** PostgreSQL 15
- **AI Engine:** DeepSeek V3 (via OpenAI SDK)
- **Infrastructure:** Docker & Docker Compose
- **Integrations:** Telegram Bot API, Google Calendar API

## 🚀 Installation & Setup

### 1. Prerequisites
- Docker Desktop installed.
- A Telegram Bot Token (from @BotFather).
- A DeepSeek API Key.
- A Google Cloud Service Account JSON file.

### 2. Configuration
1. Clone/Copy this project folder.
2. Place your Google credentials file in the root folder and rename it to `service_account.json`.
3. Create a `.env` file in the root folder:

```bash
# Security
SECRET_KEY=your-random-secret-key
DEBUG=1
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0

# Database
POSTGRES_DB=om_db
POSTGRES_USER=om_user
POSTGRES_PASSWORD=secret
DB_HOST=db
DB_PORT=5432

# AI Service
DEEPSEEK_API_KEY=sk-your-deepseek-key

# Integrations
TELEGRAM_BOT_TOKEN=123456:ABC-your-bot-token
CALENDAR_ID=your.email@gmail.com

```

### 3. Running the App

Start the containers in the background:

```bash
docker compose up -d

```

### 4. Database Setup (First Time Only)

Run migrations to create the database tables:

```bash
docker exec -it chat_to_order-web-1 python manage.py migrate

```

Create a superuser to access the Admin Panel:

```bash
docker exec -it chat_to_order-web-1 python manage.py createsuperuser

```

### 5. Connecting Telegram

To make your local server accessible to Telegram (for testing), use Ngrok:

```bash
ngrok http 8000

```

Then register your webhook with Telegram:
`https://api.telegram.org/bot<YOUR_TOKEN>/setWebhook?url=<YOUR_NGROK_URL>/webhooks/telegram/`

## 📖 Usage Guide

**1. Create an Order**
Send a message like:

> "Pesan 20 Lemper dan 5 Risoles buat Acara Pak Budi besok jam 3 sore, total 150rb"

**2. Review**
The bot will reply:

> 📝 **Review Order:**
> * 20x Lemper (Price: ?)
> * 5x Risoles (Price: ?)
> 👤 Client: Pak Budi
> 💰 Total: Rp 150,000
> 
> 
> Reply **'Ok'** to confirm.

**3. Confirm**
Reply with:

> "Ok"

**4. Result**
The bot confirms, and the event appears on your Google Calendar.

## 🛠 Troubleshooting

**View Logs:**

```bash
docker compose logs -f web

```

**Common Errors:**

* `Connection Refused`: Check if Docker is running.
* `AI Error`: Check your API Key balance.
* `Calendar Error`: Ensure you shared your Google Calendar with the Service Account email.

```

