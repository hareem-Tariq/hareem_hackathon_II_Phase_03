/**
 * ToolCallDisplay Component
 * Displays MCP tool call confirmations in a visually appealing way
 */

interface ToolCall {
  tool: string;
  arguments: Record<string, any>;
  result?: Record<string, any>;
  error?: string;
}

interface ToolCallDisplayProps {
  toolCalls: ToolCall[];
}

export default function ToolCallDisplay({ toolCalls }: ToolCallDisplayProps) {
  if (!toolCalls || toolCalls.length === 0) return null;

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

  const getToolColor = (tool: string, hasError: boolean): string => {
    if (hasError) return '#f44336';
    switch (tool) {
      case 'add_task': return '#4caf50';
      case 'list_tasks': return '#2196f3';
      case 'update_task': return '#ff9800';
      case 'complete_task': return '#8bc34a';
      case 'delete_task': return '#9e9e9e';
      default: return '#607d8b';
    }
  };

  return (
    <div style={{
      marginTop: '0.5rem',
      padding: '0.75rem',
      background: '#f5f5f5',
      borderRadius: '8px',
      fontSize: '0.85rem'
    }}>
      <div style={{ 
        fontWeight: 600, 
        marginBottom: '0.5rem',
        color: '#666',
        fontSize: '0.8rem',
        textTransform: 'uppercase',
        letterSpacing: '0.5px'
      }}>
        Actions Performed:
      </div>
      {toolCalls.map((tc, idx) => (
        <div
          key={idx}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '0.5rem',
            padding: '0.5rem',
            marginBottom: idx < toolCalls.length - 1 ? '0.25rem' : 0,
            background: 'white',
            borderRadius: '4px',
            borderLeft: `3px solid ${getToolColor(tc.tool, !!tc.error)}`
          }}
        >
          <span style={{ fontSize: '1.2rem' }}>{getToolIcon(tc.tool)}</span>
          <div style={{ flex: 1 }}>
            {tc.error ? (
              <span style={{ color: '#f44336' }}>
                <strong>{tc.tool}</strong> failed: {tc.error}
              </span>
            ) : (
              <>
                {tc.tool === 'add_task' && (
                  <span>
                    Created task: <strong>"{tc.result?.title}"</strong> (ID: {tc.result?.task_id})
                  </span>
                )}
                {tc.tool === 'list_tasks' && (
                  <span>
                    Retrieved <strong>{tc.result?.length || 0}</strong> task(s)
                  </span>
                )}
                {tc.tool === 'update_task' && (
                  <span>
                    Updated task <strong>{tc.arguments.task_id}</strong>: "{tc.result?.title}"
                  </span>
                )}
                {tc.tool === 'complete_task' && (
                  <span>
                    Marked task <strong>{tc.arguments.task_id}</strong> as <em>{tc.result?.status}</em>
                  </span>
                )}
                {tc.tool === 'delete_task' && (
                  <span>
                    Deleted task: <strong>"{tc.result?.title}"</strong>
                  </span>
                )}
              </>
            )}
          </div>
        </div>
      ))}
    </div>
  );
}
