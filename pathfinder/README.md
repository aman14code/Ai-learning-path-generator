# 🧭 PathFinder — AI-Powered Personalized Learning Path Recommender

An intelligent learning assistant that recommends personalized learning paths based on a learner's interests, goals, previous learning history and skill level.

## 🚀 Live Demo

- **Frontend:** [https://ai-learning-path-generator-five.vercel.app](https://ai-learning-path-generator-five.vercel.app)
- **Backend API:** Deployed on Render

## 🏗️ Architecture

```
pathfinder/
├── frontend/          # React + Vite (deployed on Vercel)
│   ├── src/
│   │   ├── pages/     # Dashboard, Chat, LearningPath, Courses, SkillGraph, Leaderboard
│   │   ├── api.js     # API client
│   │   └── App.jsx    # Main app with routing
│   └── package.json
├── backend/           # FastAPI + Python (deployed on Render)
│   ├── app.py         # REST API endpoints
│   ├── ml_engine.py   # TF-IDF + Ensemble SVM recommendation engine
│   ├── learning_paths.py  # Course graph + career path generator
│   ├── database.py    # User profiles, progress tracking
│   ├── train_and_save_model.py  # ML model training script
│   └── data/
│       ├── train.csv          # Training dataset (course reviews)
│       └── ultimate_model.pkl # Trained ensemble model
└── README.md
```

## 🤖 AI/ML Techniques

### Ensemble Model Architecture
- **TF-IDF Vectorizer (Word-level):** 80,000 features, (1,3)-gram, sublinear TF
- **TF-IDF Vectorizer (Char-level):** 60,000 features, (3,6)-gram char_wb
- **LogisticRegression (Word):** C=2.0, trained on word-level features
- **LogisticRegression (Char):** C=2.0, trained on char-level features
- **LinearSVC (Combo):** Calibrated SVM on concatenated word+char features
- **Ensemble Fusion:** Weighted probability averaging (3.0×LR_word + 2.5×LR_char + 2.0×SVC) / 7.5

### Additional AI Components
- **Skill Gap Analysis:** Weighted proficiency scoring per domain with role-based requirements
- **Knowledge Graph:** Prerequisite-based course graph with topological ordering
- **Learning Velocity:** Adaptive pacing based on completion patterns
- **Explainable AI:** Each recommendation includes a human-readable explanation

## 🏛️ Architecture & ML Design Decisions (For Judges)

### Why Ensemble SVM instead of Generative LLMs?
While Large Language Models (LLMs) are popular, we deliberately chose an **Ensemble TF-IDF + SVM** architecture for the core recommendation engine because:
1. **Deterministic Accuracy:** Our model consistently maps specific user keywords to exact course profiles without the hallucination risks of generative models.
2. **Latency & Performance:** Our ensemble runs locally in milliseconds, avoiding the 2-5 second network latency of third-party LLM APIs.
3. **Cost Efficiency:** It requires zero API credits to run at scale, making this a truly self-contained, production-ready solution.

### Future Scaling to Microservices
Currently built as a monolithic FastAPI application for rapid hackathon iteration, the architecture is designed to be easily decoupled into microservices:
- **Auth & Profile Service** (Node.js/Express)
- **Recommendation Engine Service** (Python/FastAPI - containing the ML model)
- **Progress Tracking & Analytics Service** (Go/Rust for high throughput)
This separation of concerns will allow the heavy ML processes to scale independently from web traffic.

## ✨ Key Features

1. **Conversational AI Assistant** — Natural language interface with streaming responses
2. **Personalized Learning Paths** — ML-powered roadmaps with milestones and prerequisites
3. **Skill Gap Analysis** — Identify weaknesses against target career requirements
4. **Interactive Knowledge Graph** — Force-directed visualization of course relationships
5. **Voice Input** — Web Speech API integration for hands-free interaction
6. **GitHub-Style Activity Heatmap** — Visual consistency tracking
7. **Global Leaderboard** — Gamified learning with badges and rankings
8. **Adaptive Feedback System** — Difficulty and relevance ratings per course
9. **Certificate of Completion** — Generated upon finishing a learning path
10. **Progress Dashboard** — Real-time stats, skill distribution, learning velocity

## 🛠️ Setup & Execution

### Prerequisites
- Python 3.10+
- Node.js 18+
- pip

### Backend Setup
```bash
cd pathfinder/backend
pip install -r requirements.txt
python train_and_save_model.py    # Train the ML model
python -m uvicorn app:app --host 0.0.0.0 --port 8000
```

### Frontend Setup
```bash
cd pathfinder/frontend
npm install
npm run dev
```

The frontend runs on `http://localhost:5173` and the backend on `http://localhost:8000`.

## 📊 Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 19, Vite, React Router, React Force Graph |
| Backend | FastAPI, Uvicorn, Python |
| ML/AI | scikit-learn, TF-IDF, SVM, Logistic Regression |
| Data | pandas, numpy, scipy |
| Deployment | Vercel (frontend), Render (backend) |

## 👥 Team

Built for HCL Simplified Hackathon 2026
