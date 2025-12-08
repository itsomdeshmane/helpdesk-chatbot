import React, { useState, useEffect } from 'react';
import authState from '../services/auth.state';
import './Auth.css';

export default function Login({ onSuccess }) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [isRegister, setIsRegister] = useState(false);
  const [email, setEmail] = useState('');
  const [fullName, setFullName] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    const errorSub = authState.error$.subscribe(err => {
      setError(err);
    });

    const loadingSub = authState.loading$.subscribe(isLoading => {
      setLoading(isLoading);
    });

    return () => {
      errorSub.unsubscribe();
      loadingSub.unsubscribe();
    };
  }, []);

  const handleLogin = async (e) => {
    e.preventDefault();
    setError(null);

    if (!username || !password) {
      setError('Please enter username and password');
      return;
    }

    const result = await authState.login(username, password);
    
    if (result.success) {
      onSuccess && onSuccess(result.user);
    }
  };

  const handleRegister = async (e) => {
    e.preventDefault();
    setError(null);

    if (!username || !email || !password) {
      setError('Please fill in all required fields');
      return;
    }

    if (password.length < 6) {
      setError('Password must be at least 6 characters');
      return;
    }

    const result = await authState.register(username, email, password, fullName);
    
    if (result.success) {
      onSuccess && onSuccess(result.user);
    }
  };

  const toggleMode = () => {
    setIsRegister(!isRegister);
    setError(null);
    setUsername('');
    setPassword('');
    setEmail('');
    setFullName('');
  };

  return (
    <div className="auth-container">
      <div className="auth-card">
        <div className="auth-header">
          <div className="auth-icon">🤖</div>
          <h2>{isRegister ? 'Create Account' : 'Welcome Back'}</h2>
          <p>{isRegister ? 'Sign up to get started' : 'Sign in to continue'}</p>
        </div>

        <form onSubmit={isRegister ? handleRegister : handleLogin} className="auth-form">
          {error && (
            <div className="error-message">
              ⚠️ {error}
            </div>
          )}

          <div className="form-group">
            <label>Username</label>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="Enter your username"
              disabled={loading}
              autoComplete="username"
            />
          </div>

          {isRegister && (
            <>
              <div className="form-group">
                <label>Email</label>
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="Enter your email"
                  disabled={loading}
                  autoComplete="email"
                />
              </div>

              <div className="form-group">
                <label>Full Name (Optional)</label>
                <input
                  type="text"
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  placeholder="Enter your full name"
                  disabled={loading}
                  autoComplete="name"
                />
              </div>
            </>
          )}

          <div className="form-group">
            <label>Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder={isRegister ? "At least 6 characters" : "Enter your password"}
              disabled={loading}
              autoComplete={isRegister ? "new-password" : "current-password"}
            />
          </div>

          <button type="submit" className="auth-button" disabled={loading}>
            {loading ? '⏳ Please wait...' : (isRegister ? '✨ Sign Up' : '🚀 Sign In')}
          </button>
        </form>

        <div className="auth-footer">
          <p>
            {isRegister ? 'Already have an account?' : "Don't have an account?"}
            {' '}
            <button onClick={toggleMode} className="link-button" disabled={loading}>
              {isRegister ? 'Sign In' : 'Sign Up'}
            </button>
          </p>
        </div>
      </div>
    </div>
  );
}






