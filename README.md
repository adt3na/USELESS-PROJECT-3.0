# Vadakkunokki.ai (വടക്കുനോക്കി.ai)

> **"THE AI KNOWS THE ANSWER. THE AI CHOOSES WHETHER YOU DESERVE IT."**

Vadakkunokki.ai is an interactive retro-gaming AI web application built with **FastAPI** (Python) and **React + TypeScript + Vite**. Powered by **Google Gemini**, the AI behaves like a mischievous, unpredictable, mood-driven retro-game character that intentionally ragebaits, refuses, challenges, annoys, or entertains the user before eventually providing the correct answer.

---

## 🎮 Core Gameplay & Mechanics

1. **Ask Any Question**: The user enters a question (e.g. *"What is the largest planet?"*).
2. **Authoritative Decision Engine**: Vadakkunokki evaluates the question and its mood across 8 behaviors:
   - `START_GAME`: Triggers one of 4 retro mini-games.
   - `RAGEBAIT`: Sassy, hilarious taunts refusing to do your homework.
   - `ASK_BACK`: Questions the user's secret motives.
   - `REFUSE`: Playful, witty refusal.
   - `DELETE_INPUT`: In angry mode, progressively erases user input with backspacing sounds!
   - `SILENT`: Stares blankly without an answer.
   - `ANSWER`: Direct factual response when in a rare generous mood.
3. **Original Question Preservation (FR-007)**: When a challenge is triggered, the original question is permanently preserved.
4. **Answer Unlocking (FR-013, FR-030)**: Winning the mini-game unlocks the answer. Vadakkunokki delivers a reluctant concession wrapped around Google Gemini's verified factual explanation.

---

## 🕹️ The 4 Modular Mini-Games

- **Tic-Tac-Toe**: Interactive 3×3 grid with server-side AI moves and win verification.
- **Bubble Shooter**: Canvas arcade shooter with aiming cannon, colored bubbles, timer, and score target.
- **Speed Math**: Rapid-fire arithmetic equations with server-validated answers and timer.
- **Science Quiz**: 3-question scientific gauntlet requiring a perfect 3/3 score.

---

## 🏗️ Project Architecture

```
uselessproject/
├── backend/
│   ├── config.py             # Centralized Pydantic settings
│   ├── main.py               # FastAPI application entry point
│   ├── requirements.txt      # Python dependencies
│   ├── games/                # Modular mini-game logic
│   │   ├── tic_tac_toe.py
│   │   ├── bubble_shooter.py
│   │   ├── speed_math.py
│   │   └── science_quiz.py
│   ├── models/               # Pydantic schemas (chat, games, session)
│   ├── routes/               # API endpoints (/chat, /game, /challenge, /session)
│   ├── services/             # Gemini, Mood, Personality, and Game services
│   ├── utils/                # Redacted logging & helper functions
│   └── tests/                # Comprehensive Pytest suite
│
├── frontend/
│   ├── src/
│   │   ├── components/       # VadakkunokkiAvatar, LandingView, ChatView, ExitModal
│   │   ├── components/games/ # GameModal, TicTacToe, BubbleShooter, SpeedMath, ScienceQuiz, VictoryModal
│   │   ├── services/         # API client & Web Audio 8-bit sound synthesizer
│   │   ├── App.tsx           # App root & state coordinator
│   │   └── index.css         # Custom Vanilla CSS retro-gaming design system
│   ├── package.json
│   └── vite.config.ts
│
├── run.bat                   # 1-click startup script for Windows
└── README.md
```

---

## 🚀 Quick Start Guide

### 1. Configure Environment
Open `backend/.env` and add your Google Gemini API key:
```env
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-2.5-flash
PORT=8000
DEBUG=True
```
*(Note: If no key is configured, high quality curated factual fallbacks automatically keep the game fully functional!)*

### 2. Run the App

#### Windows (One-Click)
Double click `run.bat` or run in terminal:
```cmd
run.bat
```

#### Manual Run
**Terminal 1 (Backend):**
```bash
.\.venv\Scripts\activate
python -m uvicorn backend.main:app --reload --port 8000
```

**Terminal 2 (Frontend):**
```bash
cd frontend
npm run dev
```

Visit **http://localhost:5173** in your browser!  
FastAPI Swagger Docs available at **http://127.0.0.1:8000/docs**.

---

## 🧪 Testing

Run backend tests:
```bash
.\.venv\Scripts\python -m pytest backend\tests -v
```

Build frontend production bundle:
```bash
cd frontend
npm run build
```
