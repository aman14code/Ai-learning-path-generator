import { useState, useEffect } from 'react';
import { api } from '../api';
import './Courses.css';

const DOMAIN_ICONS = {
  'Python': '🐍',
  'Web Development': '🌐',
  'Data Science': '📊',
  'Machine Learning': '🧠',
  'Database': '🗄️',
  'Cloud & DevOps': '☁️',
  'Mobile Development': '📱',
  'Security': '🛡️',
  'Programming': '💻',
  'Data Engineering': '⚙️',
  'Mathematics': '📐',
  'Emerging Tech': '🚀',
};

export default function Courses({ user }) {
  const [courses, setCourses] = useState([]);
  const [domains, setDomains] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState({ domain: '', difficulty: '', search: '' });
  const [selectedCourse, setSelectedCourse] = useState(null);

  useEffect(() => {
    loadCourses();
  }, []);

  async function loadCourses() {
    setLoading(true);
    try {
      const data = await api.getCourses();
      setCourses(data.courses || []);
      setDomains(data.domains || []);
    } catch (err) {
      console.error('Failed to load courses:', err);
    }
    setLoading(false);
  }

  const filtered = courses.filter(c => {
    if (filter.domain && c.domain !== filter.domain) return false;
    if (filter.difficulty && c.difficulty !== filter.difficulty) return false;
    if (filter.search) {
      const q = filter.search.toLowerCase();
      return c.name.toLowerCase().includes(q) ||
             c.domain.toLowerCase().includes(q) ||
             c.skills?.some(s => s.toLowerCase().includes(q));
    }
    return true;
  });

  const completedSet = new Set(user?.completed_courses || []);

  // Domain stats
  const domainStats = {};
  courses.forEach(c => {
    if (!domainStats[c.domain]) domainStats[c.domain] = { total: 0, completed: 0 };
    domainStats[c.domain].total++;
    if (completedSet.has(c.name)) domainStats[c.domain].completed++;
  });

  async function markCourseProgress(courseName, status) {
    if (!user?.id) return;
    try {
      await api.updateProgress({
        user_id: user.id,
        course_name: courseName,
        status: status,
        progress_percent: status === 'completed' ? 100 : 50,
      });
    } catch (err) {
      console.error('Failed to update progress:', err);
    }
  }

  return (
    <div className="courses-page animate-fade-in">
      <div className="page-header">
        <h2>Course Catalog</h2>
        <p>Explore {courses.length} courses across {domains.length} skill domains.</p>
      </div>

      {/* Domain Category Cards */}
      <div className="domain-category-cards stagger">
        {domains.slice(0, 8).map(d => (
          <button
            key={d}
            className={`domain-cat-card ${filter.domain === d ? 'active' : ''}`}
            onClick={() => setFilter({ ...filter, domain: filter.domain === d ? '' : d })}
          >
            <span className="domain-cat-icon">{DOMAIN_ICONS[d] || '📦'}</span>
            <span className="domain-cat-name">{d}</span>
            <span className="domain-cat-count">{domainStats[d]?.total || 0}</span>
            {domainStats[d]?.completed > 0 && (
              <span className="domain-cat-completed">✓{domainStats[d].completed}</span>
            )}
          </button>
        ))}
      </div>

      {/* Filters */}
      <div className="courses-filters">
        <input
          className="input"
          type="text"
          placeholder="Search courses, skills, or domains..."
          value={filter.search}
          onChange={e => setFilter({ ...filter, search: e.target.value })}
          style={{ flex: 1, minWidth: 200 }}
        />
        <select
          className="input"
          value={filter.domain}
          onChange={e => setFilter({ ...filter, domain: e.target.value })}
        >
          <option value="">All Domains</option>
          {domains.map(d => <option key={d} value={d}>{d}</option>)}
        </select>
        <select
          className="input"
          value={filter.difficulty}
          onChange={e => setFilter({ ...filter, difficulty: e.target.value })}
        >
          <option value="">All Levels</option>
          <option value="Beginner">Beginner</option>
          <option value="Intermediate">Intermediate</option>
          <option value="Advanced">Advanced</option>
        </select>
      </div>

      <div className="courses-count">
        Showing {filtered.length} of {courses.length} courses
      </div>

      {/* Course Grid */}
      {loading ? (
        <div className="courses-grid">
          {[1, 2, 3, 4, 5, 6].map(i => (
            <div key={i} className="premium-3d-card" style={{ height: 180, padding: 20 }}>
              <div className="skeleton" style={{ height: 18, width: '70%', marginBottom: 10 }} />
              <div className="skeleton" style={{ height: 14, width: '40%', marginBottom: 16 }} />
              <div className="skeleton" style={{ height: 12, width: '90%', marginBottom: 6 }} />
              <div className="skeleton" style={{ height: 12, width: '60%' }} />
            </div>
          ))}
        </div>
      ) : (
        <div className="courses-grid stagger">
          {filtered.map(course => (
            <div
              key={course.name}
              className={`course-card premium-3d-card ${completedSet.has(course.name) ? 'completed' : ''}`}
              onClick={() => setSelectedCourse(selectedCourse?.name === course.name ? null : course)}
            >
              <div className="course-card-header">
                <h4>{course.name}</h4>
                {completedSet.has(course.name) && (
                  <span className="course-done-badge">✓</span>
                )}
              </div>
              <div className="course-card-meta">
                <span className={`badge badge-${course.difficulty.toLowerCase()}`}>
                  {course.difficulty}
                </span>
                <span className="course-domain-tag">{course.domain}</span>
                <span className="course-duration">{course.duration_hours}h</span>
              </div>
              <p className="course-desc">{course.description}</p>
              <div className="course-skills">
                {course.skills?.slice(0, 4).map(s => (
                  <span key={s} className="tag">{s}</span>
                ))}
              </div>

              {/* Expanded info */}
              {selectedCourse?.name === course.name && (
                <div className="course-expanded animate-fade-in">
                  {course.prerequisites?.length > 0 && (
                    <div className="course-prereqs">
                      <strong>Prerequisites:</strong>
                      <div className="prereq-list">
                        {course.prerequisites.map(p => (
                          <span key={p} className="tag">{p}</span>
                        ))}
                      </div>
                    </div>
                  )}
                  <div className="course-all-skills">
                    <strong>Skills you'll learn:</strong>
                    <div className="skills-list">
                      {course.skills?.map(s => (
                        <span key={s} className="tag">{s}</span>
                      ))}
                    </div>
                  </div>
                  {!completedSet.has(course.name) && user?.id && (
                    <div className="course-actions-bar">
                      <button
                        className="btn btn-sm btn-ghost"
                        onClick={(e) => { e.stopPropagation(); markCourseProgress(course.name, 'in_progress'); }}
                      >
                        Start Learning
                      </button>
                      <button
                        className="btn btn-sm btn-primary"
                        onClick={(e) => { e.stopPropagation(); markCourseProgress(course.name, 'completed'); }}
                      >
                        Mark Complete
                      </button>
                    </div>
                  )}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
