'use client';

import { useState, useRef, useEffect } from 'react';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
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
}

export default function ChatbotPage() {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      message: "Hello! I'm your AI todo assistant. I can help you manage your tasks. Try asking me to add a task, list your tasks, or complete a task!",
      sender: 'AI',
      direction: 'incoming',
    }
  ]);
  const [isTyping, setIsTyping] = useState(false);
  const [conversationId, setConversationId] = useState<number | null>(null);
  const [inputMessage, setInputMessage] = useState('');
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [conversations, setConversations] = useState<Conversation[]>([
    { id: 1, title: "Create Html Game Environment..." },
    { id: 2, title: "Apply To Leave For Emergency" },
    { id: 3, title: "What Is UI UX Design?" },
    { id: 4, title: "Create POS System" },
    { id: 5, title: "What Is UX Audit?" },
    { id: 6, title: "Create Chatbot GPT..." },
    { id: 7, title: "How Chat GPT Work?" },
    { id: 8, title: "Crypto Lending App Name" },
    { id: 9, title: "Operator Grammar Types" },
    { id: 10, title: "Afm Stones For Binary DFA" },
  ]);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleNewChat = () => {
    setConversationId(null);
    setMessages([
      {
        message: "Hello! I'm your AI todo assistant. I can help you manage your tasks. Try asking me to add a task, list your tasks, or complete a task!",
        sender: 'AI',
        direction: 'incoming',
      }
    ]);
  };

  const handleClearAll = () => {
    if (confirm('Clear all conversations?')) {
      setConversations([]);
      handleNewChat();
    }
  };

  const handleSend = async (e?: React.FormEvent) => {
    e?.preventDefault();
    const message = inputMessage.trim();
    if (!message) return;

    const userMessage: ChatMessage = {
      message: message,
      sender: 'User',
      direction: 'outgoing',
    };
    setMessages(prev => [...prev, userMessage]);
    setIsTyping(true);
    setInputMessage('');

    try {
      const response = await fetch(`${API_URL}/api/${USER_ID}/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(DOMAIN_KEY && { 'X-OpenAI-Domain-Key': DOMAIN_KEY })
        },
        body: JSON.stringify({
          message: message,
          conversation_id: conversationId,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }));
        throw new Error(errorData.detail || `HTTP ${response.status}`);
      }

      const data = await response.json();

      if (!conversationId && data.conversation_id) {
        setConversationId(data.conversation_id);
      }

      const aiMessage: ChatMessage = {
        message: data.response,
        sender: 'AI',
        direction: 'incoming',
        toolCalls: data.tool_calls
      };
      setMessages(prev => [...prev, aiMessage]);

    } catch (error) {
      console.error('Chat error:', error);
      const errorMessage: ChatMessage = {
        message: `❌ Error: ${error instanceof Error ? error.message : 'Failed to send message'}`,
        sender: 'System',
        direction: 'incoming',
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsTyping(false);
    }
  };

  return (
    <div className="flex h-screen bg-white">
      {/* Sidebar */}
      <div className={`${sidebarOpen ? 'w-64' : 'w-0'} bg-[#171717] text-white flex flex-col transition-all duration-300 overflow-hidden`}>
        <div className="p-3 border-b border-gray-700">
          <button
            onClick={handleNewChat}
            className="flex items-center justify-center gap-2 px-3 py-2.5 bg-transparent border border-gray-600 rounded-md hover:bg-gray-800 transition-colors w-full text-sm font-medium"
          >
            <span className="text-lg">+</span>
            <span>New chat</span>
          </button>
        </div>

        <div className="flex-1 overflow-y-auto">
          <div className="p-3">
            <div className="flex items-center justify-between mb-2">
              <div className="text-xs text-gray-400">Your conversations</div>
              <button
                onClick={handleClearAll}
                className="text-xs text-blue-400 hover:text-blue-300"
              >
                Clear All
              </button>
            </div>

            <div className="space-y-1">
              {conversations.map((conv) => (
                <div
                  key={conv.id}
                  className="flex items-center gap-2 px-2 py-2 rounded hover:bg-gray-800 cursor-pointer group"
                >
                  <span className="text-gray-400">💬</span>
                  <span className="text-sm text-gray-300 truncate flex-1">{conv.title}</span>
                </div>
              ))}
            </div>

            <div className="mt-4 text-xs text-gray-500 px-2">Last 7 Days</div>
          </div>
        </div>

        <div className="p-3 border-t border-gray-700">
          <div className="flex items-center gap-2 px-2 py-2 hover:bg-gray-800 rounded cursor-pointer">
            <div className="w-7 h-7 bg-purple-600 rounded-full flex items-center justify-center text-xs font-bold">
              A
            </div>
            <div className="flex-1">
              <div className="text-sm font-medium">Andrew Neilson</div>
            </div>
          </div>
          <button className="flex items-center gap-2 px-2 py-2 mt-1 hover:bg-gray-800 rounded w-full text-sm text-gray-300">
            <span>⚙️</span>
            <span>Settings</span>
          </button>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <div className="bg-white border-b border-gray-100 px-4 py-3 flex items-center gap-3">
          {!sidebarOpen && (
            <button
              onClick={() => setSidebarOpen(true)}
              className="p-1.5 hover:bg-gray-100 rounded text-gray-600"
            >
              <svg width="20" height="20" fill="currentColor" viewBox="0 0 16 16">
                <path fillRule="evenodd" d="M2.5 12a.5.5 0 0 1 .5-.5h10a.5.5 0 0 1 0 1H3a.5.5 0 0 1-.5-.5zm0-4a.5.5 0 0 1 .5-.5h10a.5.5 0 0 1 0 1H3a.5.5 0 0 1-.5-.5zm0-4a.5.5 0 0 1 .5-.5h10a.5.5 0 0 1 0 1H3a.5.5 0 0 1-.5-.5z"/>
              </svg>
            </button>
          )}
          <h1 className="text-lg font-semibold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
            CHAT A.I+
          </h1>
          <div className="ml-auto flex items-center gap-2">
            <button className="p-1.5 hover:bg-gray-100 rounded">
              <svg width="18" height="18" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
                <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
                <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
              </svg>
            </button>
            <button className="p-1.5 hover:bg-gray-100 rounded">
              <svg width="18" height="18" fill="currentColor" viewBox="0 0 16 16">
                <path d="M3 9.5a1.5 1.5 0 1 1 0-3 1.5 1.5 0 0 1 0 3zm5 0a1.5 1.5 0 1 1 0-3 1.5 1.5 0 0 1 0 3zm5 0a1.5 1.5 0 1 1 0-3 1.5 1.5 0 0 1 0 3z"/>
              </svg>
            </button>
          </div>
        </div>

        {/* Messages Area */}
        <div className="flex-1 overflow-y-auto bg-white">
          <div className="max-w-3xl mx-auto px-4 py-6">
            {messages.map((msg, i) => (
              <div key={i} className="mb-8 flex gap-3">
                <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${
                  msg.direction === 'outgoing' 
                    ? 'bg-purple-600' 
                    : 'bg-gradient-to-br from-blue-500 to-purple-600'
                }`}>
                  <span className="text-white text-xs font-bold">
                    {msg.direction === 'outgoing' ? 'U' : 'AI'}
                  </span>
                </div>
                <div className="flex-1 pt-1">
                  <div className="text-xs font-semibold text-gray-600 mb-1">
                    {msg.sender === 'AI' ? 'CHAT A.I+' : msg.sender}
                  </div>
                  <div className="text-gray-800 text-sm leading-relaxed whitespace-pre-wrap">
                    {msg.message}
                  </div>
                  {msg.direction === 'incoming' && (
                    <div className="flex items-center gap-3 mt-3 text-gray-500">
                      <button className="hover:text-gray-700" title="Like">
                        👍
                      </button>
                      <button className="hover:text-gray-700" title="Dislike">
                        👎
                      </button>
                      <button className="hover:text-gray-700" title="Copy">
                        📋
                      </button>
                      <button className="hover:text-gray-700" title="More">
                        ⋯
                      </button>
                      <button className="ml-auto hover:text-gray-700 text-xs" title="Regenerate">
                        🔄 Regenerate
                      </button>
                    </div>
                  )}
                </div>
              </div>
            ))}
            
            {isTyping && (
              <div className="mb-8 flex gap-3">
                <div className="w-8 h-8 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center flex-shrink-0">
                  <span className="text-white text-xs font-bold">AI</span>
                </div>
                <div className="flex-1 pt-1">
                  <div className="text-xs font-semibold text-gray-600 mb-1">CHAT A.I+</div>
                  <div className="flex gap-1 items-center">
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
        <div className="bg-white border-t border-gray-100 p-4">
          <div className="max-w-3xl mx-auto">
            <form onSubmit={handleSend} className="relative">
              <div className="flex items-center gap-2 bg-gray-50 rounded-3xl border border-gray-200 px-4 py-2.5 hover:border-gray-300 focus-within:border-gray-400 transition-colors">
                <button type="button" className="text-gray-400 hover:text-gray-600">
                  ❤️
                </button>
                <input
                  type="text"
                  value={inputMessage}
                  onChange={(e) => setInputMessage(e.target.value)}
                  placeholder="What's in your mind?..."
                  className="flex-1 bg-transparent outline-none text-gray-800 placeholder-gray-400 text-sm"
                  disabled={isTyping}
                />
                <button
                  type="submit"
                  disabled={isTyping || !inputMessage.trim()}
                  className="w-8 h-8 bg-gradient-to-r from-blue-600 to-purple-600 rounded-full flex items-center justify-center text-white hover:opacity-90 transition-opacity disabled:opacity-40 disabled:cursor-not-allowed"
                >
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                    <path d="M22 2L11 13M22 2l-7 20-4-9-9-4 20-7z" />
                  </svg>
                </button>
              </div>
            </form>
            <div className="text-xs text-center text-gray-400 mt-2">
              Stateless UI - All conversation state persisted in database
            </div>
          </div>
        </div>
      </div>

      {/* Upgrade Sidebar (Right) */}
      <div className="w-64 bg-gradient-to-br from-blue-500 to-purple-600 text-white p-6 flex flex-col">
        <div className="flex-1">
          <div className="text-sm mb-3">Upgrade to</div>
          <h2 className="text-2xl font-bold mb-6">A.I+</h2>
          
          <div className="space-y-4 text-sm">
            <div className="flex items-start gap-2">
              <span>✨</span>
              <div>
                <div className="font-semibold">Unlimited access to GPT-4</div>
                <div className="text-xs opacity-90 mt-1">Our most capable model</div>
              </div>
            </div>
            
            <div className="flex items-start gap-2">
              <span>🎨</span>
              <div>
                <div className="font-semibold">Create images with DALL·E</div>
                <div className="text-xs opacity-90 mt-1">Generate unique visuals</div>
              </div>
            </div>
            
            <div className="flex items-start gap-2">
              <span>🎯</span>
              <div>
                <div className="font-semibold">Create and use custom GPTs</div>
                <div className="text-xs opacity-90 mt-1">Personalized AI assistants</div>
              </div>
            </div>
            
            <div className="flex items-start gap-2">
              <span>💬</span>
              <div>
                <div className="font-semibold">Higher message limits</div>
                <div className="text-xs opacity-90 mt-1">More conversations daily</div>
              </div>
            </div>
          </div>
        </div>
        
        <button className="w-full bg-white text-purple-600 font-semibold py-3 rounded-lg hover:bg-gray-100 transition-colors">
          Upgrade plan
        </button>
      </div>
    </div>
  );
}
