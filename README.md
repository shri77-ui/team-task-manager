# TaskFlow — Team Task Manager

A clean, beginner-friendly full-stack task management app built with Python Flask, SQLite, Bootstrap 5, Flask-Login, and SQLAlchemy.

---

## ✨ Features

| Feature | Details |
|---|---|
| 🔐 Authentication | Signup / Login with hashed passwords |
| 👥 Role-based Access | Admin can create, assign & delete tasks; Members update status |
| 📋 Task Management | Create, view, filter, and track tasks |
| 📊 Dashboard | Stats panel with completion progress bar |
| 🎨 Clean UI | Bootstrap 5 + custom sidebar layout |
| 🗄️ Database | SQLite (local) — swappable for Postgres |
| 🚀 Deployment | Ready for Railway (or Heroku) |

---

## 🗂️ Project Structure

```
team-task-manager/
├── app.py                  # Main Flask app (routes, models, auth)
├── requirements.txt        # Python dependencies
├── Procfile                # Railway/Heroku start command
├── runtime.txt             # Python version
├── README.md               # This file
└── templates/
    ├── base.html           # Shared layout (sidebar + nav)
    ├── login.html          # Login page
    ├── signup.html         # Registration page
    ├── dashboard.html      # Stats & recent tasks
    ├── tasks.html          # Filterable task list
    ├── create_task.html    # New task form (admin only)
    ├── task_detail.html    # Task view + status update
    └── members.html        # Team members list (admin only)
```

---

## 🚀 Local Setup

### 1. Clone or download the project

```bash
git clone https://github.com/your-username/team-task-manager.git
cd team-task-manager
```

### 2. Create a virtual environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the app

```bash
python app.py
```

Open **http://localhost:5000** in your browser.

### 5. Default admin credentials

```
Email:    admin@taskmanager.com
Password: admin123
```

---

## ☁️ Deploy to Railway

### Step 1 — Push to GitHub

```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/team-task-manager.git
git push -u origin main
```

### Step 2 — Create a Railway project

1. Go to [railway.app](https://railway.app) and sign in.
2. Click **New Project** → **Deploy from GitHub repo**.
3. Select your repository.
4. Railway auto-detects Python and runs `pip install -r requirements.txt`.

### Step 3 — Set environment variables

In Railway → your service → **Variables** tab, add:

| Key | Value |
|---|---|
| `SECRET_KEY` | A long random string (e.g. `openssl rand -hex 32`) |
| `PORT` | `5000` (Railway injects this automatically) |

### Step 4 — Deploy

Railway builds and deploys automatically on every `git push`. Your app is live at:

```
https://your-project-name.up.railway.app
```

### Notes

- SQLite stores `tasks.db` in the container filesystem. It resets on redeploy.
- For persistent data on Railway, add a **PostgreSQL** plugin and update:
  ```python
  # In app.py, Railway sets DATABASE_URL automatically for Postgres
  app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///tasks.db')
  ```
  Railway's Postgres URL starts with `postgresql://` — no code changes needed.

---

## 🔑 Role Permissions

| Action | Admin | Member |
|---|---|---|
| View dashboard | ✅ | ✅ |
| View own tasks | ✅ | ✅ |
| View all tasks | ✅ | ❌ |
| Create task | ✅ | ❌ |
| Update task status | ✅ | ✅ (own tasks) |
| Delete task | ✅ | ❌ |
| View members list | ✅ | ❌ |

---

## 🛠️ Tech Stack

- **Backend**: Python 3.11, Flask 3.0, SQLAlchemy 2.0
- **Auth**: Flask-Login, Werkzeug password hashing
- **Database**: SQLite (dev) / PostgreSQL (prod)
- **Frontend**: Bootstrap 5.3, Bootstrap Icons, Google Fonts
- **Server**: Gunicorn

---

## 📝 License

MIT — free to use and modify.
