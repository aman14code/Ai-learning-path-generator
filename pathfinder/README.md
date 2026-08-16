# PathFinder - AI-Powered Personalized Learning Path Recommender

PathFinder is an intelligent learning assistant designed for the HCL Simplified Hackathon. It generates personalized learning roadmaps based on a learner's profile, goals, and interests, leveraging an ML recommendation engine trained on 110,000+ course reviews across 80 unique courses.

## Features
- **Conversational Onboarding:** Seamlessly capture user experience level, interests, and career goals.
- **AI Recommendation Engine:** TF-IDF + Logistic Regression ensemble provides highly accurate, personalized course recommendations with explanations.
- **Personalized Learning Paths:** Automatically generates structured roadmaps with prerequisites and milestones based on topological sorting of a course graph.
- **AI Chat Assistant:** Conversational agent that answers course-related queries, compares options, and provides study tips.
- **Progress Dashboard:** Visual skill mapping, progress tracking, and personalized recommendations.

## System Architecture
- **Frontend:** React + Vite (Fast development, component-based UI)
- **Backend:** FastAPI (High-performance Python backend)
- **ML Engine:** scikit-learn (TF-IDF vectorization, pre-computed course profiles for fast <50ms inference)
- **Database:** SQLite (Zero-config embedded database)

## Local Setup & Execution Instructions

### Prerequisites
- Python 3.9+
- Node.js 18+

### 1. Backend Setup (FastAPI & ML Engine)
Open a terminal and navigate to the `backend` directory:
```bash
cd pathfinder/backend
```

Install the Python dependencies:
```bash
pip install -r requirements.txt
```

Start the FastAPI server:
```bash
python app.py
```
*The backend will be available at http://localhost:8000*

### 2. Frontend Setup (React & Vite)
Open a new terminal and navigate to the `frontend` directory:
```bash
cd pathfinder/frontend
```

Install the Node dependencies:
```bash
npm install
```

Start the Vite development server:
```bash
npm run dev
```
*The frontend will be available at http://localhost:5173*

## Usage Guide
1. Open `http://localhost:5173` in your browser.
2. Click **"Get Started Free"** on the landing page.
3. Complete the onboarding flow (enter name, select goal, experience level, and interests).
4. View your personalized **Dashboard** with AI recommendations.
5. Navigate to **Learning Path** to see your structured milestone roadmap. Click "Start" and "Done" on courses to track progress.
6. Visit the **AI Assistant** tab to ask questions like "Compare React and Angular" or "What should I learn for Data Science?".
7. Explore the **Courses** tab to browse the entire catalog of 80 courses.
