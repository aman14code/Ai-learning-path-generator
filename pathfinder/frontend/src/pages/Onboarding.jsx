import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { api } from '../api';
import './Onboarding.css';

const DOMAINS = [
  'Python', 'Web Development', 'Data Science', 'Machine Learning',
  'Cloud & DevOps', 'Mobile Development', 'Database', 'Security',
  'Programming', 'Data Engineering', 'Mathematics', 'Emerging Tech',
];

const GOALS = [
  { key: 'data_scientist', label: 'Data Scientist', icon: '\u{1F4CA}' },
  { key: 'web_developer', label: 'Full Stack Developer', icon: '\u{1F310}' },
  { key: 'ml_engineer', label: 'ML Engineer', icon: '\u{1F9E0}' },
  { key: 'devops_engineer', label: 'DevOps Engineer', icon: '\u2699\uFE0F' },
  { key: 'mobile_developer', label: 'Mobile Developer', icon: '\u{1F4F1}' },
  { key: 'data_engineer', label: 'Data Engineer', icon: '\u{1F6E0}\uFE0F' },
  { key: 'ai_specialist', label: 'AI Specialist', icon: '\u{1F916}' },
  { key: 'cybersecurity_analyst', label: 'Security Analyst', icon: '\u{1F6E1}\uFE0F' },
];

export default function Onboarding({ onComplete }) {
  const navigate = useNavigate();
  const [step, setStep] = useState(0);
  const [loading, setLoading] = useState(false);
  const [form, setForm] = useState({
    name: '',
    email: '',
    experience_level: 'beginner',
    interests: [],
    goals: '',
    selectedGoal: '',
  });

  const steps = [
    { title: 'Welcome', subtitle: "Let's personalize your learning experience" },
    { title: 'Your Goal', subtitle: 'What career are you aiming for?' },
    { title: 'Your Level', subtitle: "Where are you in your journey?" },
    { title: 'Your Interests', subtitle: 'Select topics that excite you' },
  ];

  const canNext = () => {
    if (step === 0) return form.name.trim().length > 0;
    if (step === 1) return form.selectedGoal || form.goals.trim().length > 0;
    return true;
  };

  const handleNext = async () => {
    if (step < steps.length - 1) {
      setStep(step + 1);
      return;
    }

    // Final step — create profile
    setLoading(true);
    try {
      const goalText = form.selectedGoal
        ? GOALS.find(g => g.key === form.selectedGoal)?.label || form.goals
        : form.goals;

      const result = await api.createProfile({
        name: form.name,
        email: form.email,
        experience_level: form.experience_level,
        interests: form.interests,
        goals: goalText,
      });

      // Fetch full profile
      const profile = await api.getProfile(result.user_id);
      onComplete(profile);
      navigate('/dashboard');
    } catch (err) {
      console.error('Failed to create profile:', err);
      // Fallback: create local profile
      const localProfile = {
        id: 'local_' + Date.now(),
        name: form.name,
        experience_level: form.experience_level,
        interests: form.interests,
        goals: form.selectedGoal || form.goals,
        completed_courses: [],
      };
      onComplete(localProfile);
      navigate('/dashboard');
    } finally {
      setLoading(false);
    }
  };

  const toggleInterest = (domain) => {
    setForm(prev => ({
      ...prev,
      interests: prev.interests.includes(domain)
        ? prev.interests.filter(d => d !== domain)
        : [...prev.interests, domain],
    }));
  };

  return (
    <div className="onboarding">
      <div className="bg-mesh" />

      <div className="onboarding-container">
        {/* Progress */}
        <div className="onboarding-progress">
          {steps.map((_, i) => (
            <div key={i} className={`progress-dot ${i <= step ? 'active' : ''} ${i < step ? 'completed' : ''}`} />
          ))}
        </div>

        <div className="onboarding-card glass-card animate-scale-in" key={step}>
          <h2>{steps[step].title}</h2>
          <p className="onboarding-subtitle">{steps[step].subtitle}</p>

          {/* Step 0: Name */}
          {step === 0 && (
            <div className="onboarding-form">
              <div className="input-group">
                <label className="input-label">Your Name</label>
                <input
                  className="input"
                  type="text"
                  placeholder="Enter your name"
                  value={form.name}
                  onChange={e => setForm({ ...form, name: e.target.value })}
                  autoFocus
                />
              </div>
              <div className="input-group">
                <label className="input-label">Email (optional)</label>
                <input
                  className="input"
                  type="email"
                  placeholder="your@email.com"
                  value={form.email}
                  onChange={e => setForm({ ...form, email: e.target.value })}
                />
              </div>
            </div>
          )}

          {/* Step 1: Goal */}
          {step === 1 && (
            <div className="onboarding-form">
              <div className="goal-grid">
                {GOALS.map(g => (
                  <button
                    key={g.key}
                    className={`goal-card ${form.selectedGoal === g.key ? 'selected' : ''}`}
                    onClick={() => setForm({ ...form, selectedGoal: g.key })}
                  >
                    <span className="goal-icon">{g.icon}</span>
                    <span className="goal-label">{g.label}</span>
                  </button>
                ))}
              </div>
              <div className="input-group" style={{ marginTop: 16 }}>
                <label className="input-label">Or describe your goal</label>
                <input
                  className="input"
                  type="text"
                  placeholder="e.g., I want to become a machine learning engineer"
                  value={form.goals}
                  onChange={e => setForm({ ...form, goals: e.target.value, selectedGoal: '' })}
                />
              </div>
            </div>
          )}

          {/* Step 2: Experience */}
          {step === 2 && (
            <div className="onboarding-form">
              <div className="level-options">
                {[
                  { key: 'beginner', label: 'Beginner', desc: 'New to tech / just starting', icon: '\u{1F331}' },
                  { key: 'intermediate', label: 'Intermediate', desc: '1-2 years of experience', icon: '\u{1F33F}' },
                  { key: 'advanced', label: 'Advanced', desc: '3+ years, looking to specialize', icon: '\u{1F333}' },
                ].map(level => (
                  <button
                    key={level.key}
                    className={`level-card ${form.experience_level === level.key ? 'selected' : ''}`}
                    onClick={() => setForm({ ...form, experience_level: level.key })}
                  >
                    <span className="level-icon">{level.icon}</span>
                    <span className="level-label">{level.label}</span>
                    <span className="level-desc">{level.desc}</span>
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Step 3: Interests */}
          {step === 3 && (
            <div className="onboarding-form">
              <div className="interest-tags">
                {DOMAINS.map(d => (
                  <button
                    key={d}
                    className={`interest-tag ${form.interests.includes(d) ? 'selected' : ''}`}
                    onClick={() => toggleInterest(d)}
                  >
                    {d}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Actions */}
          <div className="onboarding-actions">
            {step > 0 && (
              <button className="btn btn-ghost" onClick={() => setStep(step - 1)}>Back</button>
            )}
            <button
              className="btn btn-primary"
              onClick={handleNext}
              disabled={!canNext() || loading}
            >
              {loading ? (
                <span className="spinner" />
              ) : step === steps.length - 1 ? (
                'Create My Path'
              ) : (
                'Continue'
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
