"""
PathFinder Learning Path Generator
Builds structured learning roadmaps using a course prerequisite graph.
"""

# ============================================================================
# COURSE PREREQUISITE GRAPH
# Organized by domain with difficulty levels and dependencies
# ============================================================================

COURSE_GRAPH = {
    # ---- Python Track ----
    "Python for Absolute Beginners": {
        "prerequisites": [],
        "difficulty": 1,
        "domain": "Python",
        "duration_hours": 20,
        "description": "Start your programming journey with Python fundamentals.",
        "skills": ["variables", "loops", "functions", "data types"],
    },
    "Python Programming Masterclass": {
        "prerequisites": ["Python for Absolute Beginners"],
        "difficulty": 2,
        "domain": "Python",
        "duration_hours": 40,
        "description": "Master Python with advanced programming concepts.",
        "skills": ["file handling", "error handling", "modules", "libraries"],
    },
    "Python OOP Concepts": {
        "prerequisites": ["Python Programming Masterclass"],
        "difficulty": 2,
        "domain": "Python",
        "duration_hours": 25,
        "description": "Learn object-oriented programming in Python.",
        "skills": ["classes", "inheritance", "polymorphism", "encapsulation"],
    },
    "Advanced Python Development": {
        "prerequisites": ["Python OOP Concepts"],
        "difficulty": 3,
        "domain": "Python",
        "duration_hours": 35,
        "description": "Advanced Python patterns, decorators, generators, and more.",
        "skills": ["decorators", "generators", "context managers", "metaclasses"],
    },
    "Python Automation and Scripting": {
        "prerequisites": ["Python Programming Masterclass"],
        "difficulty": 2,
        "domain": "Python",
        "duration_hours": 20,
        "description": "Automate tasks with Python scripts.",
        "skills": ["automation", "web scraping", "file automation", "scheduling"],
    },
    "Python for Data Science": {
        "prerequisites": ["Python Programming Masterclass"],
        "difficulty": 2,
        "domain": "Python",
        "duration_hours": 30,
        "description": "Python libraries and tools for data science workflows.",
        "skills": ["numpy", "pandas", "matplotlib", "jupyter"],
    },

    # ---- Web Frontend Track ----
    "HTML and CSS for Beginners": {
        "prerequisites": [],
        "difficulty": 1,
        "domain": "Web Development",
        "duration_hours": 20,
        "description": "Build your first websites with HTML and CSS.",
        "skills": ["html tags", "css styling", "box model", "flexbox"],
    },
    "Responsive Web Design": {
        "prerequisites": ["HTML and CSS for Beginners"],
        "difficulty": 2,
        "domain": "Web Development",
        "duration_hours": 15,
        "description": "Create websites that work on all devices.",
        "skills": ["media queries", "grid layout", "mobile first", "responsive images"],
    },
    "JavaScript Fundamentals": {
        "prerequisites": ["HTML and CSS for Beginners"],
        "difficulty": 1,
        "domain": "Web Development",
        "duration_hours": 30,
        "description": "Learn the language of the web.",
        "skills": ["variables", "functions", "DOM", "events"],
    },
    "Modern JavaScript ES6 Plus": {
        "prerequisites": ["JavaScript Fundamentals"],
        "difficulty": 2,
        "domain": "Web Development",
        "duration_hours": 25,
        "description": "Master modern JavaScript features and patterns.",
        "skills": ["arrow functions", "promises", "async await", "modules"],
    },
    "TypeScript for Developers": {
        "prerequisites": ["Modern JavaScript ES6 Plus"],
        "difficulty": 2,
        "domain": "Web Development",
        "duration_hours": 20,
        "description": "Add type safety to your JavaScript projects.",
        "skills": ["types", "interfaces", "generics", "type guards"],
    },
    "React.js Development": {
        "prerequisites": ["Modern JavaScript ES6 Plus"],
        "difficulty": 2,
        "domain": "Web Development",
        "duration_hours": 35,
        "description": "Build modern UIs with React.",
        "skills": ["components", "hooks", "state management", "routing"],
    },
    "Advanced React Patterns and Performance": {
        "prerequisites": ["React.js Development"],
        "difficulty": 3,
        "domain": "Web Development",
        "duration_hours": 30,
        "description": "Deep dive into React internals, custom hooks, and performance tuning.",
        "skills": ["custom hooks", "memoization", "context", "react internals"],
    },
    "Next.js and Full Stack React": {
        "prerequisites": ["Advanced React Patterns and Performance"],
        "difficulty": 3,
        "domain": "Web Development",
        "duration_hours": 35,
        "description": "Production-ready React with Next.js.",
        "skills": ["ssr", "ssg", "server components", "next.js"],
    },
    "Angular Framework Essentials": {
        "prerequisites": ["TypeScript for Developers"],
        "difficulty": 2,
        "domain": "Web Development",
        "duration_hours": 35,
        "description": "Enterprise-grade web apps with Angular.",
        "skills": ["components", "services", "dependency injection", "rxjs"],
    },
    "Vue.js for Beginners": {
        "prerequisites": ["Modern JavaScript ES6 Plus"],
        "difficulty": 2,
        "domain": "Web Development",
        "duration_hours": 25,
        "description": "The progressive JavaScript framework.",
        "skills": ["vue components", "vue router", "vuex", "composition api"],
    },
    "JavaScript Full Stack Development": {
        "prerequisites": ["React.js Development", "Node.js Backend Development"],
        "difficulty": 3,
        "domain": "Web Development",
        "duration_hours": 45,
        "description": "Full-stack JavaScript with React and Node.",
        "skills": ["full stack", "mern", "deployment", "authentication"],
    },

    # ---- Web Backend Track ----
    "Node.js Backend Development": {
        "prerequisites": ["Modern JavaScript ES6 Plus"],
        "difficulty": 2,
        "domain": "Web Development",
        "duration_hours": 30,
        "description": "Server-side JavaScript with Node.js.",
        "skills": ["express", "middleware", "api design", "authentication"],
    },
    "Express.js Advanced API Design": {
        "prerequisites": ["Node.js Backend Development"],
        "difficulty": 3,
        "domain": "Web Development",
        "duration_hours": 25,
        "description": "Master Express.js architecture and advanced patterns.",
        "skills": ["advanced routing", "error handling", "security", "websockets"],
    },
    "REST API Design Principles": {
        "prerequisites": ["Node.js Backend Development"],
        "difficulty": 2,
        "domain": "Web Development",
        "duration_hours": 15,
        "description": "Design clean, scalable REST APIs.",
        "skills": ["rest", "http methods", "status codes", "versioning"],
    },
    "GraphQL API Development": {
        "prerequisites": ["REST API Design Principles"],
        "difficulty": 3,
        "domain": "Web Development",
        "duration_hours": 20,
        "description": "Modern API development with GraphQL.",
        "skills": ["schemas", "resolvers", "queries", "mutations"],
    },
    "Django Web Framework": {
        "prerequisites": ["Python OOP Concepts"],
        "difficulty": 2,
        "domain": "Web Development",
        "duration_hours": 35,
        "description": "Full-featured web apps with Django.",
        "skills": ["models", "views", "templates", "admin"],
    },
    "Flask API Development": {
        "prerequisites": ["Python OOP Concepts"],
        "difficulty": 2,
        "domain": "Web Development",
        "duration_hours": 20,
        "description": "Lightweight Python web APIs with Flask.",
        "skills": ["routes", "blueprints", "jinja2", "rest api"],
    },
    "Java Programming Basics": {
        "prerequisites": [],
        "difficulty": 1,
        "domain": "Programming",
        "duration_hours": 35,
        "description": "Learn programming fundamentals with Java.",
        "skills": ["oop", "data structures", "collections", "streams"],
    },
    "Advanced Java and Spring Boot": {
        "prerequisites": ["Java Programming Basics"],
        "difficulty": 3,
        "domain": "Programming",
        "duration_hours": 40,
        "description": "Enterprise Java with Spring Boot.",
        "skills": ["spring boot", "microservices", "jpa", "security"],
    },
    "Microservices with Spring Boot": {
        "prerequisites": ["Advanced Java and Spring Boot"],
        "difficulty": 3,
        "domain": "Programming",
        "duration_hours": 35,
        "description": "Build distributed systems with Spring Cloud and Spring Boot.",
        "skills": ["microservices", "spring cloud", "service discovery", "api gateway"],
    },
    "Spring Security and OAuth2": {
        "prerequisites": ["Advanced Java and Spring Boot"],
        "difficulty": 3,
        "domain": "Programming",
        "duration_hours": 20,
        "description": "Deep dive into securing Spring applications.",
        "skills": ["oauth2", "jwt", "authorization", "spring security"],
    },
    "C Plus Plus Programming Essentials": {
        "prerequisites": [],
        "difficulty": 1,
        "domain": "Programming",
        "duration_hours": 30,
        "description": "Systems programming with C++.",
        "skills": ["pointers", "memory management", "stl", "oop"],
    },
    "Go Language for Backend": {
        "prerequisites": [],
        "difficulty": 2,
        "domain": "Programming",
        "duration_hours": 25,
        "description": "Build fast, concurrent backends with Go.",
        "skills": ["goroutines", "channels", "interfaces", "http server"],
    },

    # ---- Mobile Track ----
    "React Native Mobile Development": {
        "prerequisites": ["React.js Development"],
        "difficulty": 2,
        "domain": "Mobile Development",
        "duration_hours": 30,
        "description": "Cross-platform mobile apps with React Native.",
        "skills": ["components", "navigation", "native modules", "expo"],
    },
    "Flutter Cross Platform Apps": {
        "prerequisites": [],
        "difficulty": 2,
        "domain": "Mobile Development",
        "duration_hours": 30,
        "description": "Beautiful cross-platform apps with Flutter.",
        "skills": ["widgets", "dart", "state management", "animations"],
    },
    "Android App Development": {
        "prerequisites": ["Java Programming Basics"],
        "difficulty": 2,
        "domain": "Mobile Development",
        "duration_hours": 35,
        "description": "Native Android development.",
        "skills": ["activities", "fragments", "jetpack", "material design"],
    },
    "iOS App Development with Swift": {
        "prerequisites": [],
        "difficulty": 2,
        "domain": "Mobile Development",
        "duration_hours": 35,
        "description": "Build iOS apps with Swift and SwiftUI.",
        "skills": ["swift", "swiftui", "uikit", "core data"],
    },

    # ---- Data Science Track ----
    "Excel for Data Analysis": {
        "prerequisites": [],
        "difficulty": 1,
        "domain": "Data Science",
        "duration_hours": 15,
        "description": "Data analysis fundamentals with Excel.",
        "skills": ["formulas", "pivot tables", "charts", "vlookup"],
    },
    "Data Analysis with Pandas": {
        "prerequisites": ["Python for Data Science"],
        "difficulty": 2,
        "domain": "Data Science",
        "duration_hours": 25,
        "description": "Data manipulation with pandas.",
        "skills": ["dataframes", "groupby", "merge", "data cleaning"],
    },
    "Exploratory Data Analysis": {
        "prerequisites": ["Data Analysis with Pandas"],
        "difficulty": 2,
        "domain": "Data Science",
        "duration_hours": 20,
        "description": "Discover patterns and insights in data.",
        "skills": ["distributions", "correlations", "outliers", "visualization"],
    },
    "Data Visualization with Matplotlib": {
        "prerequisites": ["Data Analysis with Pandas"],
        "difficulty": 2,
        "domain": "Data Science",
        "duration_hours": 15,
        "description": "Create compelling data visualizations.",
        "skills": ["matplotlib", "seaborn", "charts", "dashboards"],
    },
    "Tableau for Business Analytics": {
        "prerequisites": ["Excel for Data Analysis"],
        "difficulty": 2,
        "domain": "Data Science",
        "duration_hours": 20,
        "description": "Business analytics and dashboards with Tableau.",
        "skills": ["dashboards", "calculated fields", "stories", "filters"],
    },
    "Power BI Dashboard Creation": {
        "prerequisites": ["Excel for Data Analysis"],
        "difficulty": 2,
        "domain": "Data Science",
        "duration_hours": 20,
        "description": "Business intelligence dashboards with Power BI.",
        "skills": ["dax", "data modeling", "dashboards", "power query"],
    },

    # ---- Mathematics Track ----
    "Linear Algebra for Machine Learning": {
        "prerequisites": [],
        "difficulty": 2,
        "domain": "Mathematics",
        "duration_hours": 20,
        "description": "Mathematical foundations for ML.",
        "skills": ["vectors", "matrices", "eigenvalues", "transformations"],
    },
    "Calculus for Data Science": {
        "prerequisites": [],
        "difficulty": 2,
        "domain": "Mathematics",
        "duration_hours": 20,
        "description": "Calculus concepts for data science and ML.",
        "skills": ["derivatives", "gradients", "optimization", "integrals"],
    },
    "Probability and Statistics": {
        "prerequisites": [],
        "difficulty": 1,
        "domain": "Data Science",
        "duration_hours": 25,
        "description": "Foundation of data science and ML.",
        "skills": ["probability", "distributions", "central limit theorem", "sampling"],
    },
    "Bayesian Statistics": {
        "prerequisites": ["Probability and Statistics"],
        "difficulty": 3,
        "domain": "Data Science",
        "duration_hours": 20,
        "description": "Bayesian approach to statistical inference.",
        "skills": ["bayes theorem", "prior", "posterior", "mcmc"],
    },
    "Hypothesis Testing in Practice": {
        "prerequisites": ["Probability and Statistics"],
        "difficulty": 2,
        "domain": "Data Science",
        "duration_hours": 15,
        "description": "Statistical hypothesis testing for real problems.",
        "skills": ["t-test", "chi-square", "p-value", "confidence intervals"],
    },
    "Statistical Analysis with R": {
        "prerequisites": ["Probability and Statistics"],
        "difficulty": 2,
        "domain": "Data Science",
        "duration_hours": 25,
        "description": "Statistical computing with R.",
        "skills": ["r programming", "ggplot2", "regression", "anova"],
    },

    # ---- Machine Learning Track ----
    "Machine Learning Fundamentals": {
        "prerequisites": ["Python for Data Science", "Linear Algebra for Machine Learning"],
        "difficulty": 2,
        "domain": "Machine Learning",
        "duration_hours": 35,
        "description": "Core ML algorithms and concepts.",
        "skills": ["regression", "classification", "cross validation", "bias variance"],
    },
    "Supervised Learning Algorithms": {
        "prerequisites": ["Machine Learning Fundamentals"],
        "difficulty": 2,
        "domain": "Machine Learning",
        "duration_hours": 25,
        "description": "Deep dive into supervised learning.",
        "skills": ["decision trees", "random forest", "svm", "ensemble methods"],
    },
    "Unsupervised Learning Techniques": {
        "prerequisites": ["Machine Learning Fundamentals"],
        "difficulty": 2,
        "domain": "Machine Learning",
        "duration_hours": 20,
        "description": "Clustering, dimensionality reduction, and more.",
        "skills": ["k-means", "pca", "dbscan", "anomaly detection"],
    },
    "Feature Engineering for ML": {
        "prerequisites": ["Machine Learning Fundamentals"],
        "difficulty": 2,
        "domain": "Machine Learning",
        "duration_hours": 20,
        "description": "Create powerful features for ML models.",
        "skills": ["feature selection", "encoding", "scaling", "feature creation"],
    },

    # ---- Deep Learning Track ----
    "Deep Learning with TensorFlow": {
        "prerequisites": ["Machine Learning Fundamentals", "Calculus for Data Science"],
        "difficulty": 3,
        "domain": "Machine Learning",
        "duration_hours": 40,
        "description": "Build neural networks with TensorFlow and Keras.",
        "skills": ["neural networks", "keras", "cnn", "training"],
    },
    "Deep Learning with PyTorch": {
        "prerequisites": ["Machine Learning Fundamentals", "Calculus for Data Science"],
        "difficulty": 3,
        "domain": "Machine Learning",
        "duration_hours": 40,
        "description": "Deep learning with PyTorch.",
        "skills": ["tensors", "autograd", "custom models", "training loops"],
    },
    "Advanced Neural Networks": {
        "prerequisites": ["Deep Learning with TensorFlow"],
        "difficulty": 3,
        "domain": "Machine Learning",
        "duration_hours": 30,
        "description": "Advanced architectures: attention, transformers, GANs.",
        "skills": ["attention", "transformers", "gan", "architecture design"],
    },
    "Computer Vision with OpenCV": {
        "prerequisites": ["Deep Learning with TensorFlow"],
        "difficulty": 3,
        "domain": "Machine Learning",
        "duration_hours": 25,
        "description": "Image processing and computer vision.",
        "skills": ["image processing", "object detection", "segmentation", "opencv"],
    },
    "Natural Language Processing": {
        "prerequisites": ["Deep Learning with TensorFlow"],
        "difficulty": 3,
        "domain": "Machine Learning",
        "duration_hours": 30,
        "description": "NLP with deep learning.",
        "skills": ["tokenization", "embeddings", "transformers", "sentiment"],
    },
    "Transfer Learning and Fine-tuning": {
        "prerequisites": ["Deep Learning with TensorFlow"],
        "difficulty": 3,
        "domain": "Machine Learning",
        "duration_hours": 15,
        "description": "Leverage pre-trained models effectively.",
        "skills": ["pretrained models", "fine tuning", "domain adaptation", "model selection"],
    },
    "Reinforcement Learning Basics": {
        "prerequisites": ["Machine Learning Fundamentals"],
        "difficulty": 3,
        "domain": "Machine Learning",
        "duration_hours": 25,
        "description": "Agents, rewards, and policy learning.",
        "skills": ["q-learning", "policy gradient", "mdp", "exploration"],
    },
    "Generative AI and Prompt Engineering": {
        "prerequisites": ["Natural Language Processing"],
        "difficulty": 3,
        "domain": "Machine Learning",
        "duration_hours": 20,
        "description": "Master generative AI and prompt design.",
        "skills": ["llm", "prompt engineering", "fine tuning", "rag"],
    },
    "MLOps and Model Deployment": {
        "prerequisites": ["Machine Learning Fundamentals"],
        "difficulty": 3,
        "domain": "Machine Learning",
        "duration_hours": 25,
        "description": "Deploy and manage ML models in production.",
        "skills": ["mlflow", "model serving", "monitoring", "pipelines"],
    },

    # ---- Database Track ----
    "SQL for Beginners": {
        "prerequisites": [],
        "difficulty": 1,
        "domain": "Database",
        "duration_hours": 20,
        "description": "Learn SQL for data querying.",
        "skills": ["select", "joins", "aggregation", "subqueries"],
    },
    "Advanced SQL and Query Optimization": {
        "prerequisites": ["SQL for Beginners"],
        "difficulty": 3,
        "domain": "Database",
        "duration_hours": 20,
        "description": "Write performant SQL queries.",
        "skills": ["query optimization", "indexing", "execution plans", "window functions"],
    },
    "PostgreSQL Database Design": {
        "prerequisites": ["SQL for Beginners"],
        "difficulty": 2,
        "domain": "Database",
        "duration_hours": 25,
        "description": "Design robust databases with PostgreSQL.",
        "skills": ["schema design", "normalization", "constraints", "triggers"],
    },
    "MongoDB for Developers": {
        "prerequisites": [],
        "difficulty": 2,
        "domain": "Database",
        "duration_hours": 20,
        "description": "NoSQL database development with MongoDB.",
        "skills": ["documents", "aggregation", "indexing", "mongoose"],
    },
    "Database Performance Tuning": {
        "prerequisites": ["Advanced SQL and Query Optimization"],
        "difficulty": 3,
        "domain": "Database",
        "duration_hours": 15,
        "description": "Optimize database performance at scale.",
        "skills": ["profiling", "caching", "partitioning", "replication"],
    },
    "Redis Caching Strategies": {
        "prerequisites": ["SQL for Beginners"],
        "difficulty": 2,
        "domain": "Database",
        "duration_hours": 15,
        "description": "In-memory caching with Redis.",
        "skills": ["caching", "data structures", "pub/sub", "ttl"],
    },

    # ---- Data Engineering Track ----
    "Data Warehouse Design": {
        "prerequisites": ["SQL for Beginners"],
        "difficulty": 2,
        "domain": "Data Engineering",
        "duration_hours": 20,
        "description": "Design data warehouses for analytics.",
        "skills": ["star schema", "etl", "olap", "dimensional modeling"],
    },
    "ETL Pipeline Development": {
        "prerequisites": ["Python for Data Science", "SQL for Beginners"],
        "difficulty": 2,
        "domain": "Data Engineering",
        "duration_hours": 25,
        "description": "Build data pipelines with Python.",
        "skills": ["extraction", "transformation", "loading", "scheduling"],
    },
    "Data Engineering with Apache Spark": {
        "prerequisites": ["ETL Pipeline Development"],
        "difficulty": 3,
        "domain": "Data Engineering",
        "duration_hours": 30,
        "description": "Big data processing with Spark.",
        "skills": ["spark sql", "dataframes", "rdd", "streaming"],
    },
    "Apache Kafka for Real-time Data": {
        "prerequisites": ["ETL Pipeline Development"],
        "difficulty": 3,
        "domain": "Data Engineering",
        "duration_hours": 20,
        "description": "Real-time event streaming with Kafka.",
        "skills": ["producers", "consumers", "topics", "stream processing"],
    },
    "Time Series Analysis": {
        "prerequisites": ["Data Analysis with Pandas", "Probability and Statistics"],
        "difficulty": 2,
        "domain": "Data Science",
        "duration_hours": 20,
        "description": "Analyze and forecast time series data.",
        "skills": ["arima", "seasonality", "forecasting", "stationarity"],
    },

    # ---- Cloud & DevOps Track ----
    "Linux Command Line Essentials": {
        "prerequisites": [],
        "difficulty": 1,
        "domain": "Cloud & DevOps",
        "duration_hours": 15,
        "description": "Master the Linux command line.",
        "skills": ["bash", "file system", "permissions", "shell scripting"],
    },
    "Git and GitHub Mastery": {
        "prerequisites": [],
        "difficulty": 1,
        "domain": "Cloud & DevOps",
        "duration_hours": 15,
        "description": "Version control with Git and GitHub.",
        "skills": ["commits", "branches", "merge", "pull requests"],
    },
    "Docker and Containerization": {
        "prerequisites": ["Linux Command Line Essentials"],
        "difficulty": 2,
        "domain": "Cloud & DevOps",
        "duration_hours": 20,
        "description": "Containerize applications with Docker.",
        "skills": ["containers", "images", "docker compose", "networking"],
    },
    "Kubernetes Orchestration": {
        "prerequisites": ["Docker and Containerization"],
        "difficulty": 3,
        "domain": "Cloud & DevOps",
        "duration_hours": 30,
        "description": "Container orchestration with Kubernetes.",
        "skills": ["pods", "services", "deployments", "helm"],
    },
    "CI CD Pipeline Setup": {
        "prerequisites": ["Git and GitHub Mastery", "Docker and Containerization"],
        "difficulty": 2,
        "domain": "Cloud & DevOps",
        "duration_hours": 15,
        "description": "Automate build, test, and deploy pipelines.",
        "skills": ["github actions", "jenkins", "testing", "deployment"],
    },
    "DevOps Practices and Tools": {
        "prerequisites": ["CI CD Pipeline Setup"],
        "difficulty": 2,
        "domain": "Cloud & DevOps",
        "duration_hours": 25,
        "description": "DevOps culture, tools, and best practices.",
        "skills": ["monitoring", "logging", "infrastructure as code", "sre"],
    },
    "AWS Cloud Practitioner": {
        "prerequisites": [],
        "difficulty": 1,
        "domain": "Cloud & DevOps",
        "duration_hours": 20,
        "description": "Introduction to AWS cloud services.",
        "skills": ["ec2", "s3", "iam", "vpc"],
    },
    "AWS Solutions Architect": {
        "prerequisites": ["AWS Cloud Practitioner"],
        "difficulty": 3,
        "domain": "Cloud & DevOps",
        "duration_hours": 40,
        "description": "Design scalable architectures on AWS.",
        "skills": ["architecture", "high availability", "security", "cost optimization"],
    },
    "Azure Fundamentals": {
        "prerequisites": [],
        "difficulty": 1,
        "domain": "Cloud & DevOps",
        "duration_hours": 20,
        "description": "Microsoft Azure cloud fundamentals.",
        "skills": ["azure services", "virtual machines", "storage", "networking"],
    },
    "Google Cloud Platform Basics": {
        "prerequisites": [],
        "difficulty": 1,
        "domain": "Cloud & DevOps",
        "duration_hours": 20,
        "description": "Google Cloud Platform essentials.",
        "skills": ["compute engine", "cloud storage", "bigquery", "gke"],
    },

    # ---- Security Track ----
    "Cybersecurity Fundamentals": {
        "prerequisites": ["Linux Command Line Essentials"],
        "difficulty": 2,
        "domain": "Security",
        "duration_hours": 25,
        "description": "Core cybersecurity concepts and practices.",
        "skills": ["network security", "encryption", "firewalls", "risk assessment"],
    },
    "Ethical Hacking Basics": {
        "prerequisites": ["Cybersecurity Fundamentals"],
        "difficulty": 2,
        "domain": "Security",
        "duration_hours": 25,
        "description": "Penetration testing and ethical hacking.",
        "skills": ["reconnaissance", "vulnerability scanning", "exploitation", "reporting"],
    },

    # ---- Emerging Tech Track ----
    "Blockchain Development": {
        "prerequisites": ["Modern JavaScript ES6 Plus"],
        "difficulty": 2,
        "domain": "Emerging Tech",
        "duration_hours": 25,
        "description": "Build decentralized applications.",
        "skills": ["blockchain", "consensus", "dapps", "web3"],
    },
    "Smart Contract Programming with Solidity": {
        "prerequisites": ["Blockchain Development"],
        "difficulty": 3,
        "domain": "Emerging Tech",
        "duration_hours": 20,
        "description": "Write smart contracts in Solidity.",
        "skills": ["solidity", "ethereum", "erc20", "defi"],
    },
    "IoT with Raspberry Pi": {
        "prerequisites": ["Python for Absolute Beginners"],
        "difficulty": 2,
        "domain": "Emerging Tech",
        "duration_hours": 20,
        "description": "Internet of Things projects with Raspberry Pi.",
        "skills": ["sensors", "gpio", "mqtt", "iot protocols"],
    },
    "Embedded Systems Programming": {
        "prerequisites": ["C Plus Plus Programming Essentials"],
        "difficulty": 3,
        "domain": "Emerging Tech",
        "duration_hours": 25,
        "description": "Programming for embedded systems and microcontrollers.",
        "skills": ["microcontrollers", "firmware", "rtos", "hardware interfaces"],
    },
}


# ============================================================================
# CAREER PATHS - Pre-defined learning paths for common goals
# ============================================================================

CAREER_PATHS = {
    "data_scientist": {
        "title": "Data Scientist",
        "description": "Analyze data, build ML models, and derive insights.",
        "courses": [
            "Python for Absolute Beginners",
            "Python Programming Masterclass",
            "Python for Data Science",
            "Probability and Statistics",
            "Data Analysis with Pandas",
            "Data Visualization with Matplotlib",
            "Exploratory Data Analysis",
            "Linear Algebra for Machine Learning",
            "Machine Learning Fundamentals",
            "Supervised Learning Algorithms",
            "Unsupervised Learning Techniques",
            "Feature Engineering for ML",
            "Deep Learning with TensorFlow",
        ],
    },
    "web_developer": {
        "title": "Full Stack Web Developer",
        "description": "Build modern web applications from frontend to backend.",
        "courses": [
            "HTML and CSS for Beginners",
            "JavaScript Fundamentals",
            "Responsive Web Design",
            "Modern JavaScript ES6 Plus",
            "React.js Development",
            "Advanced React Patterns and Performance",
            "Node.js Backend Development",
            "Express.js Advanced API Design",
            "REST API Design Principles",
            "SQL for Beginners",
            "MongoDB for Developers",
            "Next.js and Full Stack React",
        ],
    },
    "ml_engineer": {
        "title": "Machine Learning Engineer",
        "description": "Build and deploy production ML systems.",
        "courses": [
            "Python for Absolute Beginners",
            "Python Programming Masterclass",
            "Python OOP Concepts",
            "Linear Algebra for Machine Learning",
            "Calculus for Data Science",
            "Python for Data Science",
            "Machine Learning Fundamentals",
            "Deep Learning with TensorFlow",
            "Deep Learning with PyTorch",
            "Advanced Neural Networks",
            "MLOps and Model Deployment",
            "Docker and Containerization",
        ],
    },
    "devops_engineer": {
        "title": "DevOps Engineer",
        "description": "Automate infrastructure and deployment pipelines.",
        "courses": [
            "Linux Command Line Essentials",
            "Git and GitHub Mastery",
            "Python for Absolute Beginners",
            "Python Automation and Scripting",
            "Docker and Containerization",
            "Kubernetes Orchestration",
            "CI CD Pipeline Setup",
            "DevOps Practices and Tools",
            "AWS Cloud Practitioner",
            "AWS Solutions Architect",
        ],
    },
    "mobile_developer": {
        "title": "Mobile App Developer",
        "description": "Build cross-platform mobile applications.",
        "courses": [
            "HTML and CSS for Beginners",
            "JavaScript Fundamentals",
            "Modern JavaScript ES6 Plus",
            "React.js Development",
            "React Native Mobile Development",
            "Git and GitHub Mastery",
            "REST API Design Principles",
            "Flutter Cross Platform Apps",
        ],
    },
    "data_engineer": {
        "title": "Data Engineer",
        "description": "Build data pipelines and infrastructure at scale.",
        "courses": [
            "Python for Absolute Beginners",
            "Python Programming Masterclass",
            "SQL for Beginners",
            "Advanced SQL and Query Optimization",
            "Python for Data Science",
            "ETL Pipeline Development",
            "Data Warehouse Design",
            "Data Engineering with Apache Spark",
            "Apache Kafka for Real-time Data",
            "Docker and Containerization",
        ],
    },
    "ai_specialist": {
        "title": "AI/GenAI Specialist",
        "description": "Work with cutting-edge AI and generative models.",
        "courses": [
            "Python for Absolute Beginners",
            "Python Programming Masterclass",
            "Linear Algebra for Machine Learning",
            "Machine Learning Fundamentals",
            "Deep Learning with TensorFlow",
            "Advanced Neural Networks",
            "Natural Language Processing",
            "Computer Vision with OpenCV",
            "Generative AI and Prompt Engineering",
            "Transfer Learning and Fine-tuning",
        ],
    },
    "cybersecurity_analyst": {
        "title": "Cybersecurity Analyst",
        "description": "Protect systems and networks from security threats.",
        "courses": [
            "Linux Command Line Essentials",
            "Python for Absolute Beginners",
            "Python Automation and Scripting",
            "SQL for Beginners",
            "Cybersecurity Fundamentals",
            "Ethical Hacking Basics",
            "AWS Cloud Practitioner",
            "Docker and Containerization",
        ],
    },
}


def generate_learning_path(goal, completed_courses=None, experience_level="beginner",
                           interests=None, ml_engine=None):
    """Generate a personalized learning path."""
    completed = set(completed_courses or [])

    # Check if goal matches a career path
    goal_lower = goal.lower()
    matched_career = None
    career_keywords = {
        "data_scientist": ["data scientist", "data science", "analyze data", "analytics"],
        "web_developer": ["web developer", "full stack", "frontend", "backend", "web app"],
        "ml_engineer": ["machine learning engineer", "ml engineer", "deep learning",
                        "ai engineer"],
        "devops_engineer": ["devops", "infrastructure", "deployment", "cloud engineer"],
        "mobile_developer": ["mobile developer", "app developer", "android", "ios",
                              "mobile app"],
        "data_engineer": ["data engineer", "data pipeline", "etl", "big data"],
        "ai_specialist": ["ai specialist", "artificial intelligence", "generative ai",
                          "nlp", "computer vision"],
        "cybersecurity_analyst": ["cybersecurity", "security analyst", "ethical hacking",
                                   "penetration testing"],
    }

    for career_key, keywords in career_keywords.items():
        if any(kw in goal_lower for kw in keywords):
            matched_career = career_key
            break

    if matched_career:
        career = CAREER_PATHS[matched_career]
        path_courses = [c for c in career["courses"] if c not in completed]
    else:
        # Use ML engine to find relevant courses
        if ml_engine:
            recs = ml_engine.recommend_for_goal(goal, experience_level, interests)
            path_courses = [r["course"] for r in recs if r["course"] not in completed]
        else:
            # Fallback: search by keywords
            path_courses = []
            for name, info in COURSE_GRAPH.items():
                if name in completed:
                    continue
                name_lower = name.lower()
                if any(word in name_lower for word in goal_lower.split()):
                    path_courses.append(name)

    # Resolve prerequisites and order correctly
    ordered = _topological_sort(path_courses, completed)

    # Build milestone structure
    milestones = _build_milestones(ordered)

    total_hours = sum(
        COURSE_GRAPH.get(c, {}).get("duration_hours", 20) for c in ordered
    )

    return {
        "goal": goal,
        "career_path": CAREER_PATHS.get(matched_career, {}).get("title", "Custom Path"),
        "career_description": CAREER_PATHS.get(matched_career, {}).get("description", ""),
        "total_courses": len(ordered),
        "total_hours": total_hours,
        "estimated_weeks": max(1, total_hours // 10),
        "milestones": milestones,
        "courses": [
            {
                "name": c,
                "order": i + 1,
                **COURSE_GRAPH.get(c, {
                    "difficulty": 2,
                    "domain": "General",
                    "duration_hours": 20,
                    "description": f"Learn {c}.",
                    "skills": [],
                    "prerequisites": [],
                }),
            }
            for i, c in enumerate(ordered)
        ],
    }


def _topological_sort(courses, completed):
    """Sort courses respecting prerequisites."""
    # Include prerequisites not yet completed
    all_needed = set()
    queue = list(courses)
    visited = set()

    while queue:
        course = queue.pop(0)
        if course in visited or course in completed:
            continue
        visited.add(course)
        all_needed.add(course)
        prereqs = COURSE_GRAPH.get(course, {}).get("prerequisites", [])
        for p in prereqs:
            if p not in completed and p not in visited:
                queue.append(p)
                all_needed.add(p)

    # Topological sort
    sorted_list = []
    remaining = set(all_needed)
    max_iterations = len(remaining) * 2 + 10

    while remaining and max_iterations > 0:
        max_iterations -= 1
        candidates = []
        for course in remaining:
            prereqs = COURSE_GRAPH.get(course, {}).get("prerequisites", [])
            unmet = [p for p in prereqs if p in remaining]
            if not unmet:
                candidates.append(course)
        
        if not candidates:
            break
            
        # Sort candidates by difficulty so lower level courses are completed first
        candidates.sort(key=lambda c: COURSE_GRAPH.get(c, {}).get("difficulty", 2))
        
        for c in candidates:
            sorted_list.append(c)
            remaining.discard(c)

    # Add any remaining (circular deps)
    sorted_list.extend(remaining)
    return sorted_list


def _build_milestones(courses):
    """Group courses into milestones by difficulty."""
    milestones = []
    current_milestone = {"title": "", "courses": [], "difficulty": 0}

    difficulty_names = {1: "Foundation", 2: "Core Skills", 3: "Advanced Mastery"}

    for course in courses:
        info = COURSE_GRAPH.get(course, {})
        diff = info.get("difficulty", 2)

        if diff != current_milestone["difficulty"]:
            if current_milestone["courses"]:
                milestones.append(current_milestone)
            current_milestone = {
                "title": difficulty_names.get(diff, f"Level {diff}"),
                "courses": [],
                "difficulty": diff,
            }

        current_milestone["courses"].append(course)

    if current_milestone["courses"]:
        milestones.append(current_milestone)

    return milestones


def get_all_domains():
    """Get all unique domains."""
    domains = set()
    for info in COURSE_GRAPH.values():
        domains.add(info.get("domain", "General"))
    return sorted(domains)


def get_career_paths():
    """Get all pre-defined career paths."""
    return [
        {"key": k, "title": v["title"], "description": v["description"],
         "course_count": len(v["courses"])}
        for k, v in CAREER_PATHS.items()
    ]
