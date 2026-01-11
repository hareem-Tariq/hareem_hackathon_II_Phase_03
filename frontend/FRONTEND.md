# Frontend - AI Todo Chatbot

## Requirements Met

✅ **Stateless UI**
- No business logic in frontend components
- All state persisted in backend database
- Frontend only tracks conversation_id for continuity
- Messages displayed from API responses

✅ **Conversation Continuity**
- Sends `conversation_id` back on each message
- Backend maintains conversation state in database
- Frontend receives conversation_id from first message

✅ **Assistant Replies**
- Displays AI responses from backend
- Shows typing indicator during processing
- Clean message display with ChatKit components

✅ **Tool Action Confirmations**
- Visual display of tool calls with icons
- Color-coded actions (add=green, delete=gray, etc.)
- Shows success/error states
- Formatted tool results (task IDs, counts, statuses)

✅ **Environment Configuration**
- Uses `NEXT_PUBLIC_OPENAI_DOMAIN_KEY` from .env.local
- Configurable API URL and User ID
- Domain key sent in X-Domain-Key header

✅ **No Business Logic**
- Frontend is purely presentational
- All task logic handled by backend
- No task state management in frontend
- No validation or data transformation

## Setup

### 1. Install Dependencies
```bash
npm install
```

### 2. Configure Environment
Create `.env.local` file:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_USER_ID=demo_user
NEXT_PUBLIC_OPENAI_DOMAIN_KEY=your_domain_key_here
```

### 3. Run Development Server
```bash
npm run dev
```

Visit http://localhost:3000

### 4. Build for Production
```bash
npm run build
npm start
```

## Architecture

### Stateless Design
The frontend maintains **zero business logic** and **minimal state**:
- Only tracks `conversation_id` for backend continuity
- All conversation history loaded from backend database
- Messages displayed directly from API responses
- Tool call results formatted for display only

### API Integration
```typescript
POST /api/{user_id}/chat
Headers:
  Content-Type: application/json
  X-Domain-Key: {NEXT_PUBLIC_OPENAI_DOMAIN_KEY}
Body:
  {
    "message": "Add a task to buy milk",
    "conversation_id": 123  // null for first message
  }
Response:
  {
    "conversation_id": 123,
    "response": "I've added that task for you!",
    "tool_calls": [
      {
        "tool": "add_task",
        "arguments": {"user_id": "demo_user", "title": "Buy milk"},
        "result": {"task_id": 1, "title": "Buy milk", "status": "pending"}
      }
    ]
  }
```

### Components

#### page.tsx (Main Chat Interface)
- Stateless chat UI using ChatKit
- Sends messages with conversation_id
- Displays AI responses and tool confirmations
- No task management logic

#### ToolCallDisplay.tsx
- Visual component for tool action confirmations
- Color-coded by action type
- Shows success/error states
- Purely presentational

#### ConversationInfo.tsx
- Displays conversation metadata
- Shows conversation ID and message count
- Indicates stateless UI status

## Tech Stack

- **Next.js 14**: React framework with App Router
- **ChatKit**: @chatscope/chat-ui-kit-react for chat UI
- **TypeScript**: Type-safe development
- **Tailwind CSS**: Utility-first styling

## Deployment

### Vercel (Recommended)
1. Push code to GitHub
2. Import project in Vercel
3. Set environment variables:
   - `NEXT_PUBLIC_API_URL`
   - `NEXT_PUBLIC_USER_ID`
   - `NEXT_PUBLIC_OPENAI_DOMAIN_KEY`
4. Deploy

### Docker
```bash
docker build -t todo-chatbot-frontend .
docker run -p 3000:3000 \
  -e NEXT_PUBLIC_API_URL=https://api.example.com \
  -e NEXT_PUBLIC_USER_ID=demo_user \
  -e NEXT_PUBLIC_OPENAI_DOMAIN_KEY=your_key \
  todo-chatbot-frontend
```

## Features

### Chat Interface
- Clean, modern chat UI
- Typing indicators
- Message history display
- Smooth scrolling

### Tool Call Display
- **Add Task** (➕): Shows task title and ID
- **List Tasks** (📋): Shows task count
- **Update Task** (✏️): Shows updated task
- **Complete Task** (✅): Shows completion status
- **Delete Task** (🗑️): Shows deleted task title

### Error Handling
- Displays backend error messages
- Friendly error formatting
- No technical details exposed

## Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `NEXT_PUBLIC_API_URL` | Backend API URL | Yes | http://localhost:8000 |
| `NEXT_PUBLIC_USER_ID` | User identifier | Yes | demo_user |
| `NEXT_PUBLIC_OPENAI_DOMAIN_KEY` | OpenAI domain allowlist key | No | (empty) |

## Notes

- Frontend is **completely stateless** - all state in backend database
- No localStorage, sessionStorage, or cookies used
- `conversation_id` tracked only for current session
- Refresh page = new conversation (by design)
- All business logic happens in backend via MCP tools
