import React, { useState, useEffect } from 'react';
import ChatWindowEnhanced from './components/ChatWindow-Enhanced';
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
    <ChatWindowEnhanced user={user} onLogout={handleLogout} />
  );
}
