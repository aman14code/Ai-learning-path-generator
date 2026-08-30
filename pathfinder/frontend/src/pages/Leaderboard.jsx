import { useState } from 'react';
import './Leaderboard.css';

export default function Leaderboard({ user }) {
  // Mock data for hackathon demo
  const mockLeaderboard = [
    { rank: 1, name: "Alex Chen", badges: 14, hours: 120, domain: "AI/ML" },
    { rank: 2, name: "Sarah Jenkins", badges: 12, hours: 95, domain: "Web Dev" },
    { rank: 3, name: user?.name || "You", badges: 4, hours: 12, domain: "General", isUser: true },
    { rank: 4, name: "David Kim", badges: 8, hours: 75, domain: "Cloud" },
    { rank: 5, name: "Maria Garcia", badges: 7, hours: 62, domain: "Data Science" },
    { rank: 6, name: "James Wilson", badges: 5, hours: 40, domain: "Cybersecurity" },
    { rank: 7, name: "Emily Wang", badges: 3, hours: 25, domain: "Web Dev" },
  ];

  const [activeTab, setActiveTab] = useState('global');

  return (
    <div className="container" style={{ padding: '40px 20px', maxWidth: '800px', margin: '0 auto' }}>
      <div style={{ textAlign: 'center', marginBottom: '40px' }}>
        <h1 className="gradient-text" style={{ fontSize: '2.5rem', marginBottom: '10px' }}>Global Leaderboard</h1>
        <p className="text-muted">See how you rank among other learners worldwide.</p>
      </div>

      <div className="premium-3d-card" style={{ padding: '24px' }}>
        <div style={{ display: 'flex', gap: '12px', marginBottom: '24px' }}>
          <button 
            className={`btn ${activeTab === 'global' ? 'btn-primary' : ''}`}
            onClick={() => setActiveTab('global')}
            style={activeTab !== 'global' ? { background: 'var(--bg-glass)', border: '1px solid rgba(255,255,255,0.1)' } : {}}
          >
            🌎 Global
          </button>
          <button 
            className={`btn ${activeTab === 'friends' ? 'btn-primary' : ''}`}
            onClick={() => setActiveTab('friends')}
            style={activeTab !== 'friends' ? { background: 'var(--bg-glass)', border: '1px solid rgba(255,255,255,0.1)' } : {}}
          >
            👥 Friends
          </button>
        </div>

        <div className="leaderboard-list">
          {mockLeaderboard.map((u) => (
            <div 
              key={u.rank} 
              className="glass-card" 
              style={{ 
                display: 'flex', 
                alignItems: 'center', 
                padding: '16px 20px', 
                marginBottom: '12px',
                border: u.isUser ? '1px solid #6366f1' : '1px solid rgba(255,255,255,0.05)',
                background: u.isUser ? 'rgba(99, 102, 241, 0.1)' : 'var(--bg-glass)',
                transform: u.isUser ? 'scale(1.02)' : 'scale(1)',
                transition: 'transform 0.2s ease',
              }}
            >
              <div style={{ 
                width: '40px', 
                fontSize: '1.2rem', 
                fontWeight: 'bold', 
                color: u.rank <= 3 ? '#fbbf24' : '#94a3b8' 
              }}>
                #{u.rank}
              </div>
              
              <div style={{ flex: 1 }}>
                <h4 style={{ margin: 0, display: 'flex', alignItems: 'center', gap: '8px' }}>
                  {u.name} {u.isUser && <span className="badge badge-beginner">You</span>}
                </h4>
                <div style={{ fontSize: '0.85rem', color: '#94a3b8', marginTop: '4px' }}>
                  {u.domain}
                </div>
              </div>

              <div style={{ display: 'flex', gap: '24px', textAlign: 'right' }}>
                <div>
                  <div style={{ fontSize: '1.2rem', fontWeight: 'bold' }}>{u.badges}</div>
                  <div style={{ fontSize: '0.75rem', color: '#94a3b8' }}>Badges</div>
                </div>
                <div>
                  <div style={{ fontSize: '1.2rem', fontWeight: 'bold', color: '#6366f1' }}>{u.hours}h</div>
                  <div style={{ fontSize: '0.75rem', color: '#94a3b8' }}>Learning</div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
