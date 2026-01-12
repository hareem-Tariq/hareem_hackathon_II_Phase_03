'use client';

import { useState } from 'react';
import {
  MainContainer,
  ChatContainer,
  MessageList,
  Message,
  MessageInput,
  TypingIndicator,
} from '@chatscope/chat-ui-kit-react';
import Sidebar from './components/Sidebar';

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
  position?: 'single' | 'first' | 'normal' | 'last';
  toolCalls?: ToolCall[];
}

export default function Home() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isTyping, setIsTyping] = useState(false);
  const [conversationId, setConversationId] = useState<number | null>(null);

  const handleSend = async (message: string) => {
    // Add user message to UI (stateless - no persistence in component state beyond display)
    const newMessage: ChatMessage = {
      message,
      sender: 'User',
      direction: 'outgoing',
      position: 'single'
    };
    setMessages(prevMessages => [...prevMessages, newMessage]);
    setIsTyping(true);

    try {
      // Send message to backend with conversation_id for state continuity
      const response = await fetch(`${API_URL}/api/${USER_ID}/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(DOMAIN_KEY && { 'X-Domain-Key': DOMAIN_KEY })
        },
        body: JSON.stringify({
          message,
          conversation_id: conversationId, // Send back conversation_id for stateless continuity
        }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || 'Failed to send message');
      }

      const data = await response.json();

      // Update conversation ID for subsequent requests (stateless tracking)
      if (!conversationId && data.conversation_id) {
        setConversationId(data.conversation_id);
      }

      // Add AI response to UI with tool calls (no business logic - just display)
      const aiResponse: ChatMessage = {
        message: data.response,
        sender: 'AI',
        direction: 'incoming',
        position: 'single',
        toolCalls: data.tool_calls
      };
      setMessages(prevMessages => [...prevMessages, aiResponse]);
    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage: ChatMessage = {
        message: `Error: ${error instanceof Error ? error.message : 'Failed to send message'}`,
        sender: 'System',
        direction: 'incoming',
        position: 'single'
      };
      setMessages(prevMessages => [...prevMessages, errorMessage]);
    } finally {
      setIsTyping(false);
    }
  };

  return (
    <div style={{ 
      display: 'flex', 
      height: '100vh',
      overflow: 'hidden',
      fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif'
    }}>
      {/* Left Sidebar */}
      <Sidebar conversationId={conversationId} />

      {/* Main Chat Area */}
      <main style={{ 
        flex: 1, 
        display: 'flex', 
        flexDirection: 'column',
        background: '#ffffff',
        position: 'relative'
      }}>
        <div style={{ flex: 1, position: 'relative', overflow: 'hidden' }}>
          <MainContainer style={{ 
            border: 'none',
            background: '#ffffff',
            height: '100%'
          }}>
            <ChatContainer style={{ background: '#ffffff' }}>
              <MessageList
                scrollBehavior="smooth"
                typingIndicator={isTyping ? <TypingIndicator content="Thinking..." /> : null}
                style={{
                  background: '#ffffff'
                }}
              >
                {messages.length === 0 && !isTyping && (
                  <Message
                    model={{
                      message: '',
                      sender: 'System',
                      direction: 'incoming',
                      position: 'single'
                    }}
                  >
                    <Message.CustomContent>
                      <div style={{
                        display: 'flex',
                        flexDirection: 'column',
                        alignItems: 'center',
                        justifyContent: 'center',
                        textAlign: 'center',
                        padding: '80px 20px',
                        maxWidth: '600px',
                        margin: '0 auto',
                        minHeight: '50vh'
                      }}>
                        <div style={{ 
                          fontSize: '48px', 
                          marginBottom: '24px',
                          width: '72px',
                          height: '72px',
                          borderRadius: '16px',
                          background: 'linear-gradient(135deg, #10a37f 0%, #0d8a6a 100%)',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          color: 'white',
                          boxShadow: '0 4px 14px rgba(16, 163, 127, 0.25)'
                        }}>
                          <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                            <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
                          </svg>
                        </div>
                        <h2 style={{ 
                          fontSize: '28px', 
                          fontWeight: 600, 
                          color: '#202123',
                          margin: '0 0 12px 0',
                          letterSpacing: '-0.5px'
                        }}>
                          Hello, I'm here to help
                        </h2>
                        <p style={{ 
                          fontSize: '16px', 
                          margin: 0,
                          color: '#6e6e80',
                          lineHeight: '1.5'
                        }}>
                          Ask me to manage your tasks
                        </p>
                      </div>
                    </Message.CustomContent>
                  </Message>
                )}
                {messages.map((msg, i) => {
                  // Build message text with tool confirmations inline
                  let messageText = msg.message;
                  if (msg.direction === 'incoming' && msg.toolCalls && msg.toolCalls.length > 0) {
                    const toolSummary = msg.toolCalls.map(tc => 
                      tc.error ? `✗ ${tc.tool}` : `✓ ${tc.tool}`
                    ).join(' | ');
                    messageText += `\n\n⚙ Actions: ${toolSummary}`;
                  }
                  
                  return (
                    <Message
                      key={i}
                      model={{
                        message: messageText,
                        sender: msg.sender,
                        direction: msg.direction,
                        position: msg.position || 'single'
                      }}
                    />
                  );
                })}
              </MessageList>
              <MessageInput
                placeholder="Ask me to add, list, or complete a task..."
                onSend={handleSend}
                attachButton={false}
                disabled={isTyping}
              />
            </ChatContainer>
          </MainContainer>
        </div>
      </main>
    </div>
  );
}
