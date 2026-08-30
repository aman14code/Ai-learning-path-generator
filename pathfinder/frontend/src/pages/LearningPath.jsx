import { useState, useEffect } from 'react';
import { api } from '../api';
import './LearningPath.css';

export default function LearningPath({ user, setUser }) {
  const [path, setPath] = useState(null);
  const [careerPaths, setCareerPaths] = useState([]);
  const [loading, setLoading] = useState(false);
  const [goalInput, setGoalInput] = useState(user?.goals || '');
  const [showGenerator, setShowGenerator] = useState(true);
  const [feedbackCourse, setFeedbackCourse] = useState(null);
  const [feedbackData, setFeedbackData] = useState({ difficulty: 3, relevance: 4 });
  const [showCertificate, setShowCertificate] = useState(false);

  const exportPDF = () => {
    window.print();
  };

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
      if (status === 'completed') {
        if (setUser) {
          const updated = { ...user, completed_courses: [...(user.completed_courses || []), courseName] };
          setUser(updated);
        }
        // Show feedback modal
        setFeedbackCourse(courseName);
      }
    } catch (err) {
      console.error('Failed to update progress:', err);
    }
  }

  async function submitFeedback() {
    if (!user?.id || !feedbackCourse) return;
    try {
      await api.submitFeedback({
        user_id: user.id,
        course_name: feedbackCourse,
        difficulty_rating: feedbackData.difficulty,
        relevance_rating: feedbackData.relevance,
      });
    } catch (err) {
      console.error('Failed to submit feedback:', err);
    }
    setFeedbackCourse(null);
    setFeedbackData({ difficulty: 3, relevance: 4 });
  }

  const completedSet = new Set(user?.completed_courses || []);

  // Calculate timeline
  let cumulativeHours = 0;
  const timelineData = path?.courses?.map((c, i) => {
    const isCompleted = completedSet.has(c.name);
    const hours = c.duration_hours || 20;
    cumulativeHours += hours;
    return {
      ...c,
      isCompleted,
      cumulativeHours,
      weekNumber: Math.ceil(cumulativeHours / 10),
    };
  }) || [];

  const totalWeeks = timelineData.length > 0 ? timelineData[timelineData.length - 1].weekNumber : 0;
  const completedCount = timelineData.filter(c => c.isCompleted).length;
  const progressPercent = timelineData.length > 0 ? (completedCount / timelineData.length * 100) : 0;

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
              {path.ml_powered && (
                <span style={{ display: 'inline-flex', alignItems: 'center', gap: 6, marginTop: 8, padding: '4px 12px', fontSize: '0.7rem', fontWeight: 700, borderRadius: 20, background: 'rgba(99, 102, 241, 0.12)', color: '#818cf8', border: '1px solid rgba(99, 102, 241, 0.3)' }}>
                  🤖 AI-Powered — {path.ml_model || 'TF-IDF + Ensemble SVM'}
                </span>
              )}
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
            <div style={{ display: 'flex', gap: '8px' }}>
              <button className="btn btn-ghost btn-sm" onClick={exportPDF}>
                📄 Export PDF
              </button>
              <button className="btn btn-secondary btn-sm" onClick={() => setShowGenerator(true)}>
                Change Goal
              </button>
            </div>
          </div>

          {/* Overall Progress Bar */}
          <div className="path-progress-bar glass-card">
            <div className="path-progress-info" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div>
                <span className="path-progress-label">
                  Overall Progress: {completedCount}/{timelineData.length} courses
                </span>
                <span className="path-progress-percent" style={{ marginLeft: 8 }}>{progressPercent.toFixed(0)}%</span>
              </div>
              {progressPercent === 100 && (
                <button className="btn btn-sm" style={{ background: 'linear-gradient(135deg, #f59e0b, #facc15)', color: '#000', fontWeight: 'bold' }} onClick={() => setShowCertificate(true)}>
                  🏆 Claim Certificate
                </button>
              )}
            </div>
            <div className="progress-bar" style={{ height: 8 }}>
              <div className="progress-bar-fill" style={{ width: `${progressPercent}%` }} />
            </div>
          </div>

          {/* Visual Timeline */}
          <div className="path-timeline">
            <div className="timeline-track">
              {timelineData.map((course, i) => {
                const widthPercent = 100 / timelineData.length;
                return (
                  <div
                    key={course.name}
                    className={`timeline-node ${course.isCompleted ? 'completed' : ''}`}
                    style={{ width: `${widthPercent}%` }}
                    title={`${course.name} — Week ${course.weekNumber}`}
                  >
                    <div className="timeline-dot" />
                    {i < timelineData.length - 1 && <div className="timeline-line" />}
                  </div>
                );
              })}
            </div>
            <div className="timeline-labels">
              <span>Start</span>
              <span>Week {Math.ceil(totalWeeks / 2)}</span>
              <span>Week {totalWeeks}</span>
            </div>
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
                            <div className="status-check">✓</div>
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
                            {courseInfo.ml_confidence > 0 && (
                              <span className="tag" style={{ background: 'rgba(99, 102, 241, 0.15)', color: '#818cf8', border: '1px solid rgba(99, 102, 241, 0.3)' }}>
                                🤖 {Math.round(courseInfo.ml_confidence * 100)}% match
                              </span>
                            )}
                            {courseInfo.skills?.slice(0, 3).map(s => (
                              <span key={s} className="tag">{s}</span>
                            ))}
                          </div>
                        </div>
                        <div className="path-course-actions">
                          {courseInfo.video_url && (
                            <a 
                              href={courseInfo.video_url} 
                              target="_blank" 
                              rel="noopener noreferrer" 
                              className="btn btn-sm"
                              style={{ background: 'rgba(239, 68, 68, 0.1)', color: '#ef4444', border: '1px solid rgba(239, 68, 68, 0.3)' }}
                              title="Watch related tutorials on YouTube"
                            >
                              ▶ Watch
                            </a>
                          )}
                          <button className="btn btn-sm btn-ghost" onClick={() => {
                            alert(`Knowledge Check: ${courseName}\n\n1. What are the core concepts of this subject?\n2. How would you apply this to a real world problem?\n3. Explain this topic to a beginner.\n\n(AI Quiz Generation Beta)`);
                          }}>
                            📝 Quiz
                          </button>
                          {!isCompleted && (
                            <>
                              <button className="btn btn-sm btn-ghost" onClick={() => markCourse(courseName, 'in_progress')}>
                                Start
                              </button>
                              <button className="btn btn-sm btn-primary" onClick={() => markCourse(courseName, 'completed')}>
                                Done ✓
                              </button>
                            </>
                          )}
                          {isCompleted && (
                            <span className="completed-label">✓ Done</span>
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

      {/* Certificate Modal */}
      {showCertificate && (
        <div className="feedback-overlay" onClick={() => setShowCertificate(false)}>
          <div className="certificate-modal animate-scale-in" onClick={e => e.stopPropagation()}>
            <div className="certificate-border">
              <div className="certificate-content">
                <div className="cert-logo">PF</div>
                <h2>Certificate of Completion</h2>
                <p>This is to certify that</p>
                <h3 className="cert-name">{user?.name || 'Dedicated Learner'}</h3>
                <p>has successfully completed the Learning Path:</p>
                <h4 className="cert-path">{path.career_path || 'Custom Path'}</h4>
                <div className="cert-footer">
                  <div className="cert-signature">
                    <span>Pathfinder AI</span>
                    <div className="cert-line"></div>
                    <small>Instructor</small>
                  </div>
                  <div className="cert-date">
                    <span>{new Date().toLocaleDateString()}</span>
                    <div className="cert-line"></div>
                    <small>Date</small>
                  </div>
                </div>
              </div>
            </div>
            <div className="cert-actions">
              <button className="btn btn-secondary" onClick={() => setShowCertificate(false)}>Close</button>
              <button className="btn btn-primary" onClick={() => window.print()}>Download</button>
            </div>
          </div>
        </div>
      )}

      {/* Feedback Modal */}
      {feedbackCourse && (
        <div className="feedback-overlay" onClick={() => setFeedbackCourse(null)}>
          <div className="feedback-modal glass-card animate-scale-in" onClick={e => e.stopPropagation()}>
            <h3>Course Feedback 🎉</h3>
            <p>You completed <strong>{feedbackCourse}</strong>! Help us adapt your path.</p>

            <div className="feedback-field">
              <label>Difficulty Level</label>
              <div className="rating-stars">
                {[1, 2, 3, 4, 5].map(v => (
                  <button
                    key={v}
                    className={`star-btn ${feedbackData.difficulty >= v ? 'active' : ''}`}
                    onClick={() => setFeedbackData({ ...feedbackData, difficulty: v })}
                  >
                    {v <= 2 ? '😊' : v === 3 ? '😐' : '🔥'}
                  </button>
                ))}
              </div>
              <div className="rating-labels">
                <span>Too Easy</span>
                <span>Just Right</span>
                <span>Very Hard</span>
              </div>
            </div>

            <div className="feedback-field">
              <label>Relevance to Your Goal</label>
              <div className="rating-stars">
                {[1, 2, 3, 4, 5].map(v => (
                  <button
                    key={v}
                    className={`star-btn ${feedbackData.relevance >= v ? 'active' : ''}`}
                    onClick={() => setFeedbackData({ ...feedbackData, relevance: v })}
                  >
                    ⭐
                  </button>
                ))}
              </div>
            </div>

            <div className="feedback-actions">
              <button className="btn btn-ghost" onClick={() => setFeedbackCourse(null)}>Skip</button>
              <button className="btn btn-primary" onClick={submitFeedback}>Submit Feedback</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
