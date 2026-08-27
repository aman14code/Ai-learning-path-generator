# PathFinder 🚀
**AI-Powered Personalized Learning Path Recommender**

PathFinder is an intelligent learning companion built for the **HCLTech AMPlified Hackathon**. It analyzes 110,000+ course reviews across 80+ courses to generate highly personalized, structured learning roadmaps that adapt to user goals, current skills, and feedback.

## ✨ Key Features & Innovation

1. **🧠 ML-Powered Skill Gap Analysis**
   - Automatically calculates your current proficiency across 12 tech domains.
   - Compares your skills against target role requirements (e.g., Data Scientist, DevOps Engineer).
   - Visualizes your readiness with a beautiful, custom **Canvas-based Skill Radar Chart**.
   - Prescribes the exact courses needed to close your highest-priority skill gaps.

2. **🗺️ Interactive Knowledge Graph**
   - Pure JS/Canvas implementation of a force-directed graph.
   - Visually explore course dependencies and prerequisites.
   - Highlights connected learning paths when you click on a course.
   - Shows completed courses with a glowing green aura.

3. **🤖 Conversational AI Assistant**
   - Natural language interface for course recommendations and career advice.
   - Features streaming text responses and rich inline course suggestion cards.
   - Context-aware: the AI knows your goals and completed courses.

4. **🔄 Adaptive Feedback Loop**
   - After completing a course, rate its difficulty and relevance.
   - The system tracks your "Learning Velocity" (courses per week, active streaks) and adapts pacing.
   - True adaptive learning that evolves with the user.

5. **📈 Visual Learning Roadmaps**
   - Translates abstract goals into concrete, milestone-driven paths.
   - Uses DAG topological sorting to ensure prerequisites are satisfied in the correct order.
   - Visual timeline and overall progress tracking.

## 🏗️ Technical Architecture

```mermaid
graph TB
    subgraph "Frontend (React + Vite)"
        A[Landing Page] --> B[Onboarding Wizard]
        B --> C[Dashboard (Skill Radar)]
        C --> E[Learning Path]
        C --> F[AI Chat Assistant]
        C --> G[Course Catalog]
        C --> H[Knowledge Graph]
    end
    
    subgraph "Backend (FastAPI)"
        I[REST API] --> J[ML Recommendation Engine]
        I --> K[Skill Gap Analyzer]
        I --> L[Learning Path Generator]
        I --> M[Knowledge Graph Builder]
    end
    
    subgraph "AI/ML Pipeline"
        J --> O[TF-IDF Vectorizer]
        J --> P[Cosine Similarity]
        K --> Q[Skill Taxonomy Mapping]
        L --> R[DAG Topological Sort]
    end
    
    subgraph "Data Layer"
        T[(SQLite DB)] --> I
        U[110K+ Course Reviews] --> O
    end
```

## 🛠️ Tech Stack

- **Frontend**: React, Vite, CSS3 (Glassmorphism, CSS Variables, Custom Animations), HTML5 Canvas API (for Radar Chart and Knowledge Graph)
- **Backend**: Python, FastAPI, Uvicorn
- **AI/ML**: scikit-learn (TF-IDF, Cosine Similarity), NumPy, Pandas
- **Database**: SQLite (User profiles, progress tracking, learning analytics, feedback)

## 🚀 Setup & Installation

### Prerequisites
- Node.js (v18+)
- Python 3.10+

### 1. Backend Setup

```bash
cd backend
pip install -r requirements.txt
python app.py
```
*The backend server will run on http://localhost:8000.*
*Note: The ML engine pre-computes TF-IDF vectors on startup. This takes ~3 seconds.*

### 2. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```
*The frontend will run on http://localhost:5173.*

## 📊 Judging Criteria Alignment

- **Problem Understanding (20%)**: The Skill Gap Analysis engine demonstrates deep understanding by diagnosing *why* a user needs a course, rather than just recommending one blindly.
- **Functionality (25%)**: Complete end-to-end flow from onboarding to personalized paths, chat, progress tracking, and feedback.
- **AI/ML Implementation (20%)**: Efficient TF-IDF + Cosine Similarity pipeline, coupled with heuristic-based skill taxonomy mapping and DAG topological sorting for curriculum generation.
- **Innovation (15%)**: Interactive Canvas-based Knowledge Graph and Skill Radar charts provide a massive wow-factor and unique visual insight into learning.
- **User Experience (10%)**: Premium dark mode UI with glassmorphism, 3D hover effects, micro-animations, and a highly responsive layout.

---
*Built with ❤️ for the HCLTech AMPlified Hackathon.*
