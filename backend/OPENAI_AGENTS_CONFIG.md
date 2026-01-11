# OpenAI Agents SDK Configuration

## Overview
The Todo chatbot uses OpenAI's Chat Completions API with function calling to create a stateless, scalable task management agent. This document explains the architecture and configuration.

## Architecture Principles

### 1. Stateless Agent Design
- **No memory in RAM**: Each request creates a fresh agent instance
- **Conversation state**: Stored exclusively in PostgreSQL database
- **Scalability**: Supports horizontal scaling without session affinity
- **Resource efficiency**: No memory leaks or state accumulation

### 2. Environment-Based Configuration
- **API Key**: Loaded from `OPENAI_API_KEY` environment variable
- **Settings**: Managed via Pydantic Settings with `.env` file support
- **Security**: API key never hardcoded, only in environment

### 3. MCP Tools as Callable Functions
- **Tool Registration**: MCP tools registered as OpenAI function definitions
- **Dynamic Attachment**: Tools attached per request (no global state)
- **Database Injection**: Database session injected into tool calls
- **Error Handling**: Structured error responses for graceful degradation

## Configuration Files

### 1. Environment Configuration (`.env`)
```env
OPENAI_API_KEY=sk-1234uvwx5678abcd1234uvwx5678abcd1234uvwx
DATABASE_URL=postgresql://username:password@localhost:5432/todo_chatbot
ENV=development
DEBUG=true
```

**Location**: `backend/.env`

**Security Notes**:
- Never commit `.env` to version control
- Use `.env.example` for templates
- Rotate API keys regularly

### 2. Agent Configuration Module (`app/agent/config.py`)

**Purpose**: Centralized agent configuration and settings

**Key Components**:
- `get_agent_config()`: Returns agent configuration per request
- `get_agent_system_prompt()`: Provides deterministic behavior prompt
- `build_agent_messages()`: Constructs message array with system prompt
- `MAX_CONTEXT_MESSAGES`: Context window size (50 messages)

**Configuration Parameters**:
```python
AGENT_MODEL = "gpt-4o-mini"  # Fast, cost-effective model
AGENT_TEMPERATURE = 0.7      # Balanced creativity
AGENT_MAX_TOKENS = 1000      # Response length limit
```

### 3. Agent Service (`app/agent/service.py`)

**Purpose**: Processes chat messages using OpenAI agent

**Stateless Flow**:
1. Create fresh `AsyncOpenAI` client with environment API key
2. Load conversation history from database (max 50 messages)
3. Build message array with system prompt
4. Attach MCP tools as callable functions
5. Call OpenAI API with function calling
6. Execute tool calls with database injection
7. Save response to database
8. Return response (no state retention)

**Key Function**:
```python
async def process_chat_message(
    session: Session,      # Database session
    user_id: str,          # User identifier
    message: str,          # User message
    conversation_id: Optional[int] = None
) -> Dict[str, Any]:
    # 1. Create fresh client (stateless)
    agent_config = get_agent_config()
    client = AsyncOpenAI(api_key=agent_config["api_key"])
    
    # 2. Load conversation from database
    # 3. Build messages with system prompt
    # 4. Attach MCP tools
    # 5. Call OpenAI API
    # 6. Execute tools
    # 7. Save to database
    # 8. Return response
```

## MCP Tool Integration

### Tool Definition Format
Tools are defined in OpenAI function calling format:
```python
{
    "type": "function",
    "function": {
        "name": "add_task",
        "description": "Create a new task for the user",
        "parameters": {
            "type": "object",
            "properties": {
                "user_id": {"type": "string"},
                "title": {"type": "string"},
                "description": {"type": "string"}
            },
            "required": ["user_id", "title"]
        }
    }
}
```

### Tool Registration
Tools are registered in `app/mcp/server.py`:
- `get_mcp_tools()`: Returns list of tool definitions
- `get_tool_function()`: Returns executable tool function

### Tool Execution
1. Agent decides to call tool based on user message
2. Service extracts tool name and arguments
3. Database session injected into tool call
4. Tool executes database operation
5. Result returned to agent for response generation

## Context Window Management

### Window Size: 50 Messages
- **Rationale**: Prevents OpenAI token limit errors
- **Implementation**: `load_message_history()` with LIMIT clause
- **Impact**: Last 50 messages sent to agent
- **History Preservation**: All messages retained in database

### Why 50 Messages?
- Typical conversation: 10-20 message exchanges
- Safety margin: 2-5x typical conversation length
- Token efficiency: ~2,000-5,000 tokens (well under 128k limit)
- Performance: Fast database queries

## Stateless Request Flow

```
User Request
    ↓
FastAPI Endpoint (/api/{user_id}/chat)
    ↓
process_chat_message()
    ├─ Create fresh OpenAI client (API key from env)
    ├─ Load conversation from DB (max 50 messages)
    ├─ Build messages with system prompt
    ├─ Attach MCP tools
    ├─ Call OpenAI API
    ├─ Execute tool calls (DB session injected)
    ├─ Save response to DB
    └─ Return response
    ↓
Response to User
```

**No State Retention**: Each request is independent, no global variables

## Security Considerations

### API Key Protection
- ✅ Loaded from environment variable
- ✅ Never logged or exposed in errors
- ✅ Not hardcoded in source code
- ✅ Sanitized in error messages

### Database Security
- ✅ User ID filtering on all queries
- ✅ Conversation ownership validation
- ✅ SQL injection prevention (SQLModel ORM)

### Error Handling
- ✅ Sanitized error messages (no credential exposure)
- ✅ Graceful degradation for tool failures
- ✅ User-friendly error responses

## Performance Optimization

### Database Efficiency
- **Indexed Queries**: Conversation ID and user ID indexed
- **Limited Fetches**: Only last 50 messages loaded
- **Connection Pooling**: SQLModel manages connection pool

### API Efficiency
- **Model Selection**: gpt-4o-mini for cost/speed balance
- **Token Limits**: Max 1000 tokens per response
- **Streaming**: Not implemented (not needed for task management)

### Scalability
- **Horizontal Scaling**: Stateless design supports load balancing
- **No Session Affinity**: Any server can handle any request
- **Database-Centric**: PostgreSQL handles state management

## Testing the Configuration

### 1. Verify Environment Setup
```bash
# Check .env file exists
ls backend/.env

# Verify API key is set
grep OPENAI_API_KEY backend/.env
```

### 2. Test Agent Configuration
```python
from app.agent.config import get_agent_config

config = get_agent_config()
print(f"Model: {config['model']}")
print(f"API Key Set: {bool(config['api_key'])}")
```

### 3. Test Chat Endpoint
```bash
# Start server
cd backend
uvicorn app.main:app --reload

# Send test message
curl -X POST http://localhost:8000/api/testuser/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Add task: Buy groceries"}'
```

## Troubleshooting

### Issue: OpenAI API Key Not Found
**Error**: `openai_api_key field required`

**Solution**:
1. Verify `.env` file exists in `backend/` directory
2. Check `OPENAI_API_KEY` is set in `.env`
3. Restart server to reload environment

### Issue: Database Connection Failed
**Error**: `Database connection failed`

**Solution**:
1. Verify PostgreSQL is running
2. Check `DATABASE_URL` in `.env`
3. Test connection with `python validate_db.py`

### Issue: Agent Not Calling Tools
**Error**: Agent responds without using tools

**Solution**:
1. Check system prompt in `app/agent/config.py`
2. Verify tools are registered in `app/mcp/server.py`
3. Review agent temperature (may be too low)

## Monitoring and Logging

### Logging Configuration
Located in `app/main.py`:
```python
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

### Key Log Points
- Database connectivity checks
- Agent request processing
- Tool execution results
- Error occurrences

### Production Recommendations
- Use structured logging (JSON format)
- Implement request tracing (correlation IDs)
- Monitor OpenAI API usage and costs
- Track response times and error rates

## Future Enhancements

### Potential Improvements
1. **Streaming Responses**: Implement SSE for real-time updates
2. **Conversation Summarization**: Compress old context for longer conversations
3. **Multi-Model Support**: A/B test different OpenAI models
4. **Caching**: Cache common queries for faster responses
5. **Rate Limiting**: Implement user-level rate limits

### Migration Considerations
- Current design supports easy model switching
- Stateless architecture enables blue-green deployments
- Database-centric design allows for read replicas

## References

- [OpenAI Function Calling](https://platform.openai.com/docs/guides/function-calling)
- [Pydantic Settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)
- [FastAPI Dependency Injection](https://fastapi.tiangolo.com/tutorial/dependencies/)
- [SQLModel Documentation](https://sqlmodel.tiangolo.com/)
