# 🚀 StudyPilot — VS Code Quickstart & Run Guide

Welcome to **StudyPilot**! This guide walks you through opening and running the full-stack application in Visual Studio Code.

---

## ⚡ Fastest Way to Run (1-Click)

1. Extract the `studypilot.zip` archive into any folder (e.g. `C:\Users\YourName\studypilot`).
2. Double-click **`start.bat`** (or in VS Code terminal, run `.\start.bat` or `.\start.ps1`).
3. This will automatically:
   - Start the **FastAPI backend** on `http://localhost:8000`
   - Start the **React/Vite frontend** on `http://localhost:5173`
   - Open your browser to `http://localhost:5173`

---

## 💻 Running in VS Code Step-by-Step

### 1. Open the Project in VS Code
Open VS Code and choose **File > Open Folder...**, then select the `studypilot` directory.

### 2. Run via VS Code Tasks (Built-in)
We've included pre-configured VS Code tasks in `.vscode/tasks.json`:
- Press `Ctrl + Shift + B` to trigger **Start Full Stack (Backend + Frontend)**.
- Or press `Ctrl + Shift + P` -> type `Tasks: Run Task` -> choose:
  - `Start Full Stack (Backend + Frontend)`
  - `Run Backend (FastAPI)`
  - `Run Frontend (Vite)`
  - `Run Backend Tests`

---

## 🛠️ Manual Terminal Commands

If you prefer running commands manually in VS Code integrated terminals:

### Terminal 1: Backend (FastAPI)
```powershell
cd backend

# If using existing virtual environment:
.\.venv\Scripts\python -m uvicorn app.main:app --reload --port 8000

# Or if setting up from scratch on a new machine:
python -m venv .venv
.\.venv\Scripts\pip install -r requirements.txt
.\.venv\Scripts\python -m uvicorn app.main:app --reload --port 8000
```
Backend API will be live at: **`http://localhost:8000`**  
Interactive API Docs (Swagger): **`http://localhost:8000/docs`**

### Terminal 2: Frontend (React / Vite)
```powershell
cd frontend

# Run dev server:
npm run dev
```
Frontend Web App will be live at: **`http://localhost:5173`**

---

## 🔑 Login Credentials

The database is pre-seeded with ready-to-use demo accounts:

- **Email:** `demo@studypilot.io`
- **Password:** `StudyPilot2026!`

Or click **Register** to create a fresh student account.

---

## 🧠 AI Tutor Features & Configuration

### 1. Offline Mode (No API Key Required!)
Out-of-the-box, the AI Tutor is powered by an enhanced academic knowledge engine that runs **100% offline**:
- Deep explanations for Biology (Mitosis, Meiosis, Photosynthesis, Cellular Respiration, DNA, Enzymes, etc.)
- Physics (Newton's Laws, Ohm's Law, Circuits, Energy, Waves, etc.)
- Chemistry (Acids & Bases, Chemical bonding, Stoichiometry, Thermodynamics, etc.)
- Mathematics (Calculus, Derivatives, Integrals, Quadratic equations, etc.)
- Computer Science (Python, Recursion, OOP, Big-O, Data structures, etc.)
- Dynamic pedagogical breakdown for any custom concept or question
- Mini-Quiz ("Check My Understanding") that tests your knowledge with targeted questions

### 2. Using Live AI Models (Optional Free Keys)
To connect real AI models, open **`backend/.env`** and configure your provider:

#### Option A: Google Gemini (Free API Key)
1. Get a free API key at [Google AI Studio](https://aistudio.google.com/)
2. In `backend/.env`:
```env
LLM_PROVIDER="gemini"
GEMINI_API_KEY="your-gemini-api-key-here"
GEMINI_MODEL="gemini-1.5-flash"
```

#### Option B: Groq (Ultra-Fast Free Tier)
1. Get a free API key at [Groq Console](https://console.groq.com/)
2. In `backend/.env`:
```env
LLM_PROVIDER="groq"
GROQ_API_KEY="your-groq-api-key-here"
GROQ_MODEL="llama-3.3-70b-versatile"
```

#### Option C: OpenAI
In `backend/.env`:
```env
LLM_PROVIDER="openai"
OPENAI_API_KEY="your-openai-api-key-here"
OPENAI_MODEL="gpt-4o-mini"
```

---

## 🧪 Running Automated Tests

To verify the entire system:
```powershell
cd backend
.\.venv\Scripts\python test_full_system_verification.py
.\.venv\Scripts\python -m pytest tests/
```
All 46 test cases and the 14-step end-to-end integration flow will pass with 100% success!
