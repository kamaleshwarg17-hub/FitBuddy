# 🏋️ FitBuddy – AI Fitness Plan Generator

FitBuddy is an intelligent, full-stack web application that generates personalized 7-day workout schedules and targeted nutrition/recovery advice based on user biometric data and fitness goals. Powered by **Google Gemini 1.5 Pro** and **Gemini Flash** models with a **FastAPI** backend and **SQLite** database via SQLAlchemy.

---

## 📑 Table of Contents
- [Architecture Overview](#-architecture-overview)
- [Project Structure](#-project-structure)
- [Prerequisites](#-prerequisites)
- [VS Code Setup & Installation](#-vs-code-setup--installation)
- [Configuring Gemini API Key](#-configuring-gemini-api-key)
- [Running the Application](#-running-the-application)
- [Testing the Application](#-testing-the-application)
- [Admin Dashboard](#-admin-dashboard)
- [REST API Endpoints](#-rest-api-endpoints)

---

## 🏗️ Architecture Overview

| Component | Technology | Responsibility |
|---|---|---|
| **AI Workout Planner** | Google Gemini 1.5 Pro | Generates day-by-day 7-day periodized workout plans and handles dynamic revisions |
| **AI Nutritionist** | Google Gemini Flash | Rapid generation of goal-specific nutrient timing, protein targets, and recovery tips |
| **Backend** | FastAPI + Uvicorn | High-performance async web framework managing routes, validation, and AI orchestration |
| **Persistence** | SQLite + SQLAlchemy ORM | Relational storage for users, original workout plans, feedback, and updated plans |
| **Frontend** | Jinja2 + HTML5 + Vanilla CSS | Responsive, dark-themed fitness UI featuring glassmorphism and micro-animations |

---

## 📁 Project Structure

```
fitbuddy/
├── app/
│   ├── __init__.py               # Package initializer
│   ├── main.py                   # FastAPI initialization, static mounting & lifespan
│   ├── routes.py                 # Core routing logic (/, /generate-workout, /submit-feedback, etc.)
│   ├── models.py                 # SQLAlchemy ORM models & Pydantic validation schemas
│   ├── database.py               # Database engine, session, and CRUD operations
│   ├── gemini_generator.py       # Workout generation via Gemini 1.5 Pro
│   ├── gemini_flash_generator.py # Nutrition & recovery advice via Gemini Flash
│   └── updated_plan.py           # Plan revision loop via Gemini 1.5 Pro
├── templates/
│   ├── base.html                 # Common layout, navigation, and loading modals
│   ├── index.html                # User input form with 1-click preset profiles
│   ├── result.html               # 7-day schedule display, nutrition tip, and feedback form
│   └── all_users.html            # Admin dashboard with searchable table and audit views
├── static/
│   ├── css/
│   │   └── style.css             # Dark athletic design system with glassmorphic cards
│   ├── js/
│   │   └── main.js               # Preset loaders, clipboard copy, and dynamic search
│   └── images/
│       ├── hero-bg.jpg           # High-resolution gym background image
│       └── logo.png              # FitBuddy brand icon
├── .env                          # Local environment variables
├── .env.example                  # Environment variables template
├── requirements.txt              # Production Python dependencies
├── run.py                        # Convenience server launcher
├── test_app.py                   # Automated end-to-end test suite
└── README.md                     # Comprehensive project documentation
```

---

## ⚙️ Prerequisites

1. **Python 3.10+** (Python 3.11, 3.12, 3.13 supported)
2. **VS Code** (Visual Studio Code)
3. *(Optional)* **Google Gemini API Key** from [Google AI Studio](https://aistudio.google.com/app/apikey)  
   *(FitBuddy includes built-in offline fallbacks, so the application runs immediately even before an API key is supplied!)*

---

## 💻 VS Code Setup & Installation

### Step 1: Open the Project in VS Code
1. Launch **Visual Studio Code**.
2. Go to **File** > **Open Folder...**
3. Select the `fitbuddy` folder:
   ```
   C:\Users\LENOVO\.gemini\antigravity-ide\scratch\fitbuddy
   ```

### Step 2: Open Terminal in VS Code
Open the integrated terminal in VS Code using the shortcut:
- **Windows / Linux:** `Ctrl` + `~` (or `Terminal` > `New Terminal`)

### Step 3: Create & Activate Virtual Environment
In the VS Code terminal, execute:

```powershell
# Create virtual environment
python -m venv venv

# Activate on Windows (PowerShell)
.\venv\Scripts\Activate.ps1

# (If using Windows Command Prompt / CMD)
# .\venv\Scripts\activate.bat

# (If using macOS / Linux)
# source venv/bin/activate
```

> **Note for Windows PowerShell users:** If script execution is restricted, run:  
> `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process`

### Step 4: Install Dependencies
```powershell
pip install -r requirements.txt
```

---

## 🔑 Configuring Gemini API Key

1. Open the `.env` file in the root directory.
2. Paste your Google AI Studio API key:
   ```env
   GOOGLE_API_KEY=AIzaSyYourActualGeminiKeyHere
   PORT=8000
   HOST=127.0.0.1
   ```
3. Save the file (`Ctrl + S`).

---

## 🚀 Running the Application

You can start the server using either of the following commands:

### Method 1: Using the launcher script
```powershell
python run.py
```

### Method 2: Using Uvicorn directly with hot reload
```powershell
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Once running, navigate to:
- 🌐 **Web Application:** [http://127.0.0.1:8000](http://127.0.0.1:8000)
- 📊 **Admin Dashboard:** [http://127.0.0.1:8000/view-all-users](http://127.0.0.1:8000/view-all-users)
- 📖 **Interactive Swagger API Docs:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- 🩺 **Health Check:** [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)

---

## 🧪 Testing the Application

### 1. Automated Test Suite
Run the built-in end-to-end verification script:
```powershell
python test_app.py
```
This test automatically verifies:
- Database table creation and SQLite connection.
- 7-Day workout plan generation via `generate_workout_gemini()`.
- Nutrition & recovery tip generation via `generate_nutrition_tip_with_flash()`.
- Plan update loop via `update_workout_plan()`.
- CRUD operations (`save_user`, `save_plan`, `update_plan`, `get_all_users`, `delete_user`).

### 2. Manual User Journey in the Browser
1. Open [http://127.0.0.1:8000](http://127.0.0.1:8000).
2. Click one of the **1-Click Demo Profiles** (e.g. *💪 Hypertrophy* or *🔥 Fat Loss*) to instantly populate realistic data.
3. Click **⚡ Generate 7-Day Plan**.
4. Review your personalized Day 1 through Day 7 schedule and the Gemini Flash nutrition guidance.
5. In the **Refine Your Workout Plan with AI** box at the bottom, enter adjustments (e.g., *"Replace lunges with leg press and add 15 minutes of stairmaster on cardio days"*).
6. Click **⚡ Revise Routine with AI** to view your updated plan.
7. Click **Admin Dashboard** in the navbar to see your record stored in the database.

---

## 📋 REST API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Renders the main user input homepage |
| `POST` | `/generate-workout` | Processes user metrics and generates AI workout + nutrition plan |
| `POST` | `/submit-feedback` | Updates an existing workout plan based on athlete feedback |
| `GET` | `/view-all-users` | Administrative view of all registered users and plans |
| `POST` | `/delete-user/{user_id}` | Deletes a user and their plans |
| `GET` | `/api/users` | Returns all users and plan data as JSON |
| `GET` | `/health` | Application health and Gemini configuration status |
| `GET` | `/docs` | Interactive Swagger API documentation |
