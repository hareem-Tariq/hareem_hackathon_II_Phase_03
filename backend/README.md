# Backend - AI Todo Chatbot

## Overview

Stateless FastAPI backend with OpenAI Agents and MCP tools for conversational task management.

## Architecture

- **Framework**: FastAPI 0.109.0+
- **Database**: Neon Serverless PostgreSQL via SQLModel
- **AI**: OpenAI Agents SDK with function calling
- **MCP**: Official MCP SDK for tool implementation
- **State**: Fully persisted in database (stateless server)

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Configure environment (`.env`):
   ```
   DATABASE_URL=postgresql://user:pass@host:5432/db
   OPENAI_API_KEY=your_key_here
   ```

3. Run migrations:
   ```bash
   alembic upgrade head
   ```

4. Start server:
   ```bash
   uvicorn app.main:app --reload
   ```

## API Documentation

Once running, visit:
- API Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

## MCP Tools

All tools are stateless and operate directly on the database:

1. **add_task(user_id, title, description)** → Create task
2. **list_tasks(user_id, status)** → List tasks with filters
3. **update_task(user_id, task_id, title?, description?)** → Update task
4. **complete_task(user_id, task_id, completed)** → Toggle completion
5. **delete_task(user_id, task_id)** → Delete task

## Database Models

### Task
- Fields: id, user_id, title, description, completed, created_at, updated_at
- Indexes: user_id, completed

### Conversation
- Fields: id, user_id, created_at, updated_at
- Indexes: user_id

### Message
- Fields: id, conversation_id, user_id, role, content, created_at
- Indexes: conversation_id, user_id, created_at

## Development

### Running Tests
```bash
pytest
```

### Creating Migrations
```bash
alembic revision --autogenerate -m "description"
alembic upgrade head
```

### Code Organization
```
app/
├── agent/          # OpenAI Agent service
├── models/         # SQLModel database models
├── mcp/            # MCP server and tools
│   └── tools/      # Individual MCP tool implementations
├── routes/         # FastAPI route handlers
├── schemas/        # Pydantic request/response schemas
├── config.py       # Settings and configuration
├── database.py     # Database engine and session management
└── main.py         # FastAPI application entry point
```

## Key Principles

- **Stateless**: No in-memory state, everything in DB
- **Scalable**: Supports multiple backend instances
- **MCP Compliant**: Official SDK, stateless tools
- **OpenAI Agents**: Function calling for intelligent task management

## Deployment

Recommended: Heroku, Railway, or any platform supporting Python

1. Set environment variables
2. Run migrations: `alembic upgrade head`
3. Start: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
