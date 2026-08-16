import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { api } from '../api';
import './Dashboard.css';

export default function Dashboard({ user }) {
  const navigate = useNavigate();
  const [recommendations, setRecommendations] = useState([]);
  const [progress, setProgress] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, [user]);

  async function loadData() {
    setLoading(true);
    try {
      const [recsData, progressData] = await Promise.allSettled([
        api.getRecommendations({
          user_id: user?.id,
          text: user?.goals || 'programming and technology',
          experience_level: user?.experience_level || 'beginner',
          interests: user?.interests || [],
          top_k: 6,
        }),
        user?.id ? api.getProgress(user.id) : Promise.resolve({ stats: { completed: 0, in_progress: 0, total_hours: 0, skill_domains: {} }, progress: [] }),
      ]);

      if (recsData.status === 'fulfilled') setRecommendations(recsData.value.recommendations || []);
      if (progressData.status === 'fulfilled') setProgress(progressData.value);
    } catch (err) {
      console.error('Failed to load dashboard:', err);
    }
    setLoading(false);
  }

  const stats = progress?.stats || { completed: 0, in_progress: 0, total_hours: 0, skill_domains: {} };
  const domains = Object.entries(stats.skill_domains || {});

  return (
    <div className="dashboard animate-fade-in">
      <div className="page-header">
        <h2>Welcome back, {user?.name || 'Learner'}!</h2>
        <p>Here's your learning overview and personalized recommendations.</p>
      </div>

      {/* Stats */}
      <div className="stats-grid stagger">
        <div className="stat-card">
          <div className="stat-icon" style={{ background: 'rgba(99, 102, 241, 0.15)', color: 'var(--accent-primary)' }}>
            &#128218;
          </div>
          <div className="stat-info">
            <h4>{stats.completed}</h4>
            <p>Courses Completed</p>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon" style={{ background: 'rgba(245, 158, 11, 0.15)', color: 'var(--warning)' }}>
            &#9997;
          </div>
          <div className="stat-info">
            <h4>{stats.in_progress}</h4>
            <p>In Progress</p>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon" style={{ background: 'rgba(16, 185, 129, 0.15)', color: 'var(--success)' }}>
            &#9201;
          </div>
          <div className="stat-info">
            <h4>{stats.total_hours}h</h4>
            <p>Hours Invested</p>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon" style={{ background: 'rgba(6, 182, 212, 0.15)', color: 'var(--accent-tertiary)' }}>
            &#127942;
          </div>
          <div className="stat-info">
            <h4>{domains.length}</h4>
            <p>Skill Domains</p>
          </div>
        </div>
      </div>

      <div className="dashboard-grid">
        {/* Recommendations */}
        <div className="dashboard-section">
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

        {/* Quick Actions */}
        <div className="dashboard-section">
          <h3 style={{ marginBottom: 16 }}>Quick Actions</h3>
          <div className="quick-actions stagger">
            <button className="action-card premium-3d-card" onClick={() => navigate('/learning-path')}>
              <span className="action-icon">&#128736;</span>
              <div>
                <h4>Generate Learning Path</h4>
                <p>Create a structured roadmap for your goals</p>
              </div>
            </button>
            <button className="action-card premium-3d-card" onClick={() => navigate('/chat')}>
              <span className="action-icon">&#128172;</span>
              <div>
                <h4>Ask AI Assistant</h4>
                <p>Get personalized advice and recommendations</p>
              </div>
            </button>
            <button className="action-card premium-3d-card" onClick={() => navigate('/courses')}>
              <span className="action-icon">&#128218;</span>
              <div>
                <h4>Browse Courses</h4>
                <p>Explore 80+ courses across 12 domains</p>
              </div>
            </button>
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
        </div>
      </div>
    </div>
  );
}
