import { useNavigate } from 'react-router-dom';
import './Landing.css';

const FEATURES = [
  {
    icon: '\u{1F916}',
    title: 'AI-Powered Recommendations',
    desc: 'Our ML engine analyzes 110K+ course reviews to find the perfect learning path for you.',
  },
  {
    icon: '\u{1F5FA}',
    title: 'Personalized Roadmaps',
    desc: 'Get structured learning paths with prerequisites, milestones, and estimated timelines.',
  },
  {
    icon: '\u{1F4AC}',
    title: 'AI Learning Assistant',
    desc: 'Chat with our AI to get course recommendations, comparisons, and study tips.',
  },
  {
    icon: '\u{1F4CA}',
    title: 'Progress Dashboard',
    desc: 'Track your learning journey with skill maps, progress charts, and milestone tracking.',
  },
];

const STATS = [
  { value: '80+', label: 'Courses' },
  { value: '110K+', label: 'Reviews Analyzed' },
  { value: '8', label: 'Career Paths' },
  { value: '12', label: 'Skill Domains' },
];

export default function Landing() {
  const navigate = useNavigate();

  return (
    <div className="landing">
      <div className="bg-mesh" />

      {/* Hero */}
      <header className="landing-header">
        <div className="landing-logo">
          <div className="sidebar-logo-icon">PF</div>
          <span className="landing-brand">PathFinder</span>
        </div>
      </header>

      <section className="hero">
        <div className="hero-badge">AI-Powered Learning Platform</div>
        <h1 className="hero-title">
          Find Your Perfect <br />
          <span className="gradient-text">Learning Path</span>
        </h1>
        <p className="hero-subtitle">
          Tell us your career goals and we'll create a personalized learning roadmap
          powered by AI analysis of 110,000+ course reviews across 80 courses.
        </p>
        <div className="hero-actions">
          <button className="btn btn-primary btn-lg" onClick={() => navigate('/onboarding')}>
            Get Started Free
          </button>
          <button className="btn btn-secondary btn-lg" onClick={() => document.getElementById('features').scrollIntoView({ behavior: 'smooth' })}>
            Learn More
          </button>
        </div>

        {/* Stats */}
        <div className="hero-stats">
          {STATS.map((s) => (
            <div key={s.label} className="hero-stat">
              <div className="hero-stat-value">{s.value}</div>
              <div className="hero-stat-label">{s.label}</div>
            </div>
          ))}
        </div>
      </section>

      {/* Features */}
      <section id="features" className="features-section">
        <h2 className="section-title">Why PathFinder?</h2>
        <p className="section-subtitle">Everything you need to accelerate your learning journey</p>
        <div className="features-grid stagger">
          {FEATURES.map((f) => (
            <div key={f.title} className="feature-card glass-card">
              <div className="feature-icon">{f.icon}</div>
              <h3>{f.title}</h3>
              <p>{f.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* CTA */}
      <section className="cta-section">
        <div className="cta-card glass-card">
          <h2>Ready to start your journey?</h2>
          <p>Create your learner profile in 60 seconds and get personalized recommendations.</p>
          <button className="btn btn-primary btn-lg" onClick={() => navigate('/onboarding')}>
            Create Your Profile
          </button>
        </div>
      </section>

      <footer className="landing-footer">
        <p>PathFinder - AI-Powered Personalized Learning Path Recommender</p>
        <p className="text-muted">Built for HCL PathFinder Hackathon 2026</p>
      </footer>
    </div>
  );
}
