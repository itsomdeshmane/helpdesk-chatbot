/**
 * Authentication State Management using RxJS
 * Central state management for user authentication
 */
import { BehaviorSubject } from 'rxjs';
import authService from './auth.service';

class AuthStateService {
  constructor() {
    // Initialize state observables
    this.user$ = new BehaviorSubject(null);
    this.isAuthenticated$ = new BehaviorSubject(false);
    this.loading$ = new BehaviorSubject(false);
    this.error$ = new BehaviorSubject(null);
    
    // Load initial state
    this.loadAuthState();
    
    console.log('🔐 Auth state service initialized');
  }

  /**
   * Load authentication state from storage
   */
  loadAuthState() {
    const user = authService.getUser();
    const isAuth = authService.isAuthenticated();
    
    this.user$.next(user);
    this.isAuthenticated$.next(isAuth);
    
    if (isAuth) {
      console.log('✅ User authenticated:', user?.username);
      // Verify token in background
      this.verifyToken();
    }
  }

  /**
   * Verify current token
   */
  async verifyToken() {
    const result = await authService.verifyToken();
    
    if (!result.valid) {
      this.logout();
    }
  }

  /**
   * Register new user
   */
  async register(username, email, password, fullName = null) {
    this.loading$.next(true);
    this.error$.next(null);
    
    try {
      const result = await authService.register(username, email, password, fullName);
      
      if (result.success) {
        console.log('✅ Registration successful');
        // Auto-login after registration
        return await this.login(username, password);
      } else {
        this.error$.next(result.error);
        return { success: false, error: result.error };
      }
    } catch (error) {
      const errorMsg = error.message || 'Registration failed';
      this.error$.next(errorMsg);
      return { success: false, error: errorMsg };
    } finally {
      this.loading$.next(false);
    }
  }

  /**
   * Login user
   */
  async login(username, password) {
    this.loading$.next(true);
    this.error$.next(null);
    
    try {
      const result = await authService.login(username, password);
      
      if (result.success) {
        this.user$.next(result.user);
        this.isAuthenticated$.next(true);
        console.log('✅ Login successful:', username);
        
        // SECURITY FIX: Clear local state (prevents showing previous user's data)
        try {
          const chatState = await import('./chat.state');
          chatState.default.messages$.next([]);
          chatState.default.sessionId$.next(null);
          console.log('🧹 Cleared local chat state');
        } catch (e) {
          console.log('⚠️  Could not clear chat state:', e);
        }
        
        // Load user's recent conversation history (with delay to ensure token is saved)
        setTimeout(async () => {
          try {
            const conversationService = require('./conversation.service').default;
            const chatState = require('./chat.state').default;
            
            console.log('📜 Loading user conversation history...');
            const recentConv = await conversationService.loadRecentConversation();
            
            if (recentConv.success && recentConv.messages && recentConv.messages.length > 0) {
              // Restore user's previous conversation
              chatState.sessionId$.next(recentConv.sessionId);
              
              // Convert messages to chat format
              const messages = [];
              for (const msg of recentConv.messages) {
                messages.push({
                  role: 'user',
                  content: msg.query,
                  timestamp: msg.timestamp,
                  id: Date.now() + Math.random()
                });
                messages.push({
                  role: 'assistant',
                  content: msg.response,
                  timestamp: msg.timestamp,
                  id: Date.now() + Math.random()
                });
              }
              
              chatState.messages$.next(messages);
              console.log(`✅ Restored ${recentConv.messages.length} previous messages from session ${recentConv.sessionId}`);
            } else {
              console.log('ℹ️  No previous conversation to restore (starting fresh):', recentConv.reason || recentConv.error);
            }
          } catch (e) {
            console.error('⚠️  Could not load conversation history:', e);
            // Don't fail login if history loading fails
          }
        }, 500); // Small delay to ensure token is in localStorage
        
        return { success: true, user: result.user };
      } else {
        this.error$.next(result.error);
        return { success: false, error: result.error };
      }
    } catch (error) {
      const errorMsg = error.message || 'Login failed';
      this.error$.next(errorMsg);
      return { success: false, error: errorMsg };
    } finally {
      this.loading$.next(false);
    }
  }

  /**
   * Logout user
   */
  logout() {
    // SECURITY FIX: Clear chat state before logging out
    try {
      const chatState = require('./chat.state').default;
      chatState.clearMessages();
      console.log('🧹 Cleared chat state on logout');
    } catch (e) {
      console.log('⚠️  Could not clear chat state:', e);
    }
    
    authService.logout();
    this.user$.next(null);
    this.isAuthenticated$.next(false);
    this.error$.next(null);
    console.log('✅ User logged out');
  }

  /**
   * Get current user
   */
  getUser() {
    return this.user$.getValue();
  }

  /**
   * Check if authenticated
   */
  isAuthenticated() {
    return this.isAuthenticated$.getValue();
  }

  /**
   * Clear error
   */
  clearError() {
    this.error$.next(null);
  }
}

// Create singleton instance
const authState = new AuthStateService();

export default authState;






