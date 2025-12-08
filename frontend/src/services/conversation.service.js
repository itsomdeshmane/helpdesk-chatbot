/**
 * Conversation Service
 * Handles user's conversation history management
 */

const API_BASE_URL = 'http://localhost:8000';

class ConversationService {
  /**
   * Get current user's conversations
   */
  async getMyConversations(limit = 5) {
    try {
      const token = localStorage.getItem('auth_token'); // FIX: Use correct key
      
      if (!token) {
        console.log('⚠️  No auth token found');
        return { success: false, error: 'Not authenticated' };
      }
      
      console.log(`🔍 Fetching conversations (limit: ${limit})...`);
      const response = await fetch(`${API_BASE_URL}/conversations/my-conversations?limit=${limit}`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      
      console.log(`📡 Response status: ${response.status}`);
      
      if (!response.ok) {
        const errorText = await response.text();
        console.error(`❌ API error: ${response.status} - ${errorText}`);
        throw new Error(`HTTP ${response.status}: ${errorText}`);
      }
      
      const data = await response.json();
      console.log(`✅ Received ${data.conversation_count || 0} conversations`);
      
      return {
        success: true,
        conversations: data.conversations || [],
        count: data.conversation_count || 0
      };
      
    } catch (error) {
      console.error('❌ Error fetching conversations:', error);
      return {
        success: false,
        error: error.message || 'Failed to fetch conversations'
      };
    }
  }
  
  /**
   * Get specific conversation details
   */
  async getConversation(sessionId) {
    try {
      const token = localStorage.getItem('auth_token'); // FIX: Use correct key
      
      if (!token) {
        return { success: false, error: 'Not authenticated' };
      }
      
      const response = await fetch(`${API_BASE_URL}/conversations/${sessionId}`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }
      
      const data = await response.json();
      
      return {
        success: true,
        sessionId: data.session_id,
        messages: data.messages || [],
        messageCount: data.message_count || 0
      };
      
    } catch (error) {
      console.error('Error fetching conversation:', error);
      return {
        success: false,
        error: error.message || 'Failed to fetch conversation'
      };
    }
  }
  
  /**
   * Load most recent active conversation
   */
  async loadRecentConversation() {
    try {
      console.log('🔄 Starting loadRecentConversation...');
      
      // Get user's conversations
      const result = await this.getMyConversations(1);
      
      if (!result.success) {
        console.log(`⚠️  Failed to get conversations: ${result.error}`);
        return { success: false, reason: 'api_error', error: result.error };
      }
      
      if (!result.conversations || result.conversations.length === 0) {
        console.log('ℹ️  No previous conversations found (user has clean slate)');
        return { success: false, reason: 'no_conversations' };
      }
      
      // Get the most recent conversation
      const recentConv = result.conversations[0];
      console.log(`📋 Most recent conversation: ${recentConv.session_id} (status: ${recentConv.status}, ${recentConv.message_count} messages)`);
      
      // Only load if it's active (not archived)
      if (recentConv.status !== 'active') {
        console.log(`ℹ️  Most recent conversation is ${recentConv.status} (not active)`);
        return { success: false, reason: 'not_active' };
      }
      
      // Fetch full conversation details
      console.log(`📥 Fetching full details for session: ${recentConv.session_id}`);
      const convDetails = await this.getConversation(recentConv.session_id);
      
      if (!convDetails.success) {
        console.log(`❌ Failed to get conversation details: ${convDetails.error}`);
        return { success: false, error: convDetails.error };
      }
      
      console.log(`✅ Successfully loaded conversation: ${recentConv.session_id} with ${convDetails.messages.length} messages`);
      
      return {
        success: true,
        sessionId: recentConv.session_id,
        messages: convDetails.messages,
        title: recentConv.title
      };
      
    } catch (error) {
      console.error('❌ Exception in loadRecentConversation:', error);
      return {
        success: false,
        error: error.message || 'Failed to load conversation'
      };
    }
  }
}

export default new ConversationService();

