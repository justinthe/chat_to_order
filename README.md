# 🤖 OrderBot Operation Manual

**Version:** 1.0 (Ngrok Deployment)

This document covers how to set up, run, and manage the AI Order Management System on your local machine using Docker and Ngrok.

---

## 1. Credentials & API Keys

Before running the bot, ensure your `.env` file contains these 4 keys.

### A. Telegram Bot Token

1. Open Telegram and search for **@BotFather**.
2. Send the command `/newbot`.
3. Follow the steps to name your bot.
4. Copy the **HTTP API Token** (looks like `123456:ABC-Def...`).

### B. DeepSeek API Key (The Brain)

1. Go to [platform.deepseek.com](https://platform.deepseek.com/).
2. Sign up/Log in.
3. Go to **API Keys** and create a new key.
4. Copy the key (starts with `sk-...`).

### C. Google Calendar ID (The Schedule)

1. This is simply your **Gmail address** (e.g., `your.bakery@gmail.com`).
2. **Important:** In Google Calendar Settings, ensure you have shared your calendar with the **Service Account Email** (found in `service_account.json`) and gave it **"Make changes to events"** permission.

### D. Google Service Account (The Robot File)

* Ensure you have the `service_account.json` file in your project root.
* If lost: Go to [Google Cloud Console](https://console.cloud.google.com/) > IAM & Admin > Service Accounts > Keys > Add Key (JSON).

---

## 2. Managing the Service (Docker)

These commands control the "Brain" and "Database" on your laptop. Run them in your project terminal.

### ➤ Start the Service

This starts the Database and the Python App in the background.

```bash
docker compose up -d --build

```

* `-d`: Detached mode (runs in background).
* `--build`: Recompiles code if you made changes.

### ➤ Stop the Service

Stops everything and shuts down the database safely.

```bash
docker compose down

```

### ➤ Check Logs (Debugging)

If the bot isn't replying, check the logs to see what's wrong.

```bash
docker compose logs -f web

```

*(Press `Ctrl+C` to exit logs)*

---

## 3. Ngrok Setup (Connecting to the Internet)

Since the bot runs on your laptop, Telegram needs a "tunnel" to reach it. We use **Ngrok** for this.

### Step A: Installation

1. Download Ngrok from [ngrok.com/download](https://ngrok.com/download).
2. Unzip the file.

### Step B: Configuration (One Time Only)

To prevent the tunnel from timing out, register your free account.

1. Log in to the Ngrok Dashboard.
2. Copy your **Authtoken**.
3. Run this command in your terminal:
```bash
ngrok config add-authtoken <YOUR_TOKEN_HERE>

```



### Step C: Start the Tunnel

Whenever you want the bot to be online, keep this terminal window **OPEN**.

```bash
ngrok http 8000

```

* **Result:** You will see a URL like `https://a1b2-c3d4.ngrok-free.app`.
* **Copy this URL.**

### Step D: Connect Telegram (The Handshake)

Every time you restart Ngrok (and get a new URL), you must tell Telegram.

1. Open your web browser.
2. Paste this link (replace the placeholders):
```text
https://api.telegram.org/bot<YOUR_BOT_TOKEN>/setWebhook?url=<YOUR_NGROK_URL>/webhooks/telegram/

```


3. **Example:**
`https://api.telegram.org/bot555:ABC/setWebhook?url=https://a1b2.ngrok-free.app/webhooks/telegram/`
4. You should see: `{"ok":true, ... "Webhook was set"}`.

---

## 4. User Command Guide

Here is the list of commands you can use in Telegram to interact with the bot.

### 📝 New Order

Just type naturally. The AI will extract Name, Item, Qty, Price, and Date.

* **Sample:** `"Bella pesan 2 tiramisu buat besok sore, harganya 150rb"`
* **Sample:** `"Order lemper 50 biji untuk lusa atas nama Budi"`

### ✅ Confirm Order

Saves the order permanently and syncs to Google Calendar.

* **Command:** `Ok [Order ID]`
* **Sample:** `"Ok 15"`
* **Sample:** `"Ok 20, 21"` (Confirming multiple)

### ❌ Cancel Order

Cancels the order and **deletes** the event from Google Calendar.

* **Command:** `Cancel [Order ID]`
* **Sample:** `"Cancel 15"`
* **Sample:** `"Batal 15"`

### 📋 Check Schedule

Shows all active (Pending & Confirmed) orders for the next 3 days.

* **Command:** `"Cek order"`
* **Variations:** `"List order"`, `"Jadwal"`, `"Show schedule"`

---

## 5. Troubleshooting Cheat Sheet

| Problem | Solution |
| --- | --- |
| **Bot not replying** | Check if Docker is running (`docker ps`) and Ngrok is running. |
| **"Invalid HTTP_HOST"** | In `settings.py`, ensure `ALLOWED_HOSTS = ['*']` and restart Docker. |
| **Calendar not syncing** | Check `docker compose logs -f web`. If it says "Forbidden", check Google Calendar sharing permissions. |
| **Ngrok URL Expired** | Restart Ngrok (`Ctrl+C` then `ngrok http 8000`), copy the new URL, and redo the "Connect Telegram" step. |