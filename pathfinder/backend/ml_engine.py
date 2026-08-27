"""
PathFinder ML Recommendation Engine
Uses TF-IDF + course profiles for fast inference.
No heavy classifier training at startup - pre-computes course embeddings instead.
Includes Skill Gap Analysis and Adaptive Learning capabilities.
"""
import pandas as pd
import numpy as np
import re
import os
import pickle
from collections import Counter
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import normalize

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")


def clean_text(text):
    """Clean and normalize text for NLP processing."""
    if pd.isna(text) or not text:
        return ""
    text = str(text).lower()
    text = re.sub(r"http\S+|www\S+|\S+@\S+", " ", text)
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


# ============================================================================
# SKILL TAXONOMY — Maps domains to granular skills with proficiency weights
# This is the backbone of the Skill Gap Analysis engine
# ============================================================================
SKILL_TAXONOMY = {
    "Python": {
        "skills": ["variables", "loops", "functions", "data types", "file handling",
                   "error handling", "modules", "libraries", "classes", "inheritance",
                   "decorators", "generators", "context managers", "metaclasses",
                   "automation", "web scraping", "numpy", "pandas", "matplotlib", "jupyter"],
        "weight": 1.0,
    },
    "Web Development": {
        "skills": ["html", "css", "javascript", "dom", "events", "responsive design",
                   "react", "angular", "vue", "node.js", "express", "api design",
                   "rest", "graphql", "typescript", "full stack", "authentication"],
        "weight": 1.0,
    },
    "Data Science": {
        "skills": ["data analysis", "pandas", "visualization", "matplotlib", "statistics",
                   "probability", "distributions", "hypothesis testing", "regression",
                   "excel", "tableau", "power bi", "exploratory analysis", "data cleaning",
                   "time series", "forecasting", "r programming"],
        "weight": 1.0,
    },
    "Machine Learning": {
        "skills": ["supervised learning", "unsupervised learning", "classification",
                   "regression", "decision trees", "random forest", "svm", "clustering",
                   "dimensionality reduction", "feature engineering", "cross validation",
                   "neural networks", "deep learning", "tensorflow", "pytorch", "cnn",
                   "nlp", "computer vision", "transformers", "generative ai", "mlops",
                   "reinforcement learning", "transfer learning"],
        "weight": 1.2,
    },
    "Database": {
        "skills": ["sql", "joins", "aggregation", "indexing", "query optimization",
                   "schema design", "normalization", "postgresql", "mongodb", "redis",
                   "caching", "data warehouse", "etl"],
        "weight": 0.9,
    },
    "Cloud & DevOps": {
        "skills": ["linux", "bash", "git", "docker", "kubernetes", "ci/cd",
                   "aws", "azure", "gcp", "monitoring", "infrastructure as code",
                   "deployment", "containerization"],
        "weight": 0.9,
    },
    "Mobile Development": {
        "skills": ["react native", "flutter", "android", "ios", "swift",
                   "mobile ui", "navigation", "state management"],
        "weight": 0.8,
    },
    "Security": {
        "skills": ["network security", "encryption", "firewalls", "penetration testing",
                   "vulnerability scanning", "ethical hacking", "risk assessment"],
        "weight": 0.8,
    },
    "Mathematics": {
        "skills": ["linear algebra", "vectors", "matrices", "calculus", "derivatives",
                   "gradients", "optimization", "probability theory"],
        "weight": 0.7,
    },
}

# Maps career roles to required skill domains with target proficiency (0-100)
ROLE_SKILL_REQUIREMENTS = {
    "Data Scientist": {
        "Python": 85, "Data Science": 95, "Machine Learning": 80,
        "Mathematics": 70, "Database": 60,
    },
    "Full Stack Web Developer": {
        "Web Development": 95, "Database": 75, "Cloud & DevOps": 60,
        "Python": 40,
    },
    "Machine Learning Engineer": {
        "Python": 90, "Machine Learning": 95, "Mathematics": 80,
        "Cloud & DevOps": 65, "Data Science": 60,
    },
    "DevOps Engineer": {
        "Cloud & DevOps": 95, "Python": 60, "Database": 55,
        "Security": 50,
    },
    "Mobile App Developer": {
        "Mobile Development": 90, "Web Development": 70, "Database": 50,
        "Cloud & DevOps": 40,
    },
    "Data Engineer": {
        "Database": 90, "Python": 80, "Cloud & DevOps": 70,
        "Data Science": 60,
    },
    "AI/GenAI Specialist": {
        "Machine Learning": 95, "Python": 85, "Mathematics": 75,
        "Data Science": 65, "Cloud & DevOps": 50,
    },
    "Cybersecurity Analyst": {
        "Security": 90, "Cloud & DevOps": 70, "Python": 55,
        "Database": 45,
    },
}


class RecommendationEngine:
    """AI-powered course recommendation engine with skill gap analysis."""

    def __init__(self):
        self.courses = []
        self.course_profiles = {}
        self.vectorizer = None
        self.course_vectors = None
        self.course_names = []
        self.course_metadata = {}
        self.keyword_map = {}
        self._loaded = False

    def load(self, train_path=None):
        """Load training data and build course profiles."""
        if self._loaded:
            return

        # Find training data
        if train_path is None:
            search_paths = [
                os.path.join(DATA_DIR, "train.csv"),
                r"C:\Users\amans\Downloads\train.csv",
                r"C:\Users\amans\OneDrive\Desktop\train.csv",
            ]
            for p in search_paths:
                if os.path.exists(p) and os.path.getsize(p) > 1000:
                    train_path = p
                    break

        if train_path is None:
            raise FileNotFoundError("Cannot find train.csv")

        print(f"[ML Engine] Loading data from {train_path}...")
        df = pd.read_csv(train_path)
        df["clean"] = df["Reviews"].apply(clean_text)

        self.course_names = sorted(df["Course"].unique().tolist())
        self.courses = self.course_names

        # Build TF-IDF vectorizer on all reviews
        print("[ML Engine] Building TF-IDF vectorizer...")
        self.vectorizer = TfidfVectorizer(
            max_features=30000,
            ngram_range=(1, 2),
            min_df=2,
            max_df=0.95,
            stop_words="english",
            sublinear_tf=True,
        )
        all_reviews = df["clean"].tolist()
        tfidf_matrix = self.vectorizer.fit_transform(all_reviews)

        # Compute course profile vectors (mean of all reviews per course)
        print("[ML Engine] Computing course profiles...")
        course_vectors = []
        for course in self.course_names:
            mask = df["Course"] == course
            course_mat = tfidf_matrix[mask.values]
            profile = course_mat.mean(axis=0).A1
            course_vectors.append(profile)

        self.course_vectors = normalize(np.array(course_vectors))

        # Extract top keywords per course for explanations
        feature_names = self.vectorizer.get_feature_names_out()
        for i, course in enumerate(self.course_names):
            top_indices = np.argsort(-self.course_vectors[i])[:20]
            self.keyword_map[course] = [feature_names[j] for j in top_indices]

        # Build course metadata
        for course in self.course_names:
            course_df = df[df["Course"] == course]
            self.course_metadata[course] = {
                "name": course,
                "num_reviews": len(course_df),
                "sample_reviews": course_df["Reviews"].head(3).tolist(),
                "keywords": self.keyword_map[course][:10],
                "domain": self._classify_domain(course),
                "difficulty": self._estimate_difficulty(course),
            }

        self._loaded = True
        print(f"[ML Engine] Ready! {len(self.course_names)} courses loaded.")

    def recommend_courses(self, user_text, top_k=10, excluded_courses=None):
        """Recommend courses based on user text input."""
        if not self._loaded:
            self.load()

        cleaned = clean_text(user_text)
        if not cleaned:
            return []

        # Vectorize user input
        user_vec = self.vectorizer.transform([cleaned])
        user_vec_norm = normalize(user_vec).toarray().flatten()

        # Compute similarity with all course profiles
        similarities = self.course_vectors @ user_vec_norm

        # Rank courses
        ranked_indices = np.argsort(-similarities)
        results = []
        for idx in ranked_indices:
            course = self.course_names[idx]
            if excluded_courses and course in excluded_courses:
                continue
            score = float(similarities[idx])
            if score < 0.01:
                continue

            # Generate explanation
            explanation = self._generate_explanation(user_text, course, score)

            results.append({
                "course": course,
                "score": round(score, 4),
                "explanation": explanation,
                "domain": self.course_metadata[course]["domain"],
                "difficulty": self.course_metadata[course]["difficulty"],
                "keywords": self.course_metadata[course]["keywords"][:5],
            })

            if len(results) >= top_k:
                break

        return results

    def recommend_for_goal(self, goal, experience_level="beginner", interests=None):
        """Recommend a structured learning path for a career goal."""
        if not self._loaded:
            self.load()

        # Combine goal + interests into search text
        search_text = goal
        if interests:
            search_text += " " + " ".join(interests)

        # Get all relevant courses
        all_recs = self.recommend_courses(search_text, top_k=30)

        # Filter by difficulty based on experience
        if experience_level == "beginner":
            priority_order = ["Beginner", "Intermediate", "Advanced"]
        elif experience_level == "intermediate":
            priority_order = ["Intermediate", "Advanced", "Beginner"]
        else:
            priority_order = ["Advanced", "Intermediate", "Beginner"]

        # Sort by priority then score
        def sort_key(r):
            try:
                diff_rank = priority_order.index(r["difficulty"])
            except ValueError:
                diff_rank = 3
            return (diff_rank, -r["score"])

        sorted_recs = sorted(all_recs, key=sort_key)
        return sorted_recs[:15]

    def get_course_info(self, course_name):
        """Get detailed information about a course."""
        if course_name in self.course_metadata:
            return self.course_metadata[course_name]
        return None

    def get_all_courses(self):
        """Get all available courses with metadata."""
        return [self.course_metadata[c] for c in self.course_names]

    # ========================================================================
    # SKILL GAP ANALYSIS — The core differentiator
    # ========================================================================

    def analyze_skill_gaps(self, completed_courses, target_role, course_graph=None):
        """
        Analyze skill gaps between a learner's current competencies and a target role.

        Returns:
            dict with:
            - current_skills: {domain: proficiency%} — what the user knows
            - required_skills: {domain: proficiency%} — what the role needs
            - skill_gaps: {domain: gap_score} — where the user falls short
            - gap_courses: [{course, domain, gap_it_fills, priority}] — courses to close gaps
            - overall_readiness: float 0-100 — how ready the user is for the role
            - strengths: list — domains where user exceeds requirements
            - weaknesses: list — domains with largest gaps
        """
        if course_graph is None:
            from learning_paths import COURSE_GRAPH
            course_graph = COURSE_GRAPH

        # 1. Calculate current skill proficiency per domain
        current_skills = {}
        completed_set = set(completed_courses or [])

        for domain in SKILL_TAXONOMY:
            domain_courses = [
                name for name, info in course_graph.items()
                if info.get("domain", "") == domain
            ]
            if not domain_courses:
                current_skills[domain] = 0
                continue

            completed_in_domain = [c for c in domain_courses if c in completed_set]
            # Proficiency = weighted by difficulty (advanced courses count more)
            total_weight = 0
            earned_weight = 0
            for c in domain_courses:
                diff = course_graph.get(c, {}).get("difficulty", 2)
                weight = diff * 1.5  # Advanced courses contribute more
                total_weight += weight
                if c in completed_set:
                    earned_weight += weight

            proficiency = (earned_weight / total_weight * 100) if total_weight > 0 else 0
            current_skills[domain] = round(min(100, proficiency), 1)

        # 2. Get required skills for the target role
        required_skills = ROLE_SKILL_REQUIREMENTS.get(target_role, {})
        if not required_skills:
            # Try fuzzy matching
            target_lower = target_role.lower()
            for role, reqs in ROLE_SKILL_REQUIREMENTS.items():
                if any(word in role.lower() for word in target_lower.split()):
                    required_skills = reqs
                    target_role = role
                    break

        if not required_skills:
            # Default: balanced requirements
            required_skills = {d: 50 for d in SKILL_TAXONOMY}

        # 3. Calculate skill gaps
        skill_gaps = {}
        for domain, required in required_skills.items():
            current = current_skills.get(domain, 0)
            gap = max(0, required - current)
            skill_gaps[domain] = round(gap, 1)

        # 4. Find courses to close gaps, prioritized by gap size
        gap_courses = []
        for domain, gap in sorted(skill_gaps.items(), key=lambda x: -x[1]):
            if gap <= 0:
                continue
            # Find uncompleted courses in this domain
            domain_courses = [
                (name, info) for name, info in course_graph.items()
                if info.get("domain", "") == domain and name not in completed_set
            ]
            # Sort by difficulty (teach fundamentals first)
            domain_courses.sort(key=lambda x: x[1].get("difficulty", 2))

            for name, info in domain_courses[:3]:  # Top 3 per gap domain
                gap_courses.append({
                    "course": name,
                    "domain": domain,
                    "difficulty": {1: "Beginner", 2: "Intermediate", 3: "Advanced"}.get(
                        info.get("difficulty", 2), "Intermediate"
                    ),
                    "gap_it_fills": round(gap, 1),
                    "priority": "high" if gap > 50 else "medium" if gap > 25 else "low",
                    "skills": info.get("skills", [])[:4],
                    "hours": info.get("duration_hours", 20),
                })

        # 5. Calculate overall readiness
        total_required = sum(required_skills.values())
        total_current = sum(min(current_skills.get(d, 0), r) for d, r in required_skills.items())
        overall_readiness = (total_current / total_required * 100) if total_required > 0 else 0

        # 6. Identify strengths and weaknesses
        strengths = [d for d in required_skills if current_skills.get(d, 0) >= required_skills[d]]
        weaknesses = sorted(
            [(d, skill_gaps[d]) for d in skill_gaps if skill_gaps[d] > 10],
            key=lambda x: -x[1]
        )

        return {
            "target_role": target_role,
            "current_skills": current_skills,
            "required_skills": required_skills,
            "skill_gaps": skill_gaps,
            "gap_courses": gap_courses[:10],
            "overall_readiness": round(overall_readiness, 1),
            "strengths": strengths,
            "weaknesses": [{"domain": d, "gap": g} for d, g in weaknesses[:5]],
            "total_domains_analyzed": len(required_skills),
        }

    def get_learning_velocity(self, progress_data, analytics_data):
        """
        Calculate learning velocity metrics for adaptive pacing.

        Returns metrics like:
        - courses_per_week: average completion rate
        - current_streak: consecutive days with activity
        - estimated_completion: weeks to finish current path
        - pace_label: "fast" | "steady" | "slow"
        """
        if not progress_data:
            return {
                "courses_per_week": 0,
                "current_streak": 0,
                "estimated_completion": 0,
                "pace_label": "getting_started",
                "total_active_days": 0,
            }

        # Calculate completion rate
        completed = [p for p in progress_data if p.get("status") == "completed"]
        if not completed:
            return {
                "courses_per_week": 0,
                "current_streak": 0,
                "estimated_completion": 0,
                "pace_label": "getting_started",
                "total_active_days": len(analytics_data),
            }

        # Parse dates
        from datetime import datetime, timedelta
        dates_active = set()
        for a in analytics_data:
            dates_active.add(a.get("date", ""))

        # Streak calculation
        today = datetime.now().strftime("%Y-%m-%d")
        streak = 0
        d = datetime.now()
        for _ in range(365):
            if d.strftime("%Y-%m-%d") in dates_active:
                streak += 1
                d -= timedelta(days=1)
            else:
                break

        # Pace
        total_weeks = max(1, len(dates_active) / 7)
        courses_per_week = len(completed) / total_weeks

        if courses_per_week >= 3:
            pace = "fast"
        elif courses_per_week >= 1:
            pace = "steady"
        else:
            pace = "slow"

        return {
            "courses_per_week": round(courses_per_week, 1),
            "current_streak": streak,
            "estimated_completion": 0,  # Calculated by frontend based on remaining courses
            "pace_label": pace,
            "total_active_days": len(dates_active),
        }

    # ========================================================================
    # CHAT / Q&A
    # ========================================================================

    def answer_question(self, question, user_context=None):
        """Answer a learner's question using the knowledge base."""
        cleaned = clean_text(question)

        # Check for course-specific questions
        mentioned_courses = []
        for course in self.course_names:
            if clean_text(course) in cleaned:
                mentioned_courses.append(course)

        if mentioned_courses:
            course = mentioned_courses[0]
            info = self.course_metadata[course]
            response_text = (
                f"**{course}** is a {info['difficulty'].lower()}-level course "
                f"in the {info['domain']} domain. It covers topics like "
                f"{', '.join(info['keywords'][:5])}. "
                f"Based on {info['num_reviews']} learner reviews, it's a "
                f"well-structured course for building practical skills."
            )
            # Add personalized context
            if user_context and user_context.get("goals"):
                response_text += (
                    f"\n\nBased on your goal of becoming a **{user_context['goals']}**, "
                    f"this course {'is highly relevant' if info['domain'] in (user_context.get('interests') or []) else 'can complement your learning'}."
                )
            return {
                "type": "course_info",
                "course": course,
                "response": response_text,
                "keywords": info["keywords"],
            }

        # Skill gap questions
        gap_keywords = ["skill gap", "what am i missing", "what do i need",
                       "am i ready", "readiness", "gaps", "how far"]
        is_gap = any(kw in cleaned for kw in gap_keywords)

        if is_gap and user_context:
            completed = user_context.get("completed_courses", [])
            goal = user_context.get("goals", "")
            if goal and completed:
                gap_analysis = self.analyze_skill_gaps(completed, goal)
                weakness_text = ", ".join([w["domain"] for w in gap_analysis["weaknesses"][:3]])
                return {
                    "type": "skill_gap",
                    "response": (
                        f"Based on your progress, you're **{gap_analysis['overall_readiness']:.0f}% ready** "
                        f"for a {gap_analysis['target_role']} role. "
                        f"Your biggest skill gaps are in: **{weakness_text}**. "
                        f"I recommend focusing on these areas next. Would you like me to "
                        f"generate a targeted learning path to close these gaps?"
                    ),
                    "gap_analysis": gap_analysis,
                }

        # Goal/career questions
        goal_keywords = ["become", "learn", "career", "job", "path", "roadmap",
                         "start", "beginner", "how to", "want to", "interested"]
        is_goal = any(kw in cleaned for kw in goal_keywords)

        if is_goal:
            recs = self.recommend_courses(question, top_k=5)
            if recs:
                course_list = [r["course"] for r in recs]
                return {
                    "type": "recommendation",
                    "response": (
                        f"Based on your interest, I'd recommend starting with these courses: "
                        f"**{course_list[0]}**, **{course_list[1]}**, and **{course_list[2]}**. "
                        f"These courses align well with your goals and will build a strong foundation."
                    ),
                    "recommendations": recs,
                }

        # Comparison questions
        compare_keywords = ["compare", "difference", "vs", "versus", "better",
                            "which one", "choose between"]
        is_compare = any(kw in cleaned for kw in compare_keywords)

        if is_compare:
            recs = self.recommend_courses(question, top_k=3)
            if len(recs) >= 2:
                return {
                    "type": "comparison",
                    "response": (
                        f"Great question! Here's a quick comparison of relevant courses. "
                        f"**{recs[0]['course']}** focuses on {', '.join(recs[0]['keywords'][:3])}, "
                        f"while **{recs[1]['course']}** covers {', '.join(recs[1]['keywords'][:3])}. "
                        f"Your choice depends on your specific goals and current skill level."
                    ),
                    "recommendations": recs,
                }

        # Progress/motivation questions
        progress_keywords = ["how am i doing", "progress", "doing well", "on track",
                           "motivation", "stuck", "struggling"]
        is_progress = any(kw in cleaned for kw in progress_keywords)

        if is_progress and user_context:
            completed = len(user_context.get("completed_courses", []))
            return {
                "type": "motivation",
                "response": (
                    f"You've completed **{completed} courses** so far — great progress! 🎉 "
                    f"Every course you finish brings you closer to your goal. "
                    f"The most successful learners maintain consistency over speed. "
                    f"Would you like me to suggest what to focus on next?"
                ),
            }

        # Default: recommend based on the question
        recs = self.recommend_courses(question, top_k=3)
        if recs:
            return {
                "type": "general",
                "response": (
                    f"I found some courses that might be relevant to your question: "
                    f"**{recs[0]['course']}** (match: {recs[0]['score']:.0%}). "
                    f"Would you like me to create a personalized learning path?"
                ),
                "recommendations": recs,
            }

        return {
            "type": "fallback",
            "response": (
                "I'd be happy to help! Could you tell me more about your learning goals? "
                "For example, what career are you aiming for, or what skills would you like to develop?"
            ),
        }

    def _generate_explanation(self, user_text, course, score):
        """Generate a human-readable explanation for a recommendation."""
        user_words = set(clean_text(user_text).split())
        course_kws = self.keyword_map.get(course, [])

        # Find overlapping keywords
        matching = [kw for kw in course_kws[:15] if kw in user_words]

        if matching:
            kw_str = ", ".join(matching[:3])
            return f"Recommended because your interests in {kw_str} align strongly with this course's curriculum."
        elif score > 0.15:
            return f"Highly relevant to your goals based on content analysis (match: {score:.0%})."
        elif score > 0.08:
            return f"This course covers related topics that complement your learning objectives."
        else:
            return f"This course may provide useful foundational knowledge for your goals."

    def _classify_domain(self, course_name):
        """Classify a course into a domain category."""
        name_lower = course_name.lower()
        domain_map = {
            "Python": ["python"],
            "Web Development": ["html", "css", "javascript", "react", "angular", "vue",
                                "node", "django", "flask", "typescript", "graphql",
                                "rest api", "responsive web", "full stack"],
            "Data Science": ["data analysis", "pandas", "visualization", "matplotlib",
                             "tableau", "power bi", "excel", "exploratory", "statistics",
                             "statistical", "probability", "bayesian", "hypothesis"],
            "Machine Learning": ["machine learning", "supervised", "unsupervised",
                                 "feature engineering", "reinforcement", "transfer learning",
                                 "neural network", "deep learning", "tensorflow", "pytorch",
                                 "computer vision", "nlp", "natural language", "generative ai",
                                 "mlops"],
            "Mathematics": ["linear algebra", "calculus"],
            "Database": ["sql", "postgresql", "mongodb", "database", "redis",
                         "data warehouse", "etl"],
            "Cloud & DevOps": ["aws", "azure", "google cloud", "docker", "kubernetes",
                               "ci cd", "devops", "linux", "git"],
            "Mobile Development": ["react native", "flutter", "android", "ios", "swift"],
            "Programming": ["java", "c plus plus", "go language"],
            "Data Engineering": ["apache spark", "apache kafka", "data engineering"],
            "Security": ["cybersecurity", "ethical hacking"],
            "Emerging Tech": ["blockchain", "smart contract", "solidity", "iot",
                              "raspberry pi", "embedded systems", "prompt engineering"],
        }

        for domain, keywords in domain_map.items():
            if any(kw in name_lower for kw in keywords):
                return domain
        return "General"

    def _estimate_difficulty(self, course_name):
        """Estimate course difficulty from its name."""
        name_lower = course_name.lower()
        if any(kw in name_lower for kw in ["beginner", "basics", "fundamentals",
                                            "essentials", "absolute", "introduction"]):
            return "Beginner"
        elif any(kw in name_lower for kw in ["advanced", "optimization", "fine-tuning",
                                              "orchestration", "architect"]):
            return "Advanced"
        else:
            return "Intermediate"


# Singleton
engine = RecommendationEngine()
