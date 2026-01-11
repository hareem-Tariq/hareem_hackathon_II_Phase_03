# Phase III: AI-Powered Todo Chatbot

A full-stack AI-powered conversational todo application built with Next.js, FastAPI, PostgreSQL, and OpenAI GPT-4o-mini.

## 🌟 Overview

This is an intelligent todo chatbot that allows users to manage their tasks through natural language conversations. Built with a stateless architecture for scalability and reliability.

## 🏗️ Architecture

### Tech Stack

**Frontend:**
- Next.js 14 with TypeScript
- React with Tailwind CSS
- Deployed on Vercel

**Backend:**
- FastAPI (Python 3.11)
- SQLModel + SQLAlchemy
- Deployed on Heroku

**Database:**
- Neon PostgreSQL (Serverless)
- SSL-enabled connection pooling

**AI:**
- OpenAI GPT-4o-mini
- Model Context Protocol (MCP) tools
- Stateless agent architecture

### Key Features

✨ **Natural Language Processing**
- Add tasks: "Add a task to buy groceries"
- List tasks: "Show me my tasks" or "What do I need to do?"
- Complete tasks: "Mark task 1 as done"
- Delete tasks: "Delete the groceries task"
- Update tasks: "Change task 2 to 'finish report'"

🔧 **MCP Tools Integration**
- `add_task`: Create new tasks
- `list_tasks`: Retrieve tasks with filtering
- `complete_task`: Mark tasks as completed
- `delete_task`: Remove tasks
- `update_task`: Modify task details

💬 **Stateless Conversation**
- Each request loads conversation history from database
- No server-side session storage
- Persists across server restarts
- Conversation continuity maintained

🔒 **Security**
- All secrets stored in environment variables
- SSL/TLS for database connections
- CORS configured for production
- No hardcoded credentials

## 🚀 Local Development

### Prerequisites

- Node.js 18+ and npm
- Python 3.11+
- PostgreSQL database (Neon recommended)
- OpenAI API key

### Backend Setup

1. Navigate to backend directory:
```bash
cd backend
```

2. Create virtual environment:
```bash
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # macOS/Linux
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create `.env` file:
```env
DATABASE_URL=postgresql://user:password@host-pooler.region.aws.neon.tech/dbname?sslmode=require
OPENAI_API_KEY=sk-your-api-key-here
ENV=development
DEBUG=true
```

5. Run the backend:
```bash
python main.py
```

Backend will be available at: http://localhost:8000

### Frontend Setup

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Create `.env.local` file:
```env
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
NEXT_PUBLIC_USER_ID=demo_user
NEXT_PUBLIC_OPENAI_DOMAIN_KEY=
```

4. Run the development server:
```bash
npm run dev
```

Frontend will be available at: http://localhost:3000

## 📦 Production Deployment

See [DEPLOYMENT.md](./DEPLOYMENT.md) for detailed deployment instructions.

### Quick Overview

**Backend (Heroku):**
```bash
git push heroku main
heroku config:set DATABASE_URL=<neon-url>
heroku config:set OPENAI_API_KEY=<your-key>
```

**Frontend (Vercel):**
```bash
vercel --prod
```

## 🧪 Testing

### Backend Health Check
```bash
curl http://localhost:8000/health
```

### API Endpoints

- `GET /` - Root endpoint
- `GET /health` - Health check
- `POST /api/{user_id}/chat` - Chat endpoint

## 📖 Documentation

- [DEPLOYMENT.md](./DEPLOYMENT.md) - Deployment guide
- [FEATURES.md](./FEATURES.md) - Feature documentation
- [QUICKSTART.md](./QUICKSTART.md) - Quick start guide
