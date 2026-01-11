# Frontend - AI Todo Chatbot

## Overview

Next.js frontend with OpenAI ChatKit for conversational task management. Features a **stateless UI architecture** with full conversation state persistence in the backend database.

## Technology

- **Framework**: Next.js 14 (App Router)
- **UI Library**: @chatscope/chat-ui-kit-react (OpenAI ChatKit)
- **Styling**: Tailwind CSS + Custom CSS
- **Language**: TypeScript
- **State Management**: React hooks (display only, no persistence)

## Key Features

### ✅ Stateless Chat UI
- No client-side persistence
- All conversation state stored in backend database
- Conversation continuity via `conversation_id`
- Can refresh page without losing chat history

### ✅ Conversation ID Handling
- First message creates new conversation
- Subsequent messages use existing `conversation_id`
- Backend returns `conversation_id` in every response
- Frontend tracks ID for request continuity

### ✅ Assistant Response Display
- Real-time message rendering
- Typing indicators during processing
- Error handling with user-friendly messages
- Smooth scrolling to new messages

### ✅ Tool Call Confirmations
- Visual display of MCP tool executions
- Color-coded by tool type:
  - ➕ Add Task (Green)
  - 📋 List Tasks (Blue)
  - ✏️ Update Task (Orange)
  - ✅ Complete Task (Light Green)
  - 🗑️ Delete Task (Gray)
- Shows tool results inline with responses
- Error states clearly indicated

### ✅ Domain Allowlist Key Support
- Environment variable: `NEXT_PUBLIC_OPENAI_DOMAIN_KEY`
- Sent as `X-OpenAI-Domain-Key` header
- Required for production deployment on custom domains

## Setup

1. Install dependencies:
   ```bash
   npm install
   ```

2. Configure environment (`.env.local`):
   ```env
   NEXT_PUBLIC_API_URL=http://localhost:8000
   NEXT_PUBLIC_USER_ID=demo_user
   NEXT_PUBLIC_OPENAI_DOMAIN_KEY=your_domain_key_here
   ```

3. Start development server:
   ```bash
   npm run dev
   ```

4. Open http://localhost:3000

## Project Structure

```
frontend/
├── app/
│   ├── components/
│   │   ├── ConversationInfo.tsx    # Conversation state display
│   │   └── ToolCallDisplay.tsx     # Tool confirmation UI
│   ├── chat/
│   │   └── page.tsx                # Enhanced chat page
│   ├── page.tsx                    # Main chat interface
│   ├── layout.tsx                  # Root layout
│   └── globals.css                 # Global styles
├── .env.local.example              # Environment template
├── next.config.js                  # Next.js configuration
├── package.json                    # Dependencies
├── tailwind.config.js              # Tailwind configuration
└── tsconfig.json                   # TypeScript configuration
```

## Usage Examples

Try these natural language commands:

### Adding Tasks
- "Add a task to buy groceries"
- "Remind me to call mom tomorrow"
- "Create a task: finish project report by Friday"

### Listing Tasks
- "Show me my tasks"
- "What do I need to do?"
- "List all pending tasks"
- "Show completed tasks"

### Updating Tasks
- "Update task 1 to 'Buy milk and eggs'"
- "Change the description of task 2"

### Completing Tasks
- "Mark task 1 as complete"
- "I finished task 3"
- "Complete the groceries task"

### Deleting Tasks
- "Delete task 1"
- "Remove the groceries task"

## API Integration

### Request Format

```typescript
POST /api/{user_id}/chat

Headers:
  Content-Type: application/json
  X-OpenAI-Domain-Key: {domain_key}  // Optional

Body:
{
  "message": "Add a task to buy groceries",
  "conversation_id": 1  // Optional, null for new conversation
}
```

### Response Format

```typescript
{
  "conversation_id": 1,
  "response": "I've added 'Buy groceries' to your task list.",
  "tool_calls": [
    {
      "tool": "add_task",
      "arguments": {
        "user_id": "demo_user",
        "title": "Buy groceries"
      },
      "result": {
        "task_id": 1,
        "status": "created",
        "title": "Buy groceries"
      }
    }
  ]
}
```

## Stateless Architecture

### How It Works

1. **User sends message** → Frontend sends to backend with `conversation_id`
2. **Backend processes** → Loads conversation from DB, calls OpenAI Agent
3. **Agent executes tools** → MCP tools query/update database
4. **Backend saves state** → Conversation + messages saved to DB
5. **Response returned** → Frontend displays, updates `conversation_id`

### No Client-Side Persistence

- Messages displayed are NOT stored in browser
- Refresh page = messages lost from UI (but preserved in DB)
- All state recovered by fetching conversation history (future enhancement)
- True stateless client architecture

## Customization

### Changing Colors

Edit `app/page.tsx` or `app/chat/page.tsx`:

```typescript
// Header gradient
background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'

// Tool colors
const toolColors = {
  add_task: '#4caf50',     // Green
  list_tasks: '#2196f3',   // Blue
  update_task: '#ff9800',  // Orange
  complete_task: '#8bc34a',// Light Green
  delete_task: '#9e9e9e'   // Gray
}
```

### Adding User Authentication

Replace `NEXT_PUBLIC_USER_ID` with actual user ID from auth:

```typescript
// Example with NextAuth
import { useSession } from 'next-auth/react';

const { data: session } = useSession();
const userId = session?.user?.id || 'guest';
```

### Custom Message Styling

ChatKit messages can be styled via CSS:

```css
/* In globals.css */
.cs-message--incoming {
  background-color: #f0f0f0;
}

.cs-message--outgoing {
  background-color: #007bff;
  color: white;
}
```

## Development

### Running in Development Mode

```bash
npm run dev
```

- Hot reload enabled
- TypeScript type checking
- API calls to localhost:8000

### Building for Production

```bash
npm run build
npm start
```

### Type Checking

```bash
npx tsc --noEmit
```

### Linting

```bash
npm run lint
```

## Deployment

### Vercel (Recommended)

1. **Push to GitHub**
   ```bash
   git push origin main
   ```

2. **Import in Vercel**
   - Go to https://vercel.com
   - New Project → Import from GitHub
   - Select repository
   - Set root directory to `frontend`

3. **Environment Variables**
   ```
   NEXT_PUBLIC_API_URL=https://your-backend.herokuapp.com
   NEXT_PUBLIC_USER_ID=demo_user
   NEXT_PUBLIC_OPENAI_DOMAIN_KEY=your_key_here
   ```

4. **Deploy**
   - Automatic deployment on every push
   - Preview deployments for PRs

### OpenAI Domain Allowlist

For production deployment:

1. Go to OpenAI Dashboard
2. Navigate to Domain Allowlist settings
3. Add your Vercel domain
4. Copy the domain key
5. Set `NEXT_PUBLIC_OPENAI_DOMAIN_KEY` in Vercel

## Components

### ConversationInfo

Displays current conversation metadata:
- Conversation ID
- Message count
- Stateless UI indicator

```tsx
<ConversationInfo 
  conversationId={conversationId} 
  messageCount={messageCount}
/>
```

### ToolCallDisplay (Optional)

Enhanced visual display for tool confirmations:
- Color-coded by tool type
- Icons for each tool
- Success/error states

## Performance

- **Bundle Size**: ~500KB (with ChatKit)
- **First Load**: ~2s
- **Message Send**: ~1-3s (depends on OpenAI API)
- **Optimizations**: React memoization, lazy loading

## Troubleshooting

### API Connection Failed

**Error**: `Failed to send message`

**Solutions**:
- Check `NEXT_PUBLIC_API_URL` is correct
- Ensure backend is running
- Verify CORS is configured in backend

### Domain Key Invalid

**Error**: `Invalid domain key`

**Solutions**:
- Verify key in OpenAI dashboard
- Check environment variable is set
- Ensure domain is allowlisted

### Messages Not Displaying

**Issue**: Chat interface blank

**Solutions**:
- Check browser console for errors
- Verify ChatKit styles are imported
- Clear browser cache and rebuild

### Conversation Not Persisting

**Issue**: `conversation_id` not maintained

**Solutions**:
- Check backend response includes `conversation_id`
- Verify state management in `handleSend`
- Check network tab for API responses

## Future Enhancements

- [ ] Load conversation history on mount
- [ ] User authentication integration
- [ ] Message markdown rendering
- [ ] File attachments
- [ ] Voice input
- [ ] Multi-language support
- [ ] Dark mode
- [ ] Message search
- [ ] Export conversation

## Support

For issues:
1. Check browser console
2. Verify environment variables
3. Test backend API directly
4. Review [QUICKSTART.md](../QUICKSTART.md)

## License

MIT License

