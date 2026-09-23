# WhatsApp Project Tracker

A simple but powerful **WhatsApp bot** to track your personal projects and tasks.  
Built with **Python + FastAPI + WhatsApp Cloud API + SQLite**.

---

## Features

- Create, list, and delete projects
- Add tasks to projects
- Mark tasks as done / undone
- View project status and progress
- Single-user protection (only your number can interact with the bot)
- Clean and simple text commands

### Example conversation

```
You: new project Website Redesign
Bot: ✅ Project created: Website Redesign

You: add task Website Redesign | Design homepage mockup
Bot: ✅ Task added to Website Redesign:
     [1] Design homepage mockup

You: list tasks Website Redesign
Bot: *Tasks in Website Redesign:*
     ⬜ [1] Design homepage mockup

You: done 1
Bot: ✅ Task marked as done:
     [1] Design homepage mockup

You: status Website Redesign
Bot: *Project: Website Redesign*
     Status: active
     Tasks: 1/1 done (0 remaining)
```

---

## Prerequisites

1. Meta Developer account
2. WhatsApp Business App already created
3. Permanent Access Token
4. Phone Number ID
5. A publicly reachable HTTPS URL (use [ngrok](https://ngrok.com/) while developing)

---

## Quick Start

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/whatsapp-project-tracker.git
cd whatsapp-project-tracker
```

### 2. Create virtual environment & install dependencies

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configure environment variables

```bash
cp .env.example .env
```

Edit the `.env` file:

```env
WHATSAPP_TOKEN=EAAxxxxxxx...                    # Your permanent access token
WHATSAPP_PHONE_NUMBER_ID=123456789012345        # Phone Number ID from Meta
WHATSAPP_VERIFY_TOKEN=my_secret_verify_token    # Any random string you invent
ALLOWED_PHONE_NUMBER=15551234567                # Your WhatsApp number (country code, no + or spaces)
DATABASE_URL=sqlite+aiosqlite:///./projects.db
```

### 4. Run the bot locally

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 5. Expose with ngrok (for development)

```bash
ngrok http 8000
```

Copy the HTTPS URL (example: `https://abc123.ngrok-free.app`).

### 6. Configure the Webhook in Meta

1. Go to your **WhatsApp Business App** → **Configuration** → **Webhook**
2. **Callback URL**: `https://your-ngrok-url.ngrok-free.app/webhook`
3. **Verify token**: the same value you put in `WHATSAPP_VERIFY_TOKEN`
4. Subscribe to the **messages** field

### 7. Start chatting

Open WhatsApp and send a message to your business number:

```
help
```

---

## Available Commands

| Command                        | Description                          |
|--------------------------------|--------------------------------------|
| `new project <name>`           | Create a new project                 |
| `list projects`                | Show all your projects               |
| `status <project>`             | Project overview + task list         |
| `add task <project> \| <task>` | Add a task to a project              |
| `list tasks <project>`         | List all tasks in a project          |
| `done <task_id>`               | Mark a task as completed             |
| `undone <task_id>`             | Reopen a completed task              |
| `delete project <name>`        | Delete a project and all its tasks   |
| `help`                         | Show help message                    |

---

## Project Structure

```
whatsapp-project-tracker/
├── app/
│   ├── main.py          # FastAPI application + webhook endpoints
│   ├── config.py        # Settings loaded from .env
│   ├── database.py      # Async SQLAlchemy setup
│   ├── models.py        # Project & Task database models
│   ├── handlers.py      # Command parsing and business logic
│   └── whatsapp.py      # WhatsApp Cloud API client
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

---

## Deploying to Production

You can deploy this bot easily on:

- [Railway](https://railway.app/)
- [Render](https://render.com/)
- [Fly.io](https://fly.io/)

Just set the same environment variables and update the webhook URL in Meta to your production domain.

---

## Roadmap (ideas for future versions)

- Due dates and reminders
- Daily / weekly summary messages
- Project progress percentage
- Multiple task status (todo, in-progress, blocked, done)
- Simple export of project summary

---

Made for personal productivity.
