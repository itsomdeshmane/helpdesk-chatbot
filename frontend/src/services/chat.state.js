/**
 * Chat State Management using RxJS
 * Central state management for chat messages and loading states
 */
import { BehaviorSubject } from 'rxjs';
import localStorageService from './localStorage.service';
import apiService from './api.service';

class ChatStateService {
  constructor() {
    // Initialize state observables
    this.messages$ = new BehaviorSubject([]);
    this.loading$ = new BehaviorSubject(false);
    this.error$ = new BehaviorSubject(null);
    this.tenantId$ = new BehaviorSubject('default');
    
    // Load initial state from local storage
    this.loadFromStorage();
    
    // Auto-save on changes
    this.messages$.subscribe(messages => {
      if (messages.length > 0) {
        localStorageService.saveMessages(messages);
      }
    });

    console.log('🎯 Chat state service initialized');
  }

  /**
   * Load chat history from local storage
   */
  loadFromStorage() {
    try {
      const messages = localStorageService.loadMessages();
      const tenantId = localStorageService.loadTenantId();
      
      this.messages$.next(messages);
      this.tenantId$.next(tenantId);
      
      if (messages.length > 0) {
        console.log(`📚 Loaded ${messages.length} messages from storage`);
      }
    } catch (error) {
      console.error('❌ Error loading from storage:', error);
    }
  }

  /**
   * Get current messages
   */
  getMessages() {
    return this.messages$.getValue();
  }

  /**
   * Add a message to the chat
   */
  addMessage(message) {
    const currentMessages = this.messages$.getValue();
    const newMessage = {
      ...message,
      id: Date.now() + Math.random(), // Unique ID
      timestamp: new Date().toISOString()
    };
    
    this.messages$.next([...currentMessages, newMessage]);
    console.log('💬 Added message:', message.role, message.content.substring(0, 50));
  }

  /**
   * Send a user message and get AI response
   */
  async sendMessage(query) {
    if (!query || !query.trim()) {
      console.warn('⚠️ Empty message, skipping');
      return;
    }

    try {
      // Set loading state
      this.loading$.next(true);
      this.error$.next(null);

      // Add user message
      const userMessage = {
        role: 'user',
        content: query
      };
      this.addMessage(userMessage);

      // Send to API
      const tenantId = this.tenantId$.getValue();
      const result = await apiService.sendMessage(query, tenantId);

      if (result.success) {
        // Add assistant response
        const assistantMessage = {
          role: 'assistant',
          content: result.data.response,
          module: result.data.module,
          queryType: result.data.query_type,
          duration: result.duration,
          needsClarification: result.data.needs_clarification
        };
        this.addMessage(assistantMessage);
      } else {
        // Add error message
        const errorMessage = {
          role: 'assistant',
          content: `Error: ${result.error}`,
          isError: true
        };
        this.addMessage(errorMessage);
        this.error$.next(result.error);
      }
    } catch (error) {
      console.error('❌ Error in sendMessage:', error);
      const errorMessage = {
        role: 'assistant',
        content: `Error: ${error.message}`,
        isError: true
      };
      this.addMessage(errorMessage);
      this.error$.next(error.message);
    } finally {
      this.loading$.next(false);
    }
  }

  /**
   * Clear all messages
   */
  clearMessages() {
    this.messages$.next([]);
    localStorageService.clearMessages();
    this.error$.next(null);
    console.log('🗑️ Cleared all messages');
  }

  /**
   * Set tenant ID
   */
  setTenantId(tenantId) {
    this.tenantId$.next(tenantId);
    localStorageService.saveTenantId(tenantId);
    console.log('🏢 Set tenant ID:', tenantId);
  }

  /**
   * Get storage info
   */
  getStorageInfo() {
    return localStorageService.getStorageInfo();
  }

  /**
   * Export chat history
   */
  exportHistory() {
    const messages = this.getMessages();
    const exportData = {
      messages,
      tenantId: this.tenantId$.getValue(),
      exportedAt: new Date().toISOString(),
      version: '1.0'
    };
    
    const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `chat-history-${Date.now()}.json`;
    a.click();
    URL.revokeObjectURL(url);
    
    console.log('💾 Exported chat history');
  }

  /**
   * Import chat history
   */
  importHistory(jsonData) {
    try {
      const data = JSON.parse(jsonData);
      if (data.messages && Array.isArray(data.messages)) {
        this.messages$.next(data.messages);
        console.log('📥 Imported chat history:', data.messages.length, 'messages');
        return true;
      }
      return false;
    } catch (error) {
      console.error('❌ Error importing history:', error);
      return false;
    }
  }
}

// Create singleton instance
const chatState = new ChatStateService();

export default chatState;

