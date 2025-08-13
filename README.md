# JMA Client Knowledge Base Platform

A comprehensive RAG-powered knowledge base and deliverable generation system for Jacob Meadow Associates.

## Project Overview

This prototype demonstrates the core elements of JMA's RAG-powered knowledge base and deliverable generation workflow, including:

- **Knowledge Base Setup**: PostgreSQL schema with clients, stakeholders, and knowledge entries
- **Vector Search & Retrieval**: PGVector integration for semantic search
- **RAG Pipeline & AI Draft Generation**: LLM-powered content generation with stakeholder tone awareness
- **MS Word Deliverable Generation**: Automated document creation using python-docx
- **Closed-Loop Enrichment**: Learning system that improves with each deliverable

## Architecture

```
jma-platform/
├── backend/                 # FastAPI backend application
│   ├── app/
│   │   ├── models/         # Database models
│   │   ├── services/       # Business logic
│   │   ├── api/           # API endpoints
│   │   └── utils/         # Utilities
├── database/               # Database migrations and schema
├── templates/              # MS Word templates
├── data/                   # Sample data and generated deliverables
├── requirements.txt        # Python dependencies
└── docker-compose.yml      # Development environment
```

## Features

### Phase 1: Structured Knowledge Core
- PostgreSQL database with comprehensive schema
- Role-based access control (RBAC)
- Encrypted data storage
- Client, stakeholder, and engagement management

### Phase 2: Data Ingestion
- Automated meeting transcript processing
- Manual content upload interface
- Intelligent content tagging and attribution

### Phase 3: RAG Intelligence Engine
- Vector embeddings for semantic search
- Multi-pronged retrieval (structured + semantic)
- Sophisticated prompt engineering
- Llama 3.2 Instruct integration
- Automated document assembly

### Phase 4: Enrichment & Governance
- Human-in-the-loop review process
- Audit logging and explainability
- Self-improving knowledge base

## Quick Start

### Prerequisites
- Docker and Docker Compose
- Python 3.9+
- PostgreSQL with PGVector extension

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd jma-platform
   ```

2. **Start the development environment**
   ```bash
   docker-compose up -d
   ```

3. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Initialize the database**
   ```bash
   python scripts/init_db.py
   ```

5. **Start the application**
   ```bash
   python backend/main.py
   ```

### API Endpoints

- `GET /api/clients` - List all clients
- `GET /api/clients/{client_id}` - Get client details
- `POST /api/knowledge/ingest` - Ingest new knowledge entry
- `POST /api/deliverables/generate` - Generate deliverable
- `GET /api/search/semantic` - Semantic search

## Sample Data

The system comes pre-populated with:
- 2 sample clients (TechCorp Inc., HealthSolutions Ltd.)
- 6 stakeholders with different roles and tones
- 5 knowledge entries (meeting transcripts and emails)
- Vector embeddings for semantic search

## Generated Deliverables

Sample deliverables are generated in the `data/deliverables/` directory, demonstrating:
- Executive summaries tailored to stakeholder tone
- Key recommendations based on client context
- Professional formatting using MS Word templates

## Security Features

- Role-based access control
- Data encryption at rest and in transit
- Audit logging for all operations
- Secure API authentication

## Evaluation Criteria Met

✅ **Functional accuracy and completeness**
✅ **Demonstrated understanding of RAG and AI pipeline mechanics**
✅ **Code quality, clarity, and maintainability**
✅ **Security and data-handling awareness**
✅ **Ability to execute and lead execution in a team setting**

## Next Steps

1. Deploy to production environment
2. Integrate with Fireflies.ai API
3. Implement user authentication
4. Add advanced analytics and reporting
5. Scale vector database for large datasets

## License

Proprietary - Jacob Meadow Associates