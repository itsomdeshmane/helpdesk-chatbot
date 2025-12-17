# 🎨 Frontend Refactoring Guide - SOLID Principles

**Purpose**: Guide for refactoring React frontend to follow SOLID principles  
**Status**: New architecture ready, gradual migration recommended

---

## 📋 Overview

The frontend has been refactored to follow SOLID principles:
- ✅ **Custom Hooks**: Extract business logic from components
- ✅ **Service Layer**: Separate API communication
- ✅ **Single Responsibility**: Each component/hook has one job
- ✅ **Dependency Inversion**: Components depend on abstractions (hooks/services)

### **Before vs After**

| Aspect | Before | After | Improvement |
|--------|--------|-------|-------------|
| **Component LOC** | 737 | ~200 | 73% reduction |
| **Responsibilities** | UI + Logic + API | UI only | 3x separation |
| **Testability** | Hard | Easy | Mockable hooks |
| **Reusability** | Low | High | Hooks reusable |

---

## 🏗️ New Architecture

```
frontend/src/
├── hooks/                    ✅ NEW
│   ├── useChat.js           # Chat state & logic
│   └── useChatStream.js     # Streaming logic
│
├── services/                 ✅ REFACTORED
│   ├── chat.service.js      # Chat API (SRP)
│   ├── http.client.js       # HTTP layer (SRP)
│   └── auth.service.js      # Auth only (SRP)
│
├── components/
│   ├── ChatWindow-Enhanced.js    # OLD (737 lines)
│   └── ChatWindow-V2.jsx         # ✅ NEW (200 lines, SOLID)
│
└── App.js
```

---

## 🔄 Migration Path

### **Option 1: Gradual Migration (Recommended)**

Keep old components, add new ones side-by-side:

```jsx
// App.js
import ChatWindowOld from './components/ChatWindow-Enhanced';
import ChatWindowV2 from './components/ChatWindow-V2';

function App() {
  const [useNewVersion, setUseNewVersion] = useState(false);
  
  return (
    <div>
      <button onClick={() => setUseNewVersion(!useNewVersion)}>
        Toggle Version
      </button>
      
      {useNewVersion ? <ChatWindowV2 /> : <ChatWindowOld />}
    </div>
  );
}
```

**Benefits**:
- ✅ No breaking changes
- ✅ Easy comparison
- ✅ Quick rollback
- ✅ User testing

---

### **Option 2: Direct Replacement**

Replace old component with new one:

```jsx
// App.js
// OLD:
// import ChatWindow from './components/ChatWindow-Enhanced';

// NEW:
import ChatWindow from './components/ChatWindow-V2';
```

**Benefits**:
- ✅ Immediate cleanup
- ✅ Simpler codebase
- ✅ No version confusion

---

## 🎣 Using Hooks

### **useChat Hook**

Extract chat logic from components:

```jsx
import { useChat } from '../hooks/useChat';

function MyChatComponent() {
  // Get chat functionality
  const {
    messages,        // Array of messages
    isLoading,       // Loading state
    error,           // Error state
    sessionId,       // Current session
    sendMessage,     // Send message function
    clearChat,       // Clear chat function
    retryLastMessage // Retry function
  } = useChat();
  
  // UI only
  return (
    <div>
      {messages.map(msg => (
        <div key={msg.id}>{msg.content}</div>
      ))}
      
      <button onClick={() => sendMessage('Hello')}>
        Send
      </button>
    </div>
  );
}
```

**Benefits**:
- ✅ Component focuses on UI
- ✅ Logic testable in isolation
- ✅ Reusable across components
- ✅ Easy to mock in tests

---

### **useChatStream Hook**

Streaming functionality:

```jsx
import { useChatStream } from '../hooks/useChatStream';

function StreamingChat() {
  const {
    streamedContent,  // Current streamed text
    isStreaming,      // Streaming state
    streamQuery,      // Start streaming function
    stopStreaming     // Stop streaming function
  } = useChatStream();
  
  return (
    <div>
      <div>{streamedContent}</div>
      
      {isStreaming ? (
        <button onClick={stopStreaming}>Stop</button>
      ) : (
        <button onClick={() => streamQuery('Tell me a story')}>
          Start
        </button>
      )}
    </div>
  );
}
```

---

## 🛠️ Using Services

### **Chat Service**

```jsx
import { chatService } from '../services/chat.service';

// Send query
const response = await chatService.sendQuery('How do I...?', {
  source: 'auto',
  tenant_id: 'my-tenant',
  session_id: 'session-123'
});

// Stream query
const stream = await chatService.streamQuery('Tell me...');

// Get history
const history = await chatService.getHistory('session-123');

// Health check
const health = await chatService.healthCheck();
```

**Benefits**:
- ✅ Single Responsibility (chat API only)
- ✅ Uses V2 endpoints automatically
- ✅ Fallback to V1 if needed
- ✅ Easy to test

---

### **HTTP Client**

Low-level HTTP abstraction:

```jsx
import { httpClient } from '../services/http.client';

// GET
const data = await httpClient.get('/endpoint');

// POST
const result = await httpClient.post('/endpoint', { data });

// Streaming
const stream = await httpClient.stream('/endpoint', { data });
```

**Benefits**:
- ✅ Centralized HTTP logic
- ✅ Automatic auth injection
- ✅ Error handling
- ✅ Easy to mock

---

### **Auth Service**

```jsx
import { authService } from '../services/auth.service';

// Login
await authService.login('username', 'password');

// Logout
authService.logout();

// Check auth
if (authService.isAuthenticated()) {
  // User is logged in
}

// Get token
const token = authService.getToken();
```

---

## 📏 SOLID Principles in Frontend

### **Single Responsibility Principle (SRP)**

**Before** (❌ Multiple responsibilities):
```jsx
function ChatWindow() {
  // 1. UI rendering
  // 2. API calls
  // 3. State management
  // 4. Business logic
  // 5. Error handling
  // ...737 lines of mixed concerns
}
```

**After** (✅ Single responsibility):
```jsx
// Component: UI only
function ChatWindow() {
  const { messages, sendMessage } = useChat(); // Hook: Logic
  return <div>{/* UI */}</div>;
}

// Hook: State management
function useChat() {
  // Chat state & logic
}

// Service: API calls
class ChatService {
  async sendQuery() {
    // API calls only
  }
}
```

---

### **Open-Closed Principle (OCP)**

**Extensible without modification**:

```jsx
// Easy to add new hooks without changing existing code
import { useChat } from './useChat';
import { useChatStream } from './useChatStream';
import { useChatVoice } from './useChatVoice';  // ✅ New feature

// Easy to add new services
import { chatService } from './chat.service';
import { voiceService } from './voice.service';  // ✅ New service
```

---

### **Dependency Inversion Principle (DIP)**

**Components depend on abstractions (hooks), not concrete implementations**:

```jsx
// ✅ Component depends on hook interface
function MyComponent() {
  const { sendMessage } = useChat();  // Abstract interface
  // Component doesn't know about API, axios, fetch, etc.
}

// Hook provides abstraction
function useChat() {
  // Uses chatService internally
  // Component is decoupled from implementation
}
```

---

## 🧪 Testing

### **Testing Hooks**

```jsx
import { renderHook, act } from '@testing-library/react-hooks';
import { useChat } from './useChat';

test('useChat sends message', async () => {
  const { result } = renderHook(() => useChat());
  
  await act(async () => {
    await result.current.sendMessage('Hello');
  });
  
  expect(result.current.messages).toHaveLength(2); // User + Assistant
});
```

### **Testing Components**

```jsx
import { render, screen } from '@testing-library/react';
import ChatWindow from './ChatWindow-V2';

// Mock the hook
jest.mock('../hooks/useChat', () => ({
  useChat: () => ({
    messages: [{ id: 1, role: 'user', content: 'Test' }],
    sendMessage: jest.fn(),
    isLoading: false
  })
}));

test('renders messages', () => {
  render(<ChatWindow />);
  expect(screen.getByText('Test')).toBeInTheDocument();
});
```

### **Testing Services**

```jsx
import { chatService } from './chat.service';

// Mock httpClient
jest.mock('./http.client', () => ({
  httpClient: {
    post: jest.fn().mockResolvedValue({ success: true })
  }
}));

test('chatService sends query', async () => {
  const response = await chatService.sendQuery('Test');
  expect(response.success).toBe(true);
});
```

---

## 🎨 Component Patterns

### **Container/Presentational Pattern**

```jsx
// Container: Logic
function ChatContainer() {
  const chat = useChat();  // All logic in hook
  return <ChatView {...chat} />;
}

// Presentational: UI only
function ChatView({ messages, sendMessage, isLoading }) {
  return (
    <div>
      {messages.map(msg => <Message key={msg.id} {...msg} />)}
      <MessageInput onSend={sendMessage} disabled={isLoading} />
    </div>
  );
}
```

### **Composition Pattern**

```jsx
// Build complex UI from simple components
function ChatWindow() {
  return (
    <ChatContainer>
      <ChatHeader />
      <ChatMessages />
      <ChatInput />
      <ChatFooter />
    </ChatContainer>
  );
}
```

---

## 📊 Migration Checklist

### **For Each Component:**

- [ ] ✅ Extract business logic to hooks
- [ ] ✅ Extract API calls to services
- [ ] ✅ Component renders UI only
- [ ] ✅ State managed by hooks
- [ ] ✅ Props are simple (no complex objects)
- [ ] ✅ Component is < 200 lines
- [ ] ✅ Single responsibility
- [ ] ✅ Testable

### **For Each Hook:**

- [ ] ✅ One responsibility
- [ ] ✅ Returns simple interface
- [ ] ✅ Uses services for API
- [ ] ✅ Handles errors
- [ ] ✅ Cleanup on unmount
- [ ] ✅ Testable in isolation

### **For Each Service:**

- [ ] ✅ Single responsibility
- [ ] ✅ No UI logic
- [ ] ✅ Clear API
- [ ] ✅ Error handling
- [ ] ✅ Mockable

---

## 🎯 Best Practices

### **1. Keep Components Simple**

```jsx
// ❌ BAD: Too much logic
function BadComponent() {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(false);
  
  useEffect(() => {
    setLoading(true);
    fetch('/api/data')
      .then(res => res.json())
      .then(data => {
        setData(data);
        setLoading(false);
      });
  }, []);
  
  return <div>{/* UI */}</div>;
}

// ✅ GOOD: Logic in hook
function GoodComponent() {
  const { data, loading } = useData();
  return <div>{/* UI */}</div>;
}
```

### **2. Use Custom Hooks**

```jsx
// ✅ Extract repeated logic
function useDebounce(value, delay) {
  const [debouncedValue, setDebouncedValue] = useState(value);
  
  useEffect(() => {
    const handler = setTimeout(() => setDebouncedValue(value), delay);
    return () => clearTimeout(handler);
  }, [value, delay]);
  
  return debouncedValue;
}
```

### **3. Separate Concerns**

```jsx
// ✅ UI Component
function MessageList({ messages }) {
  return messages.map(msg => <Message key={msg.id} {...msg} />);
}

// ✅ Logic Hook
function useMessages() {
  const [messages, setMessages] = useState([]);
  // Logic...
  return { messages, addMessage, clearMessages };
}

// ✅ API Service
class MessageService {
  async getMessages() { /* API call */ }
}
```

---

## 🚀 Next Steps

1. ✅ **Try new components** - Test ChatWindow-V2.jsx
2. ✅ **Migrate gradually** - One component at a time
3. ✅ **Write tests** - Test hooks and services
4. ✅ **Remove old code** - After validation
5. ✅ **Enjoy benefits** - Cleaner, testable, maintainable!

---

## 📚 Resources

- **React Hooks**: https://react.dev/reference/react
- **Testing Library**: https://testing-library.com/
- **SOLID in React**: https://konstantinlebedev.com/solid-in-react/

---

**Frontend refactored and ready! 🎉**

---

**Last Updated**: December 17, 2025  
**Status**: ✅ Ready for use

