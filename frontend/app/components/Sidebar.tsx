/**
 * Sidebar Component
 * ChatGPT-style sidebar with conversation list UI (stateless)
 */

interface SidebarProps {
  conversationId: number | null;
}

export default function Sidebar({ conversationId }: SidebarProps) {
  return (
    <div style={{
      width: '260px',
      height: '100vh',
      backgroundColor: '#f7f7f8',
      borderRight: '1px solid #e5e5e5',
      display: 'flex',
      flexDirection: 'column',
      position: 'relative'
    }}>
      {/* Header */}
      <div style={{
        padding: '1rem',
        borderBottom: '1px solid #e5e5e5'
      }}>
        <h1 style={{
          fontSize: '1.125rem',
          fontWeight: 600,
          color: '#202123',
          margin: '0 0 1rem 0'
        }}>
          AI Todo Chatbot
        </h1>
        
        {/* New Chat Button */}
        <button
          style={{
            width: '100%',
            padding: '0.625rem 0.75rem',
            backgroundColor: 'white',
            border: '1px solid #d1d5db',
            borderRadius: '0.375rem',
            fontSize: '0.875rem',
            fontWeight: 500,
            color: '#374151',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            gap: '0.5rem',
            transition: 'all 0.2s'
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.backgroundColor = '#f9fafb';
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.backgroundColor = 'white';
          }}
        >
          <span style={{ fontSize: '1.125rem' }}>+</span>
          <span>New chat</span>
        </button>
      </div>

      {/* Conversation List */}
      <div style={{
        flex: 1,
        overflowY: 'auto',
        padding: '0.5rem'
      }}>
        {/* Current Conversation (UI Only) */}
        {conversationId && (
          <div
            style={{
              padding: '0.75rem',
              backgroundColor: '#ececf1',
              borderRadius: '0.375rem',
              marginBottom: '0.5rem',
              cursor: 'pointer',
              fontSize: '0.875rem',
              color: '#202123',
              position: 'relative'
            }}
          >
            <div style={{
              overflow: 'hidden',
              textOverflow: 'ellipsis',
              whiteSpace: 'nowrap',
              fontWeight: 500
            }}>
              Conversation #{conversationId}
            </div>
            <div style={{
              fontSize: '0.75rem',
              color: '#6e6e80',
              marginTop: '0.25rem'
            }}>
              Active session
            </div>
          </div>
        )}
        
        {/* Example Past Conversations (Static UI) */}
        <div
          style={{
            padding: '0.75rem',
            backgroundColor: 'transparent',
            borderRadius: '0.375rem',
            marginBottom: '0.5rem',
            cursor: 'pointer',
            fontSize: '0.875rem',
            color: '#565869',
            transition: 'background-color 0.2s'
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.backgroundColor = '#ececf1';
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.backgroundColor = 'transparent';
          }}
        >
          <div style={{
            overflow: 'hidden',
            textOverflow: 'ellipsis',
            whiteSpace: 'nowrap'
          }}>
            Previous conversations...
          </div>
        </div>
      </div>

      {/* Footer */}
      <div style={{
        padding: '1rem',
        borderTop: '1px solid #e5e5e5',
        fontSize: '0.75rem',
        color: '#6e6e80'
      }}>
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '0.5rem',
          padding: '0.5rem',
          backgroundColor: 'white',
          borderRadius: '0.375rem',
          border: '1px solid #e5e5e5'
        }}>
          <div style={{
            width: '24px',
            height: '24px',
            borderRadius: '50%',
            backgroundColor: '#10a37f',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: 'white',
            fontSize: '0.75rem',
            fontWeight: 600
          }}>
            HT
          </div>
          <span style={{ color: '#202123', fontSize: '0.875rem' }}>Hareem Tariq</span>
        </div>
      </div>
    </div>
  );
}
