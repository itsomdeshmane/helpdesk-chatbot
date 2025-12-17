import React, { useState, useEffect } from 'react';
import './Settings.css';
import apiService from '../services/api.service';
import DocumentManagement from './DocumentManagement';

const Settings = ({ isOpen, onClose, currentTheme, onThemeChange, user }) => {
  const [activeTab, setActiveTab] = useState('general');
  const [dbConnection, setDbConnection] = useState({
    db_type: 'mysql',  // Added database type
    host: '',
    port: '3306',
    database: '',
    username: '',
    password: ''
  });
  const [testStatus, setTestStatus] = useState(null);
  const [saveStatus, setSaveStatus] = useState(null);
  const [loading, setLoading] = useState(false);
  
  // Database type defaults
  const dbDefaults = {
    mysql: { port: '3306', icon: '🐬', name: 'MySQL' },
    postgresql: { port: '5432', icon: '🐘', name: 'PostgreSQL' },
    sqlserver: { port: '1433', icon: '🗄️', name: 'SQL Server' }
  };

  // Load existing connection settings
  useEffect(() => {
    if (isOpen && activeTab === 'database') {
      loadConnectionSettings();
    }
  }, [isOpen, activeTab]);

  const loadConnectionSettings = async () => {
    try {
      setLoading(true);
      const response = await apiService.get('/settings/database-connection');
      console.log('Loaded connection settings:', response);
      
      if (response.data && response.data.data) {
        setDbConnection({
          db_type: response.data.data.db_type || 'mysql',
          host: response.data.data.host || '',
          port: response.data.data.port || '3306',
          database: response.data.data.database || '',
          username: response.data.data.username || '',
          password: '' // Never load password for security
        });
      }
    } catch (error) {
      console.error('Error loading connection settings:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleConnectionChange = (field, value) => {
    setDbConnection(prev => ({
      ...prev,
      [field]: value
    }));
    setTestStatus(null);
    setSaveStatus(null);
  };
  
  const handleDbTypeChange = (dbType) => {
    setDbConnection(prev => ({
      ...prev,
      db_type: dbType,
      port: dbDefaults[dbType].port  // Auto-update port when DB type changes
    }));
    setTestStatus(null);
    setSaveStatus(null);
  };

  const testConnection = async () => {
    try {
      setLoading(true);
      setTestStatus('testing');
      
      console.log('Testing connection with:', {
        db_type: dbConnection.db_type,
        host: dbConnection.host,
        port: dbConnection.port,
        database: dbConnection.database,
        username: dbConnection.username
      });
      
      const response = await apiService.post('/settings/test-database-connection', {
        db_type: dbConnection.db_type,
        host: dbConnection.host,
        port: parseInt(dbConnection.port),
        database: dbConnection.database,
        username: dbConnection.username,
        password: dbConnection.password
      });

      console.log('Test connection response:', response);

      // Check response.data.success (axios response structure)
      if (response.data && response.data.success) {
        setTestStatus('success');
        console.log('✅ Connection test successful');
      } else {
        setTestStatus('error');
        console.error('❌ Connection test failed:', response.data?.message);
        alert(`Connection failed: ${response.data?.message || 'Unknown error'}`);
      }
    } catch (error) {
      console.error('Connection test error:', error);
      setTestStatus('error');
      alert(`Connection failed: ${error.message || 'Network error'}`);
    } finally {
      setLoading(false);
    }
  };

  const saveConnection = async () => {
    try {
      setLoading(true);
      setSaveStatus('saving');
      
      console.log('Saving connection...');
      
      const response = await apiService.post('/settings/database-connection', {
        db_type: dbConnection.db_type,
        host: dbConnection.host,
        port: parseInt(dbConnection.port),
        database: dbConnection.database,
        username: dbConnection.username,
        password: dbConnection.password
      });

      console.log('Save connection response:', response);

      // Check response.data.success (axios response structure)
      if (response.data && response.data.success) {
        setSaveStatus('success');
        console.log('✅ Connection saved successfully');
        setTimeout(() => setSaveStatus(null), 3000);
      } else {
        setSaveStatus('error');
        console.error('❌ Save failed:', response.data?.message);
        alert(`Save failed: ${response.data?.message || 'Unknown error'}`);
      }
    } catch (error) {
      console.error('Save error:', error);
      setSaveStatus('error');
      alert(`Save failed: ${error.message || 'Network error'}`);
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="settings-overlay">
      <div className="settings-modal">
        <div className="settings-header">
          <h2>Settings</h2>
          <button className="close-btn" onClick={onClose}>×</button>
        </div>

        <div className="settings-content">
          <div className="settings-tabs">
            <button
              className={`settings-tab ${activeTab === 'general' ? 'active' : ''}`}
              onClick={() => setActiveTab('general')}
            >
              General
            </button>
            <button
              className={`settings-tab ${activeTab === 'database' ? 'active' : ''}`}
              onClick={() => setActiveTab('database')}
            >
              Database
            </button>
            <button
              className={`settings-tab ${activeTab === 'documents' ? 'active' : ''}`}
              onClick={() => setActiveTab('documents')}
            >
              Documents
            </button>
          </div>

          <div className="settings-body">
            {activeTab === 'general' && (
              <div className="settings-section">
                <h3>Appearance</h3>
                
                <div className="setting-item">
                  <label>Theme</label>
                  <div className="theme-selector">
                    <button
                      className={`theme-btn ${currentTheme === 'light' ? 'active' : ''}`}
                      onClick={() => onThemeChange('light')}
                    >
                      Light
                    </button>
                    <button
                      className={`theme-btn ${currentTheme === 'dark' ? 'active' : ''}`}
                      onClick={() => onThemeChange('dark')}
                    >
                      Dark
                    </button>
                  </div>
                </div>

                <div className="setting-item">
                  <label>Font Size</label>
                  <select className="setting-input">
                    <option>Small</option>
                    <option selected>Medium</option>
                    <option>Large</option>
                  </select>
                </div>
              </div>
            )}

            {activeTab === 'database' && (
              <div className="settings-section">
                <h3>Database Connection</h3>
                <p className="section-description">
                  Configure your database connection. Supports MySQL, PostgreSQL, and SQL Server.
                </p>

                <div className="setting-item">
                  <label>Database Type</label>
                  <select
                    className="setting-input"
                    value={dbConnection.db_type}
                    onChange={(e) => handleDbTypeChange(e.target.value)}
                  >
                    <option value="mysql">{dbDefaults.mysql.icon} MySQL</option>
                    <option value="postgresql">{dbDefaults.postgresql.icon} PostgreSQL</option>
                    <option value="sqlserver">{dbDefaults.sqlserver.icon} SQL Server</option>
                  </select>
                  <small className="input-hint">
                    Current: {dbDefaults[dbConnection.db_type].name} (Default port: {dbDefaults[dbConnection.db_type].port})
                  </small>
                </div>

                <div className="setting-item">
                  <label>Host</label>
                  <input
                    type="text"
                    className="setting-input"
                    placeholder="localhost or IP address"
                    value={dbConnection.host}
                    onChange={(e) => handleConnectionChange('host', e.target.value)}
                  />
                </div>

                <div className="setting-item">
                  <label>Port</label>
                  <input
                    type="number"
                    className="setting-input"
                    placeholder="3306"
                    value={dbConnection.port}
                    onChange={(e) => handleConnectionChange('port', e.target.value)}
                  />
                </div>

                <div className="setting-item">
                  <label>Database Name</label>
                  <input
                    type="text"
                    className="setting-input"
                    placeholder="database_name"
                    value={dbConnection.database}
                    onChange={(e) => handleConnectionChange('database', e.target.value)}
                  />
                </div>

                <div className="setting-item">
                  <label>Username</label>
                  <input
                    type="text"
                    className="setting-input"
                    placeholder="db_user"
                    value={dbConnection.username}
                    onChange={(e) => handleConnectionChange('username', e.target.value)}
                  />
                </div>

                <div className="setting-item">
                  <label>Password</label>
                  <input
                    type="password"
                    className="setting-input"
                    placeholder="Enter password"
                    value={dbConnection.password}
                    onChange={(e) => handleConnectionChange('password', e.target.value)}
                  />
                </div>

                <div className="connection-actions">
                  <button
                    className="test-btn"
                    onClick={testConnection}
                    disabled={loading || !dbConnection.host || !dbConnection.database}
                  >
                    {testStatus === 'testing' ? 'Testing...' : 'Test Connection'}
                  </button>
                  
                  {testStatus === 'success' && (
                    <span className="status-msg success">✓ Connection successful!</span>
                  )}
                  {testStatus === 'error' && (
                    <span className="status-msg error">✗ Connection failed</span>
                  )}
                </div>

                <div className="save-section">
                  <button
                    className="save-btn"
                    onClick={saveConnection}
                    disabled={loading || !dbConnection.host || !dbConnection.database}
                  >
                    {saveStatus === 'saving' ? 'Saving...' : 'Save Connection'}
                  </button>
                  
                  {saveStatus === 'success' && (
                    <span className="status-msg success">✓ Saved successfully!</span>
                  )}
                  {saveStatus === 'error' && (
                    <span className="status-msg error">✗ Save failed</span>
                  )}
                </div>
              </div>
            )}

            {activeTab === 'documents' && (
              <div className="settings-section">
                <DocumentManagement user={user} />
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Settings;


