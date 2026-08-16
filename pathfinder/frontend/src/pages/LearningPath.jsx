import { useState, useEffect } from 'react';
import { api } from '../api';
import './LearningPath.css';

export default function LearningPath({ user, setUser }) {
  const [path, setPath] = useState(null);
  const [careerPaths, setCareerPaths] = useState([]);
  const [loading, setLoading] = useState(false);
  const [goalInput, setGoalInput] = useState(user?.goals || '');
  const [showGenerator, setShowGenerator] = useState(true);

  useEffect(() => {
    api.getCareerPaths()
      .then(data => setCareerPaths(data.career_paths || []))
      .catch(() => {});

    // Auto-generate if user has a goal
    if (user?.goals) {
      generatePath(user.goals);
    }
  }, []);

  async function generatePath(goal) {
    setLoading(true);
    try {
      const result = await api.generatePath({
        user_id: user?.id,
        goal: goal,
        experience_level: user?.experience_level || 'beginner',
        completed_courses: user?.completed_courses || [],
        interests: user?.interests || [],
      });
      setPath(result);
      setShowGenerator(false);
    } catch (err) {
      console.error('Failed to generate path:', err);
    }
    setLoading(false);
  }

  async function markCourse(courseName, status) {
    if (!user?.id) return;
    try {
      await api.updateProgress({
        user_id: user.id,
        course_name: courseName,
        status: status,
        progress_percent: status === 'completed' ? 100 : status === 'in_progress' ? 50 : 0,
      });
      // Update local state
      if (status === 'completed' && setUser) {
        const updated = { ...user, completed_courses: [...(user.completed_courses || []), courseName] };
        setUser(updated);
      }
    } catch (err) {
      console.error('Failed to update progress:', err);
    }
  }

  const completedSet = new Set(user?.completed_courses || []);

  return (
    <div className="learning-path-page animate-fade-in">
      <div className="page-header">
        <h2>Learning Path</h2>
        <p>Your personalized roadmap to achieve your career goals.</p>
      </div>

      {/* Generator */}
      {showGenerator && (
        <div className="path-generator glass-card">
          <h3>Generate Your Learning Path</h3>
          <p>Choose a career path or describe your goal</p>

          <div className="career-path-grid stagger">
            {careerPaths.map(cp => (
              <button
                key={cp.key}
                className="career-path-card"
                onClick={() => { setGoalInput(cp.title); generatePath(cp.title); }}
                disabled={loading}
              >
                <h4>{cp.title}</h4>
                <p>{cp.description}</p>
                <span className="career-course-count">{cp.course_count} courses</span>
              </button>
            ))}
          </div>

          <div className="path-custom" style={{ marginTop: 20 }}>
            <div style={{ display: 'flex', gap: 12 }}>
              <input
                className="input"
                style={{ flex: 1 }}
                type="text"
                placeholder="Or type your goal: e.g., I want to become an AI engineer"
                value={goalInput}
                onChange={e => setGoalInput(e.target.value)}
                onKeyDown={e => e.key === 'Enter' && goalInput && generatePath(goalInput)}
              />
              <button
                className="btn btn-primary"
                onClick={() => generatePath(goalInput)}
                disabled={!goalInput || loading}
              >
                {loading ? <span className="spinner" /> : 'Generate'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Path Display */}
      {path && (
        <div className="path-result animate-fade-in">
          <div className="path-header glass-card">
            <div className="path-header-info">
              <h3>{path.career_path || 'Custom Path'}</h3>
              {path.career_description && <p>{path.career_description}</p>}
            </div>
            <div className="path-stats">
              <div className="path-stat">
                <strong>{path.total_courses}</strong>
                <span>Courses</span>
              </div>
              <div className="path-stat">
                <strong>{path.total_hours}h</strong>
                <span>Total Time</span>
              </div>
              <div className="path-stat">
                <strong>~{path.estimated_weeks}w</strong>
                <span>Duration</span>
              </div>
            </div>
            <button className="btn btn-secondary btn-sm" onClick={() => setShowGenerator(true)}>
              Change Goal
            </button>
          </div>

          {/* Milestones */}
          <div className="milestones">
            {path.milestones?.map((milestone, mi) => (
              <div key={mi} className="milestone animate-fade-in" style={{ animationDelay: `${mi * 0.1}s` }}>
                <div className="milestone-header">
                  <div className="milestone-badge">
                    <span className="milestone-number">{mi + 1}</span>
                  </div>
                  <h4>{milestone.title}</h4>
                  <span className="milestone-count">{milestone.courses.length} courses</span>
                </div>

                <div className="milestone-courses">
                  {milestone.courses.map((courseName) => {
                    const courseInfo = path.courses?.find(c => c.name === courseName) || {};
                    const isCompleted = completedSet.has(courseName);

                    return (
                      <div key={courseName} className={`path-course-card glass-card ${isCompleted ? 'completed' : ''}`}>
                        <div className="path-course-status">
                          {isCompleted ? (
                            <div className="status-check">&#10003;</div>
                          ) : (
                            <div className="status-circle" />
                          )}
                        </div>
                        <div className="path-course-info">
                          <h5>{courseName}</h5>
                          <p>{courseInfo.description || ''}</p>
                          <div className="path-course-meta">
                            <span className="tag">{courseInfo.domain || 'General'}</span>
                            <span className="path-duration">{courseInfo.duration_hours || 20}h</span>
                            {courseInfo.skills?.slice(0, 3).map(s => (
                              <span key={s} className="tag">{s}</span>
                            ))}
                          </div>
                        </div>
                        <div className="path-course-actions">
                          {!isCompleted && (
                            <>
                              <button className="btn btn-sm btn-ghost" onClick={() => markCourse(courseName, 'in_progress')}>
                                Start
                              </button>
                              <button className="btn btn-sm btn-primary" onClick={() => markCourse(courseName, 'completed')}>
                                Done
                              </button>
                            </>
                          )}
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
