# SchoolOps - AI-Powered School Management System

A comprehensive cloud/mobile/web system that automates school operations with advanced AI capabilities.

## Tech Stack

### Frontend
- **Next.js 14** - React framework with App Router
- **TypeScript** - Type safety
- **Tailwind CSS** - Utility-first styling
- **Lucide React** - Icon library
- **Recharts** - Data visualization

### Backend
- **Python FastAPI** - High-performance API framework
- **Strawberry GraphQL** - GraphQL implementation
- **PostgreSQL** - Primary database
- **Redis** - Caching and sessions
- **ElasticSearch** - Search and analytics

### AI Services
- **Python FastAPI** - Microservices framework
- **PyTorch/TensorFlow** - ML model training
- **Hugging Face Transformers** - Pre-trained models
- **OpenAI API** - LLM integration
- **LangChain** - AI agent orchestration
- **LangGraph** - Workflow automation

## Project Structure

```
schoolops-system/
├── frontend/                 # Next.js frontend application
│   ├── src/
│   │   ├── app/             # App Router pages
│   │   ├── components/      # React components
│   │   ├── lib/            # Utilities and configs
│   │   └── styles/         # Global styles
│   └── package.json
│
├── backend/                 # FastAPI GraphQL backend
│   ├── app/
│   │   ├── schema/         # GraphQL schema
│   │   ├── models/         # Database models
│   │   ├── services/       # Business logic
│   │   ├── graphql/        # Resolvers
│   │   └── middleware/     # Auth, logging
│   ├── requirements.txt
│   └── main.py
│
├── ai-services/            # AI microservices
│   ├── analytics/         # Predictions & insights
│   ├── personalization/   # Learning paths
│   ├── automation/        # AI assistants
│   ├── nlp/               # Chatbot & NLP
│   ├── vision/            # Document OCR
│   └── optimization/      # Timetable & routes
│
└── database/              # Database schema
    ├── models.sql         # SQLAlchemy models
    └── migrations/        # Alembic migrations
```

## Core Modules

1. **Admin & Setup** - School profiles, RBAC, bulk import
2. **Student Information System** - Profiles, enrollment, attributes
3. **Attendance & Timetable** - Daily tracking, scheduling
4. **Academics & Assessment** - Lesson plans, exams, grading
5. **Communication** - Announcements, chat, meetings
6. **Fees & Finance** - Billing, payments, reports
7. **Transport & Hostel** - GPS tracking, room allocation
8. **Library & Inventory** - Catalog, checkouts
9. **Staff Management** - Payroll, performance
10. **Reports & Dashboards** - Analytics, custom reports

## AI Features

- **Analytics & Predictions** - At-risk student detection, enrollment forecasting
- **Personalization** - Adaptive learning paths, smart recommendations
- **Automation** - AI quiz generation, auto-grading
- **NLP** - Multilingual chatbot, voice assistant
- **Document AI** - OCR, receipt processing
- **Optimization** - Timetable optimization, route planning

## Getting Started

### Frontend
```bash
cd frontend
npm install
npm run dev
```

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
uvicorn main:app --reload
```

### AI Services
```bash
cd ai-services
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8001
```

## License

MIT
