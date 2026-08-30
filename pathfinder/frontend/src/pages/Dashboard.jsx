import { useState, useEffect, useRef, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { api } from '../api';
import './Dashboard.css';

/* ---- Animated Counter Hook ---- */
function useAnimatedCounter(target, duration = 1200) {
  const [count, setCount] = useState(0);
  useEffect(() => {
    if (target === 0) { setCount(0); return; }
    let start = 0;
    const step = Math.max(1, Math.ceil(target / (duration / 16)));
    const timer = setInterval(() => {
      start += step;
      if (start >= target) { setCount(target); clearInterval(timer); }
      else setCount(start);
    }, 16);
    return () => clearInterval(timer);
  }, [target, duration]);
  return count;
}

/* ---- Skill Radar Chart (Pure Canvas) ---- */
function SkillRadarChart({ currentSkills, requiredSkills, size = 300 }) {
  const canvasRef = useRef(null);

  const draw = useCallback(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    const dpr = window.devicePixelRatio || 1;
    canvas.width = size * dpr;
    canvas.height = size * dpr;
    ctx.scale(dpr, dpr);
    canvas.style.width = size + 'px';
    canvas.style.height = size + 'px';

    const cx = size / 2, cy = size / 2;
    const radius = size / 2 - 40;
    const domains = Object.keys(requiredSkills || {});
    if (domains.length < 3) return;
    const n = domains.length;
    const angleStep = (2 * Math.PI) / n;

    ctx.clearRect(0, 0, size, size);

    // Draw grid rings
    for (let ring = 1; ring <= 4; ring++) {
      const r = (radius * ring) / 4;
      ctx.beginPath();
      for (let i = 0; i <= n; i++) {
        const angle = i * angleStep - Math.PI / 2;
        const x = cx + r * Math.cos(angle);
        const y = cy + r * Math.sin(angle);
        i === 0 ? ctx.moveTo(x, y) : ctx.lineTo(x, y);
      }
      ctx.closePath();
      ctx.strokeStyle = 'rgba(255,255,255,0.08)';
      ctx.lineWidth = 1;
      ctx.stroke();
    }

    // Draw axis lines + labels
    ctx.font = '11px Inter, sans-serif';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    for (let i = 0; i < n; i++) {
      const angle = i * angleStep - Math.PI / 2;
      const x = cx + radius * Math.cos(angle);
      const y = cy + radius * Math.sin(angle);
      ctx.beginPath();
      ctx.moveTo(cx, cy);
      ctx.lineTo(x, y);
      ctx.strokeStyle = 'rgba(255,255,255,0.06)';
      ctx.lineWidth = 1;
      ctx.stroke();

      // Label
      const lx = cx + (radius + 24) * Math.cos(angle);
      const ly = cy + (radius + 24) * Math.sin(angle);
      ctx.fillStyle = '#94a3b8';
      const label = domains[i].length > 12 ? domains[i].slice(0, 11) + '…' : domains[i];
      ctx.fillText(label, lx, ly);
    }

    // Draw required skills polygon (target)
    ctx.beginPath();
    for (let i = 0; i <= n; i++) {
      const idx = i % n;
      const angle = idx * angleStep - Math.PI / 2;
      const val = (requiredSkills[domains[idx]] || 0) / 100;
      const x = cx + radius * val * Math.cos(angle);
      const y = cy + radius * val * Math.sin(angle);
      i === 0 ? ctx.moveTo(x, y) : ctx.lineTo(x, y);
    }
    ctx.closePath();
    ctx.fillStyle = 'rgba(239, 68, 68, 0.08)';
    ctx.fill();
    ctx.strokeStyle = 'rgba(239, 68, 68, 0.4)';
    ctx.lineWidth = 2;
    ctx.setLineDash([6, 4]);
    ctx.stroke();
    ctx.setLineDash([]);

    // Draw current skills polygon
    ctx.beginPath();
    for (let i = 0; i <= n; i++) {
      const idx = i % n;
      const angle = idx * angleStep - Math.PI / 2;
      const val = (currentSkills[domains[idx]] || 0) / 100;
      const x = cx + radius * val * Math.cos(angle);
      const y = cy + radius * val * Math.sin(angle);
      i === 0 ? ctx.moveTo(x, y) : ctx.lineTo(x, y);
    }
    ctx.closePath();
    const grad = ctx.createRadialGradient(cx, cy, 0, cx, cy, radius);
    grad.addColorStop(0, 'rgba(99, 102, 241, 0.35)');
    grad.addColorStop(1, 'rgba(6, 182, 212, 0.15)');
    ctx.fillStyle = grad;
    ctx.fill();
    ctx.strokeStyle = '#6366f1';
    ctx.lineWidth = 2.5;
    ctx.stroke();

    // Draw dots on current polygon
    for (let i = 0; i < n; i++) {
      const angle = i * angleStep - Math.PI / 2;
      const val = (currentSkills[domains[i]] || 0) / 100;
      const x = cx + radius * val * Math.cos(angle);
      const y = cy + radius * val * Math.sin(angle);
      ctx.beginPath();
      ctx.arc(x, y, 4, 0, Math.PI * 2);
      ctx.fillStyle = '#6366f1';
      ctx.fill();
      ctx.strokeStyle = '#fff';
      ctx.lineWidth = 1.5;
      ctx.stroke();
    }
  }, [currentSkills, requiredSkills, size]);

  useEffect(() => { draw(); }, [draw]);

  return (
    <div className="radar-chart-wrapper">
      <canvas ref={canvasRef} />
      <div className="radar-legend">
        <span className="legend-item"><span className="legend-dot current" /> Your Skills</span>
        <span className="legend-item"><span className="legend-dot required" /> Target Role</span>
      </div>
    </div>
  );
}

/* ---- Readiness Gauge ---- */
function ReadinessGauge({ value }) {
  const animatedValue = useAnimatedCounter(Math.round(value));
  const circumference = 2 * Math.PI * 54;
  const offset = circumference - (animatedValue / 100) * circumference;
  const color = value >= 75 ? '#10b981' : value >= 40 ? '#f59e0b' : '#ef4444';

  return (
    <div className="readiness-gauge">
      <svg width="130" height="130" viewBox="0 0 120 120">
        <circle cx="60" cy="60" r="54" fill="none" stroke="rgba(255,255,255,0.06)" strokeWidth="8" />
        <circle
          cx="60" cy="60" r="54" fill="none"
          stroke={color} strokeWidth="8" strokeLinecap="round"
          strokeDasharray={circumference} strokeDashoffset={offset}
          transform="rotate(-90 60 60)"
          style={{ transition: 'stroke-dashoffset 1.5s ease' }}
        />
      </svg>
      <div className="gauge-value" style={{ color }}>
        <span className="gauge-number">{animatedValue}%</span>
        <span className="gauge-label">Ready</span>
      </div>
    </div>
  );
}

/* ---- Main Dashboard ---- */
export default function Dashboard({ user }) {
  const navigate = useNavigate();
  const [recommendations, setRecommendations] = useState([]);
  const [progress, setProgress] = useState(null);
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, [user]);

  async function loadData() {
    setLoading(true);
    try {
      const promises = [
        api.getRecommendations({
          user_id: user?.id,
          text: user?.goals || 'programming and technology',
          experience_level: user?.experience_level || 'beginner',
          interests: user?.interests || [],
          top_k: 6,
        }),
        user?.id ? api.getProgress(user.id) : Promise.resolve({
          stats: { completed: 0, in_progress: 0, total_hours: 0, skill_domains: {} },
          progress: [],
        }),
        user?.id ? api.getAnalytics(user.id) : Promise.resolve({ velocity: null, skill_gap: null }),
      ];

      const [recsData, progressData, analyticsData] = await Promise.allSettled(promises);

      if (recsData.status === 'fulfilled') setRecommendations(recsData.value.recommendations || []);
      if (progressData.status === 'fulfilled') setProgress(progressData.value);
      if (analyticsData.status === 'fulfilled') setAnalytics(analyticsData.value);
    } catch (err) {
      console.error('Failed to load dashboard:', err);
    }
    setLoading(false);
  }

  const stats = progress?.stats || { completed: 0, in_progress: 0, total_hours: 0, skill_domains: {} };
  const domains = Object.entries(stats.skill_domains || {});
  const skillGap = analytics?.skill_gap;
  const velocity = analytics?.velocity;

  const completedAnimated = useAnimatedCounter(stats.completed);
  const inProgressAnimated = useAnimatedCounter(stats.in_progress);
  const hoursAnimated = useAnimatedCounter(stats.total_hours);
  const domainsAnimated = useAnimatedCounter(domains.length);

  return (
    <div className="dashboard animate-fade-in">
      <div className="page-header">
        <h2>Welcome back, {user?.name || 'Learner'}! 👋</h2>
        <p>Here's your learning overview and personalized recommendations.</p>
      </div>

      {/* Stats */}
      <div className="stats-grid stagger">
        <div className="stat-card">
          <div className="stat-icon" style={{ background: 'rgba(99, 102, 241, 0.15)', color: 'var(--accent-primary)' }}>
            📚
          </div>
          <div className="stat-info">
            <h4>{completedAnimated}</h4>
            <p>Courses Completed</p>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon" style={{ background: 'rgba(245, 158, 11, 0.15)', color: 'var(--warning)' }}>
            ✍
          </div>
          <div className="stat-info">
            <h4>{inProgressAnimated}</h4>
            <p>In Progress</p>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon" style={{ background: 'rgba(16, 185, 129, 0.15)', color: 'var(--success)' }}>
            ⏱
          </div>
          <div className="stat-info">
            <h4>{hoursAnimated}h</h4>
            <p>Hours Invested</p>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon" style={{ background: 'rgba(6, 182, 212, 0.15)', color: 'var(--accent-tertiary)' }}>
            🏆
          </div>
          <div className="stat-info">
            <h4>{domainsAnimated}</h4>
            <p>Skill Domains</p>
          </div>
        </div>
      </div>

      {/* Learning Velocity Banner */}
      {velocity && velocity.pace_label !== 'getting_started' && (
        <div className="velocity-banner glass-card animate-fade-in">
          <div className="velocity-info">
            <div className="velocity-streak">
              <span className="streak-fire">🔥</span>
              <span className="streak-count">{velocity.current_streak} day streak</span>
            </div>
            <div className="velocity-pace">
              <span className={`pace-badge pace-${velocity.pace_label}`}>
                {velocity.pace_label === 'fast' ? '⚡ Fast Pace' : velocity.pace_label === 'steady' ? '📈 Steady' : '🌱 Building'}
              </span>
              <span className="pace-detail">{velocity.courses_per_week} courses/week</span>
            </div>
          </div>
          {velocity.total_active_days > 0 && (
            <div className="velocity-stat">
              <strong>{velocity.total_active_days}</strong>
              <span>Active Days</span>
            </div>
          )}
        </div>
      )}

      <div className="dashboard-grid">
        {/* Left Column — Recommendations + Skill Gap */}
        <div className="dashboard-section">
          {/* Skill Radar */}
          {skillGap && (
            <div className="skill-radar-section glass-card animate-fade-in" style={{ marginBottom: 24 }}>
              <div className="radar-header">
                <div>
                  <h3>Skill Gap Analysis</h3>
                  <p className="text-muted">Your skills vs {skillGap.target_role} requirements</p>
                </div>
                <ReadinessGauge value={skillGap.overall_readiness} />
              </div>
              <SkillRadarChart
                currentSkills={skillGap.current_skills}
                requiredSkills={skillGap.required_skills}
                size={320}
              />
              {/* Gap highlights */}
              {skillGap.weaknesses?.length > 0 && (
                <div className="gap-highlights">
                  <h4>Focus Areas</h4>
                  <div className="gap-items">
                    {skillGap.weaknesses.slice(0, 4).map(w => (
                      <div key={w.domain} className="gap-item">
                        <span className="gap-domain">{w.domain}</span>
                        <div className="gap-bar-wrapper">
                          <div className="gap-bar" style={{ width: `${Math.min(100, w.gap)}%` }} />
                        </div>
                        <span className="gap-value">-{w.gap}%</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Recommendations */}
          <div className="section-header">
            <h3>Recommended For You</h3>
            <button className="btn btn-ghost btn-sm" onClick={() => navigate('/courses')}>
              View All
            </button>
          </div>

          {loading ? (
            <div className="cards-grid stagger">
              {[1, 2, 3].map(i => (
                <div key={i} className="premium-3d-card" style={{ height: 160, padding: 20 }}>
                  <div className="skeleton" style={{ height: 20, width: '60%', marginBottom: 12 }} />
                  <div className="skeleton" style={{ height: 14, width: '40%', marginBottom: 20 }} />
                  <div className="skeleton" style={{ height: 14, width: '80%' }} />
                </div>
              ))}
            </div>
          ) : (
            <div className="cards-grid stagger">
              {recommendations.map((rec, i) => (
                <div key={i} className="course-rec-card premium-3d-card">
                  <div className="rec-header">
                    <h4>{rec.course}</h4>
                    <span className={`badge badge-${rec.difficulty?.toLowerCase()}`}>
                      {rec.difficulty}
                    </span>
                  </div>
                  <div className="rec-domain">{rec.domain}</div>
                  <p className="rec-explanation">{rec.explanation}</p>
                  <div className="rec-footer">
                    <div className="rec-tags">
                      {rec.keywords?.slice(0, 3).map(kw => (
                        <span key={kw} className="tag">{kw}</span>
                      ))}
                    </div>
                    <div className="rec-score">
                      {Math.round(rec.score * 100)}% match
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Right Column — Quick Actions + Skills */}
        <div className="dashboard-section">
          <h3 style={{ marginBottom: 16 }}>Quick Actions</h3>
          <div className="quick-actions stagger">
            <button className="action-card premium-3d-card" onClick={() => navigate('/learning-path')}>
              <span className="action-icon">🛠</span>
              <div>
                <h4>Generate Learning Path</h4>
                <p>Create a structured roadmap for your goals</p>
              </div>
            </button>
            <button className="action-card premium-3d-card" onClick={() => navigate('/chat')}>
              <span className="action-icon">💬</span>
              <div>
                <h4>Ask AI Assistant</h4>
                <p>Get personalized advice and recommendations</p>
              </div>
            </button>
            <button className="action-card premium-3d-card" onClick={() => navigate('/skill-graph')}>
              <span className="action-icon">🗺️</span>
              <div>
                <h4>Knowledge Graph</h4>
                <p>Explore course prerequisites interactively</p>
              </div>
            </button>
            <button className="action-card premium-3d-card" onClick={() => navigate('/courses')}>
              <span className="action-icon">📚</span>
              <div>
                <h4>Browse Courses</h4>
                <p>Explore 80+ courses across 12 domains</p>
              </div>
            </button>
          </div>

          {/* Gamification / Badges */}
          <div style={{ marginTop: 24 }}>
            <h3 style={{ marginBottom: 16 }}>Your Badges</h3>
            <div className="badges-grid stagger">
              <div className={`badge-card ${stats.completed >= 1 ? 'unlocked' : 'locked'}`} title={stats.completed >= 1 ? "Earned by completing your first course!" : "Complete 1 course to unlock"}>
                <div className="badge-icon">{stats.completed >= 1 ? '🌟' : '🔒'}</div>
                <div className="badge-info">
                  <h5>First Steps</h5>
                  <p>1st Course</p>
                </div>
              </div>
              <div className={`badge-card ${stats.completed >= 3 ? 'unlocked' : 'locked'}`} title={stats.completed >= 3 ? "Earned by completing 3 courses!" : "Complete 3 courses to unlock"}>
                <div className="badge-icon">{stats.completed >= 3 ? '🔥' : '🔒'}</div>
                <div className="badge-info">
                  <h5>On Fire</h5>
                  <p>3 Courses</p>
                </div>
              </div>
              <div className={`badge-card ${stats.total_hours >= 10 ? 'unlocked' : 'locked'}`} title={stats.total_hours >= 10 ? "Earned by dedicating 10+ hours to learning!" : "Learn for 10 hours to unlock"}>
                <div className="badge-icon">{stats.total_hours >= 10 ? '⏳' : '🔒'}</div>
                <div className="badge-info">
                  <h5>Dedicated</h5>
                  <p>10+ Hours</p>
                </div>
              </div>
              <div className={`badge-card ${domains.length >= 3 ? 'unlocked' : 'locked'}`} title={domains.length >= 3 ? "Earned by learning in 3+ different domains!" : "Learn 3+ domains to unlock"}>
                <div className="badge-icon">{domains.length >= 3 ? '🧠' : '🔒'}</div>
                <div className="badge-info">
                  <h5>Polymath</h5>
                  <p>3+ Domains</p>
                </div>
              </div>
            </div>
          </div>

          {/* Skill Domains */}
          {domains.length > 0 && (
            <div style={{ marginTop: 24 }}>
              <h3 style={{ marginBottom: 16 }}>Your Skills</h3>
              <div className="skill-bars">
                {domains.map(([domain, count]) => (
                  <div key={domain} className="skill-bar-item">
                    <div className="skill-bar-label">
                      <span>{domain}</span>
                      <span className="text-muted">{count} courses</span>
                    </div>
                    <div className="progress-bar">
                      <div className="progress-bar-fill" style={{ width: `${Math.min(100, count * 20)}%` }} />
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Gap Courses */}
          {skillGap?.gap_courses?.length > 0 && (
            <div style={{ marginTop: 24 }}>
              <h3 style={{ marginBottom: 16 }}>Courses to Close Gaps</h3>
              <div className="gap-courses-list">
                {skillGap.gap_courses.slice(0, 5).map((gc, i) => (
                  <div key={i} className="gap-course-item glass-card">
                    <div className="gap-course-priority">
                      <span className={`priority-dot priority-${gc.priority}`} />
                    </div>
                    <div className="gap-course-info">
                      <h5>{gc.course}</h5>
                      <div className="gap-course-meta">
                        <span className="tag">{gc.domain}</span>
                        <span className={`badge badge-${gc.difficulty?.toLowerCase()}`}>{gc.difficulty}</span>
                        <span className="text-muted" style={{ fontSize: '0.7rem' }}>{gc.hours}h</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
