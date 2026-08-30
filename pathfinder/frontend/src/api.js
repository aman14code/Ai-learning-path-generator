// Hardcoded Render URL for hackathon deployment
const API_BASE = import.meta.env.VITE_API_URL || 'https://pathfinder-backend-wnvm.onrender.com/api';

async function request(path, options = {}) {
  const url = `${API_BASE}${path}`;
  const config = {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  };

  if (config.body && typeof config.body === 'object') {
    config.body = JSON.stringify(config.body);
  }

  const res = await fetch(url, config);
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Request failed' }));
    throw new Error(err.detail || 'Request failed');
  }
  return res.json();
}

export const api = {
  // Profile
  createProfile: (data) => request('/profile', { method: 'POST', body: data }),
  getProfile: (id) => request(`/profile/${id}`),
  updateProfile: (id, data) => request(`/profile/${id}`, { method: 'PUT', body: data }),

  // Recommendations
  getRecommendations: (data) => request('/recommend', { method: 'POST', body: data }),

  // Learning Path
  generatePath: (data) => request('/learning-path', { method: 'POST', body: data }),
  getCareerPaths: () => request('/career-paths'),

  // Courses
  getCourses: (params = {}) => {
    const qs = new URLSearchParams(params).toString();
    return request(`/courses${qs ? '?' + qs : ''}`);
  },
  getCourse: (name) => request(`/courses/${encodeURIComponent(name)}`),

  // Chat
  sendMessage: (data) => request('/chat', { method: 'POST', body: data }),
  getChatHistory: (userId) => request(`/chat/${userId}/history`),

  // Progress
  updateProgress: (data) => request('/progress', { method: 'POST', body: data }),
  getProgress: (userId) => request(`/progress/${userId}`),

  // Skill Gap Analysis
  analyzeSkillGap: (data) => request('/skill-gap', { method: 'POST', body: data }),

  // Analytics
  getAnalytics: (userId) => request(`/analytics/${userId}`),

  // Feedback
  submitFeedback: (data) => request('/feedback', { method: 'POST', body: data }),
  getFeedback: (userId) => request(`/feedback/${userId}`),

  // Knowledge Graph
  getGraph: () => request('/graph'),

  // Health
  health: () => request('/health'),
};
