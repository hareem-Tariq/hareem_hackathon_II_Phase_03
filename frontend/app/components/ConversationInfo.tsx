/**
 * ConversationInfo Component
 * Displays current conversation state information
 */

interface ConversationInfoProps {
  conversationId: number | null;
  messageCount: number;
}

export default function ConversationInfo({ conversationId, messageCount }: ConversationInfoProps) {
  if (!conversationId) return null;

  return (
    <div style={{
      display: 'flex',
      gap: '1rem',
      alignItems: 'center',
      justifyContent: 'center',
      fontSize: '0.75rem',
      opacity: 0.7,
      marginTop: '0.25rem'
    }}>
      <span>
        💬 Conversation: <strong>#{conversationId}</strong>
      </span>
      <span>|</span>
      <span>
        📝 Messages: <strong>{messageCount}</strong>
      </span>
      <span>|</span>
      <span style={{ color: '#4caf50' }}>
        ● Stateless UI
      </span>
    </div>
  );
}
