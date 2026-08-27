import { useNavigate } from 'react-router-dom';
import { useEffect, useRef } from 'react';
import './Landing.css';

/* ---- Neural Particle Canvas Background ---- */
function NeuralParticles() {
  const canvasRef = useRef(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    let animFrame;
    let particles = [];

    function resize() {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
    }
    resize();
    window.addEventListener('resize', resize);

    // Create particles
    const count = Math.min(80, Math.floor(window.innerWidth / 18));
    for (let i = 0; i < count; i++) {
      particles.push({
        x: Math.random() * canvas.width,
        y: Math.random() * canvas.height,
        vx: (Math.random() - 0.5) * 0.4,
        vy: (Math.random() - 0.5) * 0.4,
        r: Math.random() * 2 + 1,
        alpha: Math.random() * 0.5 + 0.1,
      });
    }

    function draw() {
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      // Update and draw particles
      for (const p of particles) {
        p.x += p.vx;
        p.y += p.vy;
        if (p.x < 0) p.x = canvas.width;
        if (p.x > canvas.width) p.x = 0;
        if (p.y < 0) p.y = canvas.height;
        if (p.y > canvas.height) p.y = 0;

        ctx.beginPath();
        ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(99, 102, 241, ${p.alpha})`;
        ctx.fill();
      }

      // Draw connections
      for (let i = 0; i < particles.length; i++) {
        for (let j = i + 1; j < particles.length; j++) {
          const dx = particles[i].x - particles[j].x;
          const dy = particles[i].y - particles[j].y;
          const dist = Math.sqrt(dx * dx + dy * dy);
          if (dist < 150) {
            ctx.beginPath();
            ctx.moveTo(particles[i].x, particles[i].y);
            ctx.lineTo(particles[j].x, particles[j].y);
            ctx.strokeStyle = `rgba(99, 102, 241, ${0.08 * (1 - dist / 150)})`;
            ctx.lineWidth = 0.5;
            ctx.stroke();
          }
        }
      }

      animFrame = requestAnimationFrame(draw);
    }
    draw();

    return () => {
      cancelAnimationFrame(animFrame);
      window.removeEventListener('resize', resize);
    };
  }, []);

  return <canvas ref={canvasRef} className="neural-canvas" />;
}

const FEATURES = [
  {
    icon: '\u{1F9E0}',
    title: 'AI-Powered Recommendations',
    desc: 'Our ML engine analyzes 110K+ course reviews using TF-IDF vectorization and cosine similarity to find the perfect courses for you.',
  },
  {
    icon: '\u{1F5FA}',
    title: 'Personalized Roadmaps',
    desc: 'Get structured learning paths with prerequisites resolved via DAG topological sort, milestones, and estimated timelines.',
  },
  {
    icon: '\u{1F4AC}',
    title: 'AI Learning Assistant',
    desc: 'Chat with our AI to get recommendations, skill gap analysis, course comparisons, and context-aware study guidance.',
  },
  {
    icon: '\u{1F4CA}',
    title: 'Skill Gap Analysis',
    desc: 'See exactly where you stand vs your target role with interactive radar charts. Know your strengths and weaknesses.',
  },
  {
    icon: '\u{1F517}',
    title: 'Knowledge Graph',
    desc: 'Explore an interactive force-directed graph of 80+ courses and their prerequisite relationships.',
  },
  {
    icon: '\u{1F504}',
    title: 'Adaptive Feedback',
    desc: 'Rate course difficulty and relevance after completion. The system adapts future recommendations based on your feedback.',
  },
];

const STATS = [
  { value: '80+', label: 'Courses' },
  { value: '110K+', label: 'Reviews Analyzed' },
  { value: '8', label: 'Career Paths' },
  { value: '12', label: 'Skill Domains' },
];

const STEPS = [
  { num: '01', title: 'Create Your Profile', desc: 'Tell us your career goals, experience level, and interests in a quick onboarding flow.', icon: '👤' },
  { num: '02', title: 'Get AI Recommendations', desc: 'Our ML engine analyzes your profile and generates a personalized learning path with prerequisites.', icon: '🤖' },
  { num: '03', title: 'Learn & Track Progress', desc: 'Follow your roadmap, track progress, get skill gap analysis, and adapt your path as you grow.', icon: '📈' },
];

const TECH_STACK = [
  { name: 'React', color: '#61DAFB' },
  { name: 'FastAPI', color: '#009688' },
  { name: 'Python', color: '#3776AB' },
  { name: 'scikit-learn', color: '#F7931E' },
  { name: 'TF-IDF', color: '#9966FF' },
  { name: 'SQLite', color: '#003B57' },
  { name: 'Vite', color: '#646CFF' },
  { name: 'Canvas API', color: '#FF6384' },
];

export default function Landing() {
  const navigate = useNavigate();

  return (
    <div className="landing">
      <NeuralParticles />
      <div className="bg-mesh" />

      {/* Header */}
      <header className="landing-header">
        <div className="landing-logo">
          <div className="sidebar-logo-icon">PF</div>
          <span className="landing-brand">PathFinder</span>
        </div>
      </header>

      {/* Hero 3D Split Layout */}
      <section className="hero-3d-split">
        <div className="hero-content">
          <div className="hero-badge">AI-Powered Learning Platform</div>
          <h1 className="hero-title">
            Find Your Perfect <br />
            <span className="gradient-text">Learning Path</span>
          </h1>
          <p className="hero-subtitle">
            Tell us your career goals and we'll create a personalized learning roadmap
            powered by AI analysis of 110,000+ course reviews across 80+ courses.
          </p>
          <div className="hero-actions">
            <button className="btn btn-primary btn-lg" onClick={() => navigate('/onboarding')}>
              Get Started Free
            </button>
            <button className="btn btn-secondary btn-lg" onClick={() => document.getElementById('how-it-works').scrollIntoView({ behavior: 'smooth' })}>
              How It Works
            </button>
          </div>
          
          <div className="hero-stats">
            {STATS.map((s) => (
              <div key={s.label} className="hero-stat">
                <div className="hero-stat-value">{s.value}</div>
                <div className="hero-stat-label">{s.label}</div>
              </div>
            ))}
          </div>
        </div>
        
        <div className="hero-image-container">
          <div className="hero-glow-orb"></div>
          <div className="hero-3d-graphic">
            <div className="hero-orb-ring ring-1" />
            <div className="hero-orb-ring ring-2" />
            <div className="hero-orb-ring ring-3" />
            <div className="hero-orb-center">
              <span>PF</span>
            </div>
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section id="how-it-works" className="how-it-works-section">
        <h2 className="section-title">How It Works</h2>
        <p className="section-subtitle">Three simple steps to your personalized learning journey</p>
        <div className="steps-flow">
          {STEPS.map((step, i) => (
            <div key={step.num} className="step-card" style={{ animationDelay: `${i * 0.15}s` }}>
              <div className="step-number">{step.num}</div>
              <div className="step-icon">{step.icon}</div>
              <h3>{step.title}</h3>
              <p>{step.desc}</p>
              {i < STEPS.length - 1 && <div className="step-connector" />}
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
            <div key={f.title} className="feature-card premium-3d-card">
              <div className="feature-icon">{f.icon}</div>
              <h3>{f.title}</h3>
              <p>{f.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Tech Stack */}
      <section className="tech-stack-section">
        <h2 className="section-title">Built With</h2>
        <div className="tech-badges">
          {TECH_STACK.map(t => (
            <div key={t.name} className="tech-badge" style={{ borderColor: t.color + '44', color: t.color }}>
              <span className="tech-dot" style={{ background: t.color }} />
              {t.name}
            </div>
          ))}
        </div>
      </section>

      {/* CTA */}
      <section className="cta-section">
        <div className="cta-card premium-3d-card float-anim">
          <h2>Ready to start your journey?</h2>
          <p>Create your learner profile in 60 seconds and get personalized AI-powered recommendations.</p>
          <button className="btn btn-primary btn-lg" onClick={() => navigate('/onboarding')}>
            Create Your Profile
          </button>
        </div>
      </section>

      <footer className="landing-footer">
        <p>PathFinder — AI-Powered Personalized Learning Path Recommender</p>
        <p className="text-muted">Built for HCLTech AMPlified Season 1 — 2026 | Team MIET-4</p>
      </footer>
    </div>
  );
}
