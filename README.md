# SMARAN

Graph-Based Emotionally Intelligent Memory System for Elder Care.

## Phase 1 setup

### Prerequisites
- Python 3.10+
- AuraDB Neo4j Instance

### Setup Instructions
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Set up environment:
   ```bash
   cp .env.example .env
   # Edit .env with your AuraDB credentials, GROQ API Key, etc.
   ```

### Running the App
Start the app using Uvicorn:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Alternatively, single-command startup script (to be created) or docker-compose:
```bash
docker-compose up --build -d
```
"# SMARAN" 
