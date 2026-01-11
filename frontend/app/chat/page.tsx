'use client';

import { useState, useRef, useEffect } from 'react';
import ConversationInfo from '../components/ConversationInfo';

const API_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';
const USER_ID = process.env.NEXT_PUBLIC_USER_ID || 'demo_user';
const DOMAIN_KEY = process.env.NEXT_PUBLIC_OPENAI_DOMAIN_KEY || '';

interface ToolCall {
  tool: string;
  arguments: Record<string, any>;
  result?: Record<string, any>;
  error?: string;
}

interface ChatMessage {
  message: string;
  sender: string;
  direction: 'incoming' | 'outgoing';
  toolCalls?: ToolCall[];
}

interface Conversation {
  id: number;
  title: string;
  lastMessage: string;
  timestamp: Date;
}

export default function ChatbotPage() {
  // Stateless UI state - only for display, all persistence in backend
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      message: "Hello! I'm your AI todo assistant. I can help you manage your tasks through natural language. Try these commands:\n\n• 'Add a task to buy groceries'\n• 'Show me my tasks'\n• 'Complete task 1'\n• 'Delete the groceries task'\n• 'What do I need to do today?'",
      sender: 'AI',
      direction: 'incoming',
    }
  ]);
  const [isTyping, setIsTyping] = useState(false);
  const [conversationId, setConversationId] = useState<number | null>(null);
  const [messageCount, setMessageCount] = useState(1);
  const [inputMessage, setInputMessage] = useState('');
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [conversations, setConversations] = useState<Conversation[]>([
    { id: 1, title: "What is use of that chatbot ?", lastMessage: "Chatbots can be used for...", timestamp: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000) }
  ]);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const getToolIcon = (tool: string): string => {
    switch (tool) {
      case 'add_task': return '➕';
      case 'list_tasks': return '📋';
      case 'update_task': return '✏️';
      case 'complete_task': return '✅';
      case 'delete_task': return '🗑️';
      default: return '🔧';
    }
  };

  const formatToolConfirmations = (toolCalls: ToolCall[]): string => {
    if (!toolCalls || toolCalls.length === 0) return '';
    
    const confirmations = toolCalls.map(tc => {
      const icon = getToolIcon(tc.tool);
      if (tc.error) {
        return `❌ ${tc.tool} failed: ${tc.error}`;
      }
      
      switch (tc.tool) {
        case 'add_task':
          return `${icon} Created: "${tc.result?.title}" (ID: ${tc.result?.task_id})`;
        case 'list_tasks':
          return `${icon} Found ${tc.result?.length || 0} task(s)`;
        case 'update_task':
          return `${icon} Updated task ${tc.arguments.task_id}`;
        case 'complete_task':
          return `${icon} Task ${tc.arguments.task_id} → ${tc.result?.status}`;
        case 'delete_task':
          return `${icon} Deleted: "${tc.result?.title}"`;
        default:
          return `${icon} Executed: ${tc.tool}`;
      }
    });
    
    return '\n\n─────────────────────\n' + confirmations.join('\n');
  };

  const handleNewChat = () => {
    setConversationId(null);
    setMessages([
      {
        message: "Hello! I'm your AI todo assistant. I can help you manage your tasks through natural language. Try these commands:\n\n• 'Add a task to buy groceries'\n• 'Show me my tasks'\n• 'Complete task 1'\n• 'Delete the groceries task'\n• 'What do I need to do today?'",
        sender: 'AI',
        direction: 'incoming',
      }
    ]);
    setMessageCount(1);
  };

  const handleClearAll = () => {
    setConversations([]);
    handleNewChat();
  };

  const handleSend = async (e?: React.FormEvent) => {
    e?.preventDefault();
    const message = inputMessage.trim();
    if (!message) return;

    // Add user message to UI (stateless display only)
    const userMessage: ChatMessage = {
      message: message,
      sender: 'User',
      direction: 'outgoing',
    };
    setMessages(prev => [...prev, userMessage]);
    setMessageCount(prev => prev + 1);
    setIsTyping(true);
    setInputMessage('');

    try {
      // Call backend API with conversation_id for state continuity
      const response = await fetch(`${API_URL}/api/${USER_ID}/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(DOMAIN_KEY && { 'X-OpenAI-Domain-Key': DOMAIN_KEY })
        },
        body: JSON.stringify({
          message: message.trim(),
          conversation_id: conversationId, // Null for first message, then persisted
        }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }));
        throw new Error(errorData.detail || `HTTP ${response.status}`);
      }

      const data = await response.json();

      // Update conversation ID from backend (stateless tracking)
      if (!conversationId && data.conversation_id) {
        setConversationId(data.conversation_id);
      }

      // Format response with tool confirmations
      let responseText = data.response;
      if (data.tool_calls && data.tool_calls.length > 0) {
        const toolConfirmations = formatToolConfirmations(data.tool_calls);
        responseText += toolConfirmations;
      }

      // Add AI response to UI
      const aiMessage: ChatMessage = {
        message: responseText,
        sender: 'AI',
        direction: 'incoming',
        toolCalls: data.tool_calls
      };
      setMessages(prev => [...prev, aiMessage]);
      setMessageCount(prev => prev + 1);

    } catch (error) {
      console.error('Chat error:', error);
      
      // Display error message to user
      const errorMessage: ChatMessage = {
        message: `❌ Error: ${error instanceof Error ? error.message : 'Failed to send message. Please check your connection and try again.'}`,
        sender: 'System',
        direction: 'incoming',
      };
      setMessages(prev => [...prev, errorMessage]);
      setMessageCount(prev => prev + 1);
      
    } finally {
      setIsTyping(false);
    }
  };

  return (
    <div className="flex h-screen bg-white">
      {/* Sidebar */}
      <div className={`${sidebarOpen ? 'w-64' : 'w-0'} bg-[#171717] text-white flex flex-col transition-all duration-300 overflow-hidden`}>
        <div className="p-4 flex items-center justify-between border-b border-gray-700">
          <button
            onClick={handleNewChat}
            className="flex items-center gap-2 px-4 py-2.5 bg-transparent border border-gray-600 rounded-lg hover:bg-gray-800 transition-colors w-full"
          >
            <span className="text-xl">+</span>
            <span className="text-sm font-medium">New chat</span>
          </button>
          <button
            onClick={() => setSidebarOpen(false)}
            className="ml-2 p-2 hover:bg-gray-800 rounded"
          >
            ✕
          </button>
        </div>

        <div className="flex-1 overflow-y-auto p-2">
          <div className="mb-4">
            <div className="text-xs text-gray-400 px-3 py-2">Your conversations</div>
            <button
              onClick={handleClearAll}
              className="text-xs text-gray-400 hover:text-white px-3 py-1 w-full text-left hover:bg-gray-800 rounded"
            >
              Clear All
            </button>
          </div>

          {conversations.map((conv) => (
            <div
              key={conv.id}
              className="px-3 py-2.5 mb-1 rounded-lg hover:bg-gray-800 cursor-pointer group"
            >
              <div className="flex items-start gap-2">
                <span className="text-base mt-0.5">💬</span>
                <div className="flex-1 min-w-0">
                  <div className="text-sm text-gray-200 truncate">{conv.title}</div>
                </div>
              </div>
            </div>
          ))}

          <div className="mt-4 px-3 py-2">
            <div className="text-xs text-gray-500">Last 7 Days</div>
          </div>
        </div>

        <div className="p-4 border-t border-gray-700">
          <div className="flex items-center gap-3 px-2 py-2 hover:bg-gray-800 rounded cursor-pointer">
            <div className="w-8 h-8 bg-purple-600 rounded-full flex items-center justify-center text-sm font-semibold">
              A
            </div>
            <div className="text-sm">
              <div className="font-medium">Andrew Neilson</div>
            </div>
          </div>
          <button className="flex items-center gap-2 px-2 py-2 mt-2 hover:bg-gray-800 rounded w-full text-left text-sm">
            <span>⚙️</span>
            <span>Settings</span>
          </button>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <div className="bg-white border-b border-gray-200 px-4 py-3 flex items-center gap-4">
          {!sidebarOpen && (
            <button
              onClick={() => setSidebarOpen(true)}
              className="p-2 hover:bg-gray-100 rounded"
            >
              ☰
            </button>
          )}
          <div className="flex-1">
            <h1 className="text-xl font-semibold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
              CHAT A.I+
            </h1>
          </div>
          <ConversationInfo 
            conversationId={conversationId} 
            messageCount={messageCount}
          />
        </div>

        {/* Messages Area */}
        <div className="flex-1 overflow-y-auto bg-white">
          <div className="max-w-3xl mx-auto px-4 py-8">
            {messages.map((msg, i) => (
              <div
                key={i}
                className={`mb-6 flex gap-4 ${msg.direction === 'outgoing' ? 'flex-row-reverse' : ''}`}
              >
                <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${
                  msg.direction === 'outgoing' ? 'bg-purple-600' : 'bg-gradient-to-br from-blue-500 to-purple-600'
                }`}>
                  <span className="text-white text-sm font-semibold">
                    {msg.direction === 'outgoing' ? 'U' : 'AI'}
                  </span>
                </div>
                <div className="flex-1">
                  <div className={`text-sm font-semibold mb-1 ${msg.direction === 'outgoing' ? 'text-right' : ''}`}>
                    {msg.sender === 'AI' ? 'CHAT A.I+' : msg.sender}
                  </div>
                  <div className={`prose max-w-none ${msg.direction === 'outgoing' ? 'text-right' : ''}`}>
                    <div className="whitespace-pre-wrap text-gray-800 leading-relaxed">
                      {msg.message}
                    </div>
                  </div>
                </div>
              </div>
            ))}
            
            {isTyping && (
              <div className="mb-6 flex gap-4">
                <div className="w-8 h-8 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center flex-shrink-0">
                  <span className="text-white text-sm font-semibold">AI</span>
                </div>
                <div className="flex-1">
                  <div className="text-sm font-semibold mb-1">CHAT A.I+</div>
                  <div className="flex gap-1 items-center text-gray-500">
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        </div>

        {/* Input Area */}
        <div className="bg-white border-t border-gray-200">
          <div className="max-w-3xl mx-auto p-4">
            <form onSubmit={handleSend} className="relative">
              <div className="flex items-center gap-2 bg-gray-50 rounded-2xl border border-gray-200 px-4 py-3 hover:border-gray-300 transition-colors">
                <input
                  type="text"
                  value={inputMessage}
                  onChange={(e) => setInputMessage(e.target.value)}
                  placeholder="What's in your mind?..."
                  className="flex-1 bg-transparent outline-none text-gray-800 placeholder-gray-400"
                  disabled={isTyping}
                />
                <button
                  type="submit"
                  disabled={isTyping || !inputMessage.trim()}
                  className="w-9 h-9 bg-gradient-to-r from-blue-600 to-purple-600 rounded-full flex items-center justify-center text-white hover:opacity-90 transition-opacity disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M22 2L11 13M22 2l-7 20-4-9-9-4 20-7z" />
                  </svg>
                </button>
              </div>
            </form>
            <div className="text-xs text-center text-gray-500 mt-3">
              Stateless UI - All conversation state persisted in database
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
