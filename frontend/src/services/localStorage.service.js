/**
 * Local Storage Service
 * Handles persistent storage of chat history
 */

const STORAGE_KEYS = {
  CHAT_HISTORY: 'helpdesk_chat_history',
  CHAT_SESSIONS: 'helpdesk_chat_sessions',
  TENANT_ID: 'helpdesk_tenant_id',
  SESSION_ID: 'helpdesk_session_id'
};

class LocalStorageService {
  /**
   * Save messages to local storage
   */
  saveMessages(messages) {
    try {
      const data = {
        messages,
        lastUpdated: new Date().toISOString(),
        version: '1.0'
      };
      localStorage.setItem(STORAGE_KEYS.CHAT_HISTORY, JSON.stringify(data));
      console.log('💾 Saved messages to local storage:', messages.length);
      return true;
    } catch (error) {
      console.error('Error saving messages:', error);
      return false;
    }
  }

  /**
   * Load messages from local storage
   */
  loadMessages() {
    try {
      const stored = localStorage.getItem(STORAGE_KEYS.CHAT_HISTORY);
      if (!stored) {
        console.log('📭 No stored messages found');
        return [];
      }

      const data = JSON.parse(stored);
      console.log('📬 Loaded messages from local storage:', data.messages?.length || 0);
      return data.messages || [];
    } catch (error) {
      console.error('Error loading messages:', error);
      return [];
    }
  }

  /**
   * Clear all messages from local storage
   */
  clearMessages() {
    try {
      localStorage.removeItem(STORAGE_KEYS.CHAT_HISTORY);
      console.log('🗑️ Cleared chat history');
      return true;
    } catch (error) {
      console.error('Error clearing messages:', error);
      return false;
    }
  }

  /**
   * Save tenant ID
   */
  saveTenantId(tenantId) {
    try {
      localStorage.setItem(STORAGE_KEYS.TENANT_ID, tenantId);
      return true;
    } catch (error) {
      console.error('Error saving tenant ID:', error);
      return false;
    }
  }

  /**
   * Load tenant ID
   */
  loadTenantId() {
    try {
      return localStorage.getItem(STORAGE_KEYS.TENANT_ID) || 'default';
    } catch (error) {
      console.error('Error loading tenant ID:', error);
      return 'default';
    }
  }

  /**
   * Get storage info
   */
  getStorageInfo() {
    try {
      const messages = this.loadMessages();
      const tenantId = this.loadTenantId();
      const stored = localStorage.getItem(STORAGE_KEYS.CHAT_HISTORY);
      const sizeKB = stored ? (stored.length / 1024).toFixed(2) : 0;

      return {
        messageCount: messages.length,
        tenantId,
        storageSizeKB: sizeKB,
        lastUpdated: messages.length > 0 ? JSON.parse(stored).lastUpdated : null
      };
    } catch (error) {
      console.error('Error getting storage info:', error);
      return null;
    }
  }
}

export default new LocalStorageService();

