import { useState, useEffect, createContext, useContext } from 'react';
import { BrowserRouter, Routes, Route, NavLink, Navigate } from 'react-router-dom';
import { api } from './api';
import Landing from './pages/Landing';
import Onboarding from './pages/Onboarding';
import Dashboard from './pages/Dashboard';
import LearningPath from './pages/LearningPath';
import Chat from './pages/Chat';
import Courses from './pages/Courses';
import './index.css';

// User context
const UserContext = createContext(null);
export const useUser = () => useContext(UserContext);

function Sidebar({ user }) {
  const initial = user?.name ? user.name.charAt(0).toUpperCase() : '?';

  return (
    <aside className="app-sidebar">
      <div className="sidebar-logo">
        <div className="sidebar-logo-icon">PF</div>
        <h1>PathFinder</h1>
      </div>

      <nav className="sidebar-nav">
        <NavLink to="/dashboard" className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
          <span className="nav-icon">&#9878;</span> Dashboard
        </NavLink>
        <NavLink to="/learning-path" className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
          <span className="nav-icon">&#9776;</span> Learning Path
        </NavLink>
        <NavLink to="/chat" className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
          <span className="nav-icon">&#9993;</span> AI Assistant
        </NavLink>
        <NavLink to="/courses" className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
          <span className="nav-icon">&#9733;</span> Courses
        </NavLink>
      </nav>

      <div className="sidebar-footer">
        <div className="sidebar-user">
          <div className="sidebar-avatar">{initial}</div>
          <div className="sidebar-user-info">
            <div className="sidebar-user-name">{user?.name || 'Guest'}</div>
            <div className="sidebar-user-level">{user?.experience_level || 'beginner'}</div>
          </div>
        </div>
      </div>
    </aside>
  );
}

function AppLayout({ user, setUser }) {
  return (
    <div className="app-layout">
      <div className="bg-mesh" />
      <Sidebar user={user} />
      <main className="app-main">
        <div className="app-content">
          <Routes>
            <Route path="/dashboard" element={<Dashboard user={user} />} />
            <Route path="/learning-path" element={<LearningPath user={user} setUser={setUser} />} />
            <Route path="/chat" element={<Chat user={user} />} />
            <Route path="/courses" element={<Courses user={user} />} />
            <Route path="*" element={<Navigate to="/dashboard" replace />} />
          </Routes>
        </div>
      </main>
    </div>
  );
}

function App() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check for saved user
    const savedId = localStorage.getItem('pathfinder_user_id');
    if (savedId) {
      api.getProfile(savedId)
        .then((u) => { setUser(u); setLoading(false); })
        .catch(() => { localStorage.removeItem('pathfinder_user_id'); setLoading(false); });
    } else {
      setLoading(false);
    }
  }, []);

  const handleProfileCreated = (userData) => {
    setUser(userData);
    localStorage.setItem('pathfinder_user_id', userData.id || userData.user_id);
  };

  if (loading) {
    return (
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100vh' }}>
        <div className="spinner" style={{ width: 40, height: 40 }} />
      </div>
    );
  }

  return (
    <UserContext.Provider value={{ user, setUser }}>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={user ? <Navigate to="/dashboard" replace /> : <Landing />} />
          <Route path="/onboarding" element={<Onboarding onComplete={handleProfileCreated} />} />
          <Route path="/*" element={
            user ? <AppLayout user={user} setUser={setUser} /> : <Navigate to="/" replace />
          } />
        </Routes>
      </BrowserRouter>
    </UserContext.Provider>
  );
}

export default App;
