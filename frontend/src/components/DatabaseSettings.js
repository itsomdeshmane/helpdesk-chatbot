import React, { useState, useEffect } from 'react';
import './DatabaseSettings.css';

const DatabaseSettings = () => {
  const [connections, setConnections] = useState([]);
  const [supportedDatabases, setSupportedDatabases] = useState([]);
  const [defaultPorts, setDefaultPorts] = useState({});
  const [showAddForm, setShowAddForm] = useState(false);
  const [testingConnection, setTestingConnection] = useState(false);
  const [testResult, setTestResult] = useState(null);
  
  // Form state
  const [formData, setFormData] = useState({
    name: '',
    db_type: 'mysql',
    host: 'localhost',
    port: '',
    database: '',
    user: '',
    password: '',
    is_default: false
  });

  useEffect(() => {
    fetchSupportedDatabases();
    fetchConnections();
  }, []);

  const fetchSupportedDatabases = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/database-settings/supported-databases');
      const data = await response.json();
      if (data.success) {
        setSupportedDatabases(data.databases);
        setDefaultPorts(data.default_ports);
        // Set default port for MySQL
        setFormData(prev => ({
          ...prev,
          port: data.default_ports['mysql']
        }));
      }
    } catch (error) {
      console.error('Failed to fetch supported databases:', error);
    }
  };

  const fetchConnections = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/database-settings/connections');
      const data = await response.json();
      if (data.success) {
        setConnections(data.connections);
      }
    } catch (error) {
      console.error('Failed to fetch connections:', error);
    }
  };

  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  };

  const handleDbTypeChange = (e) => {
    const dbType = e.target.value;
    setFormData(prev => ({
      ...prev,
      db_type: dbType,
      port: defaultPorts[dbType] || ''
    }));
  };

  const handleTestConnection = async () => {
    setTestingConnection(true);
    setTestResult(null);

    try {
      const response = await fetch('http://localhost:8000/api/database-settings/test-connection', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          db_type: formData.db_type,
          host: formData.host,
          port: parseInt(formData.port) || null,
          database: formData.database,
          user: formData.user,
          password: formData.password
        }),
      });

      const data = await response.json();
      setTestResult(data);
    } catch (error) {
      setTestResult({
        success: false,
        message: `Test failed: ${error.message}`
      });
    } finally {
      setTestingConnection(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    try {
      const response = await fetch('http://localhost:8000/api/database-settings/connections', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          ...formData,
          port: parseInt(formData.port) || null
        }),
      });

      const data = await response.json();
      
      if (data.success) {
        alert('Connection saved successfully!');
        setShowAddForm(false);
        resetForm();
        fetchConnections();
      } else {
        alert(`Failed to save connection: ${data.message}`);
      }
    } catch (error) {
      alert(`Error saving connection: ${error.message}`);
    }
  };

  const handleDeleteConnection = async (name) => {
    if (!window.confirm(`Are you sure you want to delete connection "${name}"?`)) {
      return;
    }

    try {
      const response = await fetch(`http://localhost:8000/api/database-settings/connections/${name}`, {
        method: 'DELETE',
      });

      const data = await response.json();
      
      if (data.success) {
        alert('Connection deleted successfully!');
        fetchConnections();
      } else {
        alert(`Failed to delete connection: ${data.message}`);
      }
    } catch (error) {
      alert(`Error deleting connection: ${error.message}`);
    }
  };

  const resetForm = () => {
    setFormData({
      name: '',
      db_type: 'mysql',
      host: 'localhost',
      port: defaultPorts['mysql'] || '',
      database: '',
      user: '',
      password: '',
      is_default: false
    });
    setTestResult(null);
  };

  const getDatabaseIcon = (dbType) => {
    switch (dbType) {
      case 'mysql':
        return '🐬';
      case 'postgresql':
        return '🐘';
      case 'sqlserver':
        return '🗄️';
      default:
        return '💾';
    }
  };

  return (
    <div className="database-settings">
      <div className="settings-header">
        <h2>🗄️ Database Connections</h2>
        <button 
          className="btn btn-primary"
          onClick={() => setShowAddForm(!showAddForm)}
        >
          {showAddForm ? '✕ Cancel' : '+ Add Connection'}
        </button>
      </div>

      {/* Add/Edit Form */}
      {showAddForm && (
        <div className="connection-form-container">
          <h3>Add New Database Connection</h3>
          <form onSubmit={handleSubmit} className="connection-form">
            <div className="form-grid">
              <div className="form-group">
                <label>Connection Name *</label>
                <input
                  type="text"
                  name="name"
                  value={formData.name}
                  onChange={handleInputChange}
                  placeholder="e.g., Production DB"
                  required
                />
              </div>

              <div className="form-group">
                <label>Database Type *</label>
                <select
                  name="db_type"
                  value={formData.db_type}
                  onChange={handleDbTypeChange}
                  required
                >
                  {supportedDatabases.map(db => (
                    <option key={db} value={db}>
                      {getDatabaseIcon(db)} {db.toUpperCase()}
                    </option>
                  ))}
                </select>
              </div>

              <div className="form-group">
                <label>Host *</label>
                <input
                  type="text"
                  name="host"
                  value={formData.host}
                  onChange={handleInputChange}
                  placeholder="localhost"
                  required
                />
              </div>

              <div className="form-group">
                <label>Port</label>
                <input
                  type="number"
                  name="port"
                  value={formData.port}
                  onChange={handleInputChange}
                  placeholder={`Default: ${defaultPorts[formData.db_type]}`}
                />
              </div>

              <div className="form-group">
                <label>Database Name *</label>
                <input
                  type="text"
                  name="database"
                  value={formData.database}
                  onChange={handleInputChange}
                  placeholder="Database name"
                  required
                />
              </div>

              <div className="form-group">
                <label>Username *</label>
                <input
                  type="text"
                  name="user"
                  value={formData.user}
                  onChange={handleInputChange}
                  placeholder="Database user"
                  required
                />
              </div>

              <div className="form-group">
                <label>Password *</label>
                <input
                  type="password"
                  name="password"
                  value={formData.password}
                  onChange={handleInputChange}
                  placeholder="Database password"
                  required
                />
              </div>

              <div className="form-group checkbox-group">
                <label>
                  <input
                    type="checkbox"
                    name="is_default"
                    checked={formData.is_default}
                    onChange={handleInputChange}
                  />
                  <span>Set as default connection</span>
                </label>
              </div>
            </div>

            {/* Test Result */}
            {testResult && (
              <div className={`test-result ${testResult.success ? 'success' : 'error'}`}>
                <strong>{testResult.success ? '✓ Success' : '✗ Failed'}:</strong> {testResult.message}
                {testResult.version && <div className="version-info">Version: {testResult.version}</div>}
              </div>
            )}

            {/* Form Actions */}
            <div className="form-actions">
              <button
                type="button"
                className="btn btn-secondary"
                onClick={handleTestConnection}
                disabled={testingConnection}
              >
                {testingConnection ? '⏳ Testing...' : '🔍 Test Connection'}
              </button>
              <button
                type="submit"
                className="btn btn-primary"
              >
                💾 Save Connection
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Connections List */}
      <div className="connections-list">
        <h3>Saved Connections ({connections.length})</h3>
        {connections.length === 0 ? (
          <div className="empty-state">
            <p>No database connections configured yet.</p>
            <p>Click "Add Connection" to get started.</p>
          </div>
        ) : (
          <div className="connections-grid">
            {connections.map((conn) => (
              <div key={conn.name} className={`connection-card ${conn.is_default ? 'default' : ''}`}>
                <div className="card-header">
                  <div className="card-title">
                    <span className="db-icon">{getDatabaseIcon(conn.db_type)}</span>
                    <span className="conn-name">{conn.name}</span>
                    {conn.is_default && <span className="default-badge">DEFAULT</span>}
                  </div>
                  <button 
                    className="btn-delete"
                    onClick={() => handleDeleteConnection(conn.name)}
                    title="Delete connection"
                  >
                    🗑️
                  </button>
                </div>
                <div className="card-body">
                  <div className="conn-detail">
                    <span className="label">Type:</span>
                    <span className="value">{conn.db_type.toUpperCase()}</span>
                  </div>
                  <div className="conn-detail">
                    <span className="label">Host:</span>
                    <span className="value">{conn.host}:{conn.port}</span>
                  </div>
                  <div className="conn-detail">
                    <span className="label">Database:</span>
                    <span className="value">{conn.database}</span>
                  </div>
                  <div className="conn-detail">
                    <span className="label">User:</span>
                    <span className="value">{conn.user}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Supported Databases Info */}
      <div className="info-section">
        <h4>ℹ️ Supported Databases</h4>
        <div className="supported-list">
          <div className="db-info">
            <span>🐬 <strong>MySQL</strong></span>
            <span>Default Port: {defaultPorts.mysql}</span>
          </div>
          <div className="db-info">
            <span>🐘 <strong>PostgreSQL</strong></span>
            <span>Default Port: {defaultPorts.postgresql}</span>
          </div>
          <div className="db-info">
            <span>🗄️ <strong>SQL Server</strong></span>
            <span>Default Port: {defaultPorts.sqlserver}</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DatabaseSettings;

