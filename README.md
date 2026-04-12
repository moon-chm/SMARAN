# 🧠 SMARAN

> Meaningful memory care through emotionally intelligent AI

## The Problem
Dementia and Alzheimer's disease progressively rob individuals of their memories, independence, and identity. Caregivers face overwhelming emotional and physical burdens while trying to piece together fragmented recollections to provide optimal care. The current tools are often impersonal, clinical, or overly technical for elderly patients to utilize effectively.

## The Solution
SMARAN ("remembrance" in Sanskrit) is an AI-powered memory assistant that builds a personal, accessible knowledge graph of an elder's life. 

By engaging elderly users through a friendly chat interface (complete with voice interactions and emotional awareness), SMARAN gently stores core memories, routines, medical needs, and preferences. For caregivers, SMARAN provides a clinical intelligence dashboard mapping out these nodes in real-time, proactively alerting them to physical or emotional changes and enabling them to track the elder's wellbeing comprehensively.

---

## 🏗️ Architecture

```text
                     +-------------------+
  (Voice/Text) <---> |  Elder Dashboard  |
                     +-------------------+
                              ^
                              | (HTTPS / REST)
                              v
                     +-------------------+       +--------------------+
  Caregiver UI <---> |    FastAPI App    |<=====>|   Groq LLM Engine  |
                     +-------------------+       +--------------------+
                              |
       +----------------------+-----------------------+
       |                      |                       |
       v                      v                       v
+-------------+        +-------------+         +-------------+
|    spaCy    |        |   FAISS     |         | Neo4j Graph |
| (NLP/NER)   |        | (Vec Store) |         |  (Aura DB)  |
+-------------+        +-------------+         +-------------+
```

## 🛠️ Stack
| Component | Technology | Role |
| :--- | :--- | :--- |
| **Frontend** | Streamlit | Rapid, stateful, and customizable UIs |
| **Backend** | FastAPI (Python 3.10) | Async REST API orchestration |
| **Database** | Neo4j / Cypher | Knowledge graph persistence & modeling |
| **Vector DB** | FAISS | Semantic similarity and fast retrieval |
| **LLM** | Groq | Ultra-fast inference for conversational AI |
| **NLP** | spaCy | Offline Named Entity Recognition (NER) |
| **Voice** | ElevenLabs | Realistic TTS & Voice Cloning |

## ✨ Features
### 👨‍⚕️ Caregiver Portal
- **Role-based Authentication**: Secure access strictly scoped to the dashboard capabilities.
- **Clinical Graph View**: Complete mapping of appointments, medicines, symptoms, and emotional memories.
- **Memory Ingestion Engine**: Accepts natural text inputs, parses intent, and automatically creates connected nodes in the neo4j space.
- **Conflict Detection**: Alerts caregivers when new ingested memories contradict highly-reinforced existing data.
- **Visual Mindmap**: Interactive pyvis-rendered knowledge maps of the elder's psyche.

### 🧓 Elder Companion
- **Accessible Design**: High contrast, huge fonts, and drastically simplified interactions.
- **Emotionally Reactive Conversation**: Dynamically tracks and responds to mood (Happy, Sad, Anxious, etc).
- **Voice Capabilities**: Reads replies aloud with hyper-realistic voices (including cloned voices of loved ones).
- **Proactive Interventions**: Senses anxiety or sadness and fires clinical alerts to the caregiver automatically.
- **One-Touch Emergency**: Immediately escalates urgent needs into the ecosystem.

---

## 🚀 Setup & Execution

1. **Clone the repository**
   ```bash
   git clone https://github.com/organization/smaran.git
   cd smaran
   ```

2. **Configure Environment**
   ```bash
   cp .env.example .env
   # Edit .env with your Neo4j, Groq, and ElevenLabs credentials.
   ```

3. **Run with Docker Compose**
   ```bash
   docker-compose up --build
   ```

## 🔑 Demo Credentials
If you've run the seeder script, use the following to explore the portals:
- **Caregiver Login**: `caregiver_demo` / `Demo@1234` (Access `http://localhost:8501`)
- **Elder Login**: `elder_123` / `Demo@1234` (Access `http://localhost:8502`)

## 📚 API Documentation
Once running, interactive API docs are auto-generated:
- Swagger: `http://localhost:8000/docs`

