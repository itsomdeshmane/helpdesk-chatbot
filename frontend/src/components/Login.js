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
      <div className="auth-wrapper">
        {/* Left Side - Branding */}
        <div className="auth-branding">
          <div className="branding-content">
            <h1 className="brand-title">AI Helpdesk</h1>
            <p className="brand-subtitle">Your intelligent assistant for support and analytics</p>
            <div className="brand-features">
              <div className="feature-item">
                <span className="feature-icon">✓</span>
                <span>Smart document search</span>
              </div>
              <div className="feature-item">
                <span className="feature-icon">✓</span>
                <span>Database analytics</span>
              </div>
              <div className="feature-item">
                <span className="feature-icon">✓</span>
                <span>Natural language queries</span>
              </div>
            </div>
          </div>
        </div>

        {/* Right Side - Form */}
        <div className="auth-form-container">
          <div className="auth-card">
            <div className="auth-header">
              <h2>{isRegister ? 'Create Account' : 'Sign In'}</h2>
              <p>{isRegister ? 'Start your journey with AI Helpdesk' : 'Welcome back! Please sign in to continue'}</p>
            </div>

            {error && (
              <div className="error-message">
                {error}
              </div>
            )}

            <form onSubmit={isRegister ? handleRegister : handleLogin} className="auth-form">
              <div className="form-group">
                <input
                  type="text"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  placeholder="Username"
                  disabled={loading}
                  autoComplete="username"
                  required
                />
              </div>

              {isRegister && (
                <>
                  <div className="form-group">
                    <input
                      type="email"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      placeholder="Email address"
                      disabled={loading}
                      autoComplete="email"
                      required
                    />
                  </div>

                  <div className="form-group">
                    <input
                      type="text"
                      value={fullName}
                      onChange={(e) => setFullName(e.target.value)}
                      placeholder="Full name (optional)"
                      disabled={loading}
                      autoComplete="name"
                    />
                  </div>
                </>
              )}

              <div className="form-group">
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="Password"
                  disabled={loading}
                  autoComplete={isRegister ? "new-password" : "current-password"}
                  required
                />
                {isRegister && <span className="helper-text">Minimum 6 characters</span>}
              </div>

              <button type="submit" className="auth-button" disabled={loading}>
                {loading ? 'Please wait...' : (isRegister ? 'Create Account' : 'Sign In')}
              </button>
            </form>

            <div className="auth-divider">
              <span>or</span>
            </div>

            <button onClick={toggleMode} className="toggle-button" disabled={loading}>
              {isRegister ? 'Already have an account? Sign In' : 'Need an account? Sign Up'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}








