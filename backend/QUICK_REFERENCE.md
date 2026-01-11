# OpenAI Agents SDK - Quick Reference

## Configuration Overview

### Environment Variables (.env)
```env
OPENAI_API_KEY=sk-1234uvwx5678abcd1234uvwx5678abcd1234uvwx
DATABASE_URL=postgresql://username:password@localhost:5432/todo_chatbot
ENV=development
DEBUG=true
```

### Agent Settings (app/agent/config.py)
```python
AGENT_MODEL = "gpt-4o-mini"       # Model
AGENT_TEMPERATURE = 0.7            # Creativity (0-1)
AGENT_MAX_TOKENS = 1000            # Max response length
MAX_CONTEXT_MESSAGES = 50          # Context window size
```

## Stateless Architecture

### Per-Request Flow
```
1. Create fresh AsyncOpenAI client (API key from env)
2. Load conversation from database (max 50 messages)
3. Build messages with system prompt
4. Attach MCP tools
5. Call OpenAI API
6. Execute tool calls
7. Save to database
8. Return response
```

### No Memory Storage
- ❌ No global OpenAI client
- ❌ No agent state in RAM
- ✅ All state in PostgreSQL
- ✅ Fresh client per request
- ✅ Horizontal scaling ready

## MCP Tools

### Available Tools
1. **add_task** - Create new task
2. **list_tasks** - View tasks (all/pending/completed)
3. **update_task** - Modify existing task
4. **delete_task** - Remove task
5. **complete_task** - Mark task as done

### Tool Execution
- Tools attached per request (no global state)
- Database session automatically injected
- Structured error handling
- Results returned to agent for response

## Key Functions

### get_agent_config()
Returns configuration for fresh agent per request:
```python
{
    "model": "gpt-4o-mini",
    "temperature": 0.7,
    "max_tokens": 1000,
    "api_key": settings.openai_api_key  # From environment
}
```

### process_chat_message()
Main entry point for chat processing:
```python
result = await process_chat_message(
    session=db,              # Database session
    user_id="user123",       # User identifier
    message="Add buy milk",  # User message
    conversation_id=None     # Optional existing conversation
)
```

Returns:
```python
{
    "conversation_id": 1,
    "response": "I've added 'buy milk' to your list.",
    "tool_calls": [...]
}
```

## Testing

### Run Verification
```bash
cd backend
python verify_agent_config.py
```

### Expected Output
```
✓ PASS: Environment Variables
✓ PASS: Agent Configuration
✓ PASS: MCP Tools
✓ PASS: Stateless Architecture
🎉 All tests passed!
```

## Common Commands

### Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### Run Migrations
```bash
cd backend
alembic upgrade head
```

### Start Server
```bash
cd backend
uvicorn app.main:app --reload
```

### Test Chat Endpoint
```bash
curl -X POST http://localhost:8000/api/testuser/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Add task: Buy groceries"}'
```

## Security Checklist

- ✅ API key in environment (not hardcoded)
- ✅ User ID filtering on all queries
- ✅ Conversation ownership validation
- ✅ Error message sanitization
- ✅ .env not in version control

## Performance Tips

- ✅ Context window limited to 50 messages
- ✅ Database queries indexed (user_id, conversation_id)
- ✅ Connection pooling enabled
- ✅ gpt-4o-mini for speed/cost balance

## Troubleshooting

### API Key Not Found
1. Check `.env` file exists in `backend/`
2. Verify `OPENAI_API_KEY` is set
3. Restart server to reload environment

### Database Connection Error
1. Check PostgreSQL is running
2. Verify `DATABASE_URL` in `.env`
3. Test with `python validate_db.py`

### Tools Not Working
1. Verify tools in `app/mcp/server.py`
2. Check database session injection
3. Review system prompt in `app/agent/config.py`

## Documentation

- **Comprehensive Guide**: [OPENAI_AGENTS_CONFIG.md](OPENAI_AGENTS_CONFIG.md)
- **Setup Summary**: [AGENT_SETUP_SUMMARY.md](AGENT_SETUP_SUMMARY.md)
- **Verification Script**: `verify_agent_config.py`

---
**Quick Start**: Run `python verify_agent_config.py` to verify configuration
