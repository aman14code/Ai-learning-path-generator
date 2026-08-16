"""
PathFinder ML Recommendation Engine
Uses TF-IDF + course profiles for fast inference.
No heavy classifier training at startup - pre-computes course embeddings instead.
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


class RecommendationEngine:
    """AI-powered course recommendation engine."""

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

    def answer_question(self, question, context=None):
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
            return {
                "type": "course_info",
                "course": course,
                "response": (
                    f"**{course}** is a {info['difficulty'].lower()}-level course "
                    f"in the {info['domain']} domain. It covers topics like "
                    f"{', '.join(info['keywords'][:5])}. "
                    f"Based on {info['num_reviews']} learner reviews, it's a "
                    f"well-structured course for building practical skills."
                ),
                "keywords": info["keywords"],
            }

        # Goal/career questions
        goal_keywords = ["become", "learn", "career", "job", "path", "roadmap",
                         "start", "beginner", "how to", "want to", "interested"]
        is_goal = any(kw in cleaned for kw in goal_keywords)

        if is_goal:
            recs = self.recommend_courses(question, top_k=5)
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
