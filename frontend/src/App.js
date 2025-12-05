import React, { useState, useEffect } from 'react';
import ChatWindow from './components/ChatWindow';
import Login from './components/Login';
import authState from './services/auth.state';
import './App.css';

export default function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Subscribe to authentication state
    const authSub = authState.isAuthenticated$.subscribe(isAuth => {
      setIsAuthenticated(isAuth);
      setLoading(false);
    });

    const userSub = authState.user$.subscribe(userData => {
      setUser(userData);
    });

    return () => {
      authSub.unsubscribe();
      userSub.unsubscribe();
    };
  }, []);

  const handleLogout = () => {
    if (window.confirm('Are you sure you want to logout?')) {
      authState.logout();
    }
  };

  if (loading) {
    return (
      <div className="loading-screen">
        <div className="loading-spinner"></div>
        <p>Loading...</p>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Login onSuccess={() => setLoading(false)} />;
  }

  return (
    <div className="app-container">
      <header className="app-header">
        <div className="header-content">
          <div className="header-left">
            <div className="header-icon">💬</div>
            <h1>AI Assistant</h1>
          </div>
          <div className="header-right">
            <div className="user-info">
              <span className="user-name">👤 {user?.username}</span>
              <span className="user-role">{user?.role}</span>
            </div>
            <button onClick={handleLogout} className="logout-button">
              🚪 Logout
            </button>
          </div>
        </div>
      </header>
      <ChatWindow />
    </div>
  );
}
