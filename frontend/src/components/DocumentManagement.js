import React, { useState } from 'react';
import './DocumentManagement.css';
import apiService from '../services/api.service';

const DocumentManagement = ({ user }) => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [reloading, setReloading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState(null);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [tenantId, setTenantId] = useState('default');

  const handleFileSelect = (event) => {
    const file = event.target.files[0];
    if (file) {
      // Validate file type
      const validTypes = ['.pdf', '.docx', '.xlsx', '.txt', '.md'];
      const fileExt = file.name.substring(file.name.lastIndexOf('.')).toLowerCase();
      
      if (validTypes.some(ext => fileExt === ext)) {
        setSelectedFile(file);
        setUploadStatus(null);
      } else {
        setUploadStatus({
          type: 'error',
          message: 'Invalid file type. Supported: PDF, DOCX, XLSX, TXT, MD'
        });
        setSelectedFile(null);
      }
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) {
      setUploadStatus({
        type: 'error',
        message: 'Please select a file first'
      });
      return;
    }

    setUploading(true);
    setUploadProgress(10);
    setUploadStatus({
      type: 'info',
      message: 'Uploading document...'
    });

    try {
      const formData = new FormData();
      formData.append('file', selectedFile);
      formData.append('tenant_id', tenantId);

      setUploadProgress(30);

      const response = await apiService.post('/documents/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        },
        onUploadProgress: (progressEvent) => {
          const percentCompleted = Math.round(
            (progressEvent.loaded * 100) / progressEvent.total
          );
          setUploadProgress(30 + (percentCompleted * 0.6)); // 30-90%
        }
      });

      setUploadProgress(100);

      if (response.data && response.data.status === 'indexed') {
        setUploadStatus({
          type: 'success',
          message: `✅ Successfully uploaded and indexed: ${response.data.filename} (${response.data.chunks} chunks)`
        });
        setSelectedFile(null);
        // Reset file input
        document.getElementById('file-input').value = '';
      } else if (response.data && response.data.status === 'error') {
        setUploadStatus({
          type: 'error',
          message: `❌ ${response.data.message}`
        });
      } else {
        setUploadStatus({
          type: 'error',
          message: '❌ Upload failed. Please try again.'
        });
      }
    } catch (error) {
      console.error('Upload error:', error);
      setUploadStatus({
        type: 'error',
        message: `❌ Upload failed: ${error.message}`
      });
    } finally {
      setUploading(false);
      setTimeout(() => setUploadProgress(0), 2000);
    }
  };

  const handleReloadAllDocs = async () => {
    if (!window.confirm('This will reload ALL documents from the docs folder. Continue?')) {
      return;
    }

    setReloading(true);
    setUploadStatus({
      type: 'info',
      message: 'Reloading all documents...'
    });

    try {
      const formData = new FormData();
      formData.append('tenant_id', tenantId);

      const response = await apiService.post('/documents/reload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });

      if (response.data && response.data.status === 'processing') {
        setUploadStatus({
          type: 'success',
          message: '✅ ' + response.data.message
        });
      } else {
        setUploadStatus({
          type: 'error',
          message: '❌ Failed to reload documents'
        });
      }
    } catch (error) {
      console.error('Reload error:', error);
      setUploadStatus({
        type: 'error',
        message: `❌ Reload failed: ${error.message}`
      });
    } finally {
      setReloading(false);
    }
  };

  const handleReloadMarkdown = async () => {
    if (!window.confirm('This will reload all markdown documentation. Continue?')) {
      return;
    }

    setReloading(true);
    setUploadStatus({
      type: 'info',
      message: 'Reloading markdown documentation...'
    });

    try {
      const formData = new FormData();
      formData.append('tenant_id', tenantId);

      const response = await apiService.post('/documents/reload-markdown', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });

      if (response.data && response.data.status === 'processing') {
        setUploadStatus({
          type: 'success',
          message: '✅ ' + response.data.message
        });
      } else {
        setUploadStatus({
          type: 'error',
          message: '❌ Failed to reload markdown'
        });
      }
    } catch (error) {
      console.error('Reload markdown error:', error);
      setUploadStatus({
        type: 'error',
        message: `❌ Reload failed: ${error.message}`
      });
    } finally {
      setReloading(false);
    }
  };

  return (
    <div className="document-management">
      <div className="doc-section">
        <h3>📤 Upload Document</h3>
        <p className="section-description">
          Upload documents to the knowledge base. Supported formats: PDF, DOCX, XLSX, TXT, MD
        </p>

        <div className="upload-area">
          <div className="tenant-selector">
            <label>Tenant ID:</label>
            <input
              type="text"
              value={tenantId}
              onChange={(e) => setTenantId(e.target.value)}
              placeholder="default"
              className="tenant-input"
            />
          </div>

          <div className="file-selector">
            <input
              id="file-input"
              type="file"
              accept=".pdf,.docx,.xlsx,.txt,.md"
              onChange={handleFileSelect}
              disabled={uploading}
              className="file-input"
            />
            <label htmlFor="file-input" className="file-label">
              {selectedFile ? selectedFile.name : '📁 Choose File'}
            </label>
          </div>

          {selectedFile && (
            <div className="selected-file">
              <span className="file-info">
                📄 {selectedFile.name} ({(selectedFile.size / 1024).toFixed(2)} KB)
              </span>
            </div>
          )}

          <button
            onClick={handleUpload}
            disabled={uploading || !selectedFile}
            className="upload-btn"
          >
            {uploading ? '⏳ Uploading...' : '📤 Upload & Index'}
          </button>

          {uploadProgress > 0 && uploadProgress < 100 && (
            <div className="progress-bar">
              <div 
                className="progress-fill" 
                style={{ width: `${uploadProgress}%` }}
              ></div>
              <span className="progress-text">{uploadProgress}%</span>
            </div>
          )}
        </div>
      </div>

      <div className="doc-section">
        <h3>🔄 Reload Documents</h3>
        <p className="section-description">
          Reload documents from the server's docs folder. This will re-index all existing documents.
        </p>

        <div className="reload-buttons">
          <button
            onClick={handleReloadAllDocs}
            disabled={reloading}
            className="reload-btn"
          >
            {reloading ? '⏳ Reloading...' : '🔄 Reload All Documents'}
          </button>

          <button
            onClick={handleReloadMarkdown}
            disabled={reloading}
            className="reload-btn secondary"
          >
            {reloading ? '⏳ Reloading...' : '📝 Reload Markdown Only'}
          </button>
        </div>

        <div className="reload-info">
          <p>
            <strong>Note:</strong> Reloading runs in the background and may take a few minutes
            depending on the number of documents.
          </p>
        </div>
      </div>

      {uploadStatus && (
        <div className={`status-message ${uploadStatus.type}`}>
          {uploadStatus.message}
        </div>
      )}

      <div className="doc-section info-section">
        <h4>ℹ️ Information</h4>
        <ul className="info-list">
          <li><strong>Upload:</strong> Uploads a single document and indexes it immediately</li>
          <li><strong>Reload All:</strong> Re-indexes all documents from the docs folder (PDF, DOCX, XLSX, TXT)</li>
          <li><strong>Reload Markdown:</strong> Re-indexes only markdown files with structure-aware chunking</li>
          <li><strong>Tenant ID:</strong> Namespace for documents (default: 'default')</li>
          <li><strong>Processing:</strong> Documents are processed in the background</li>
        </ul>
      </div>
    </div>
  );
};

export default DocumentManagement;

