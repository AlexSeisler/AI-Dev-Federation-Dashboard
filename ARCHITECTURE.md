# AI-Dev-Federation-Dashboard - System Architecture

## 🎯 Purpose

The **AI-Dev-Federation-Dashboard** was built as a **multi-agent orchestration platform** demonstrating how an engineering org can be mirrored in AI.  
It provides an **end-to-end execution layer** where agents collaborate to plan, validate, and implement code changes inside a real GitHub repository.

- **CIAN (General Manager)** → Validates input + routes execution  
- **System Architect** → Generates plans, DAGs, and task decomposition  
- **Security Architect** → Placeholder agent for security-first expansion  
- **DevBot** → Execution layer for file-level patching  
- **Community Layer (Trifecta)** → Real builders leveraging the Federation system  

---

## 🛠 Core Architecture Overview

The system is designed as a **full-stack application** with a **React frontend** and a **FastAPI backend**, connected to **GitHub** and **Hugging Face** APIs.

### 🔹 Frontend (React + Vite)
- React 19 + Vite 6.3  
- Tailwind CSS + Framer Motion  
- shadcn/ui components + Lucide icons  

**Views implemented for:**
- `/cian` → CIAN (strategic GM agent)  
- `/architect` → System Architect  
- `/security` → Security placeholder agent  
- `/devbot` → DevBot execution engine  
- `/community` → Trifecta community showcase  

---

### 🔹 Backend (FastAPI)
FastAPI provides orchestration logic, agent pipelines, and integrations:

- `main.py` → App entrypoint + middleware  
- `tasks.py` → Task runner, SSE streaming, Hugging Face integration  
- `hf_client.py` → Hugging Face Router completions (Llama-3.1 model)  
- `github_service.py` → Repo tree + file retrieval from GitHub  
- `security.py` → Middleware (endpoint allowlist, guest rate limiting, audit logging)  
- `models.py` → SQLAlchemy ORM (users, tasks, logs, memories)  

---

### 🔹 Data & Storage
- **SQLite + SQLAlchemy** → Users, tasks, audit logs, conversation memory  
- **GitHub API** → Live repo tree + file content for DevBot execution  
- **Hugging Face API** → AI reasoning and completion  
- **In-memory Queues** → Real-time log streaming (SSE)  

---

## 🔗 System Data Flow

```mermaid
flowchart TD

A[User Input] --> B[Frontend React Dashboard]
B --> C[FastAPI Backend]

C -->|Validation| D[CIAN Agent]
D -->|Planning| E[System Architect]
E -->|Decomposition| F[Task Queue]

F -->|Execution Task| G[DevBot Engine]
G -->|File Retrieval| H[GitHub API]
G -->|Reasoning| I[Hugging Face API]
G -->|Patch Proposal| J[GitHub PR Flow]

F -->|Security Tickets| K[Security Architect]

C -->|Community View| L[Trifecta Community Showcase]\
```

## 🧩 Subsystem Breakdown
```text
| Subsystem        | Implementation         | Purpose                                         |
|------------------|------------------------|-------------------------------------------------|
| frontend_ui      | React + Vite + Tailwind| Dashboard views for agents + community           |
| orchestration    | FastAPI                | Routes, SSE, middleware, task execution          |
| ai_completion    | Hugging Face API       | LLM completions for planning + file reviews      |
| repo_service     | GitHub REST API        | Repo tree, file content, patch flow              |
| database         | SQLite + SQLAlchemy    | Users, tasks, logs, memory persistence           |
| security         | Middleware + Audit Log | Endpoint allowlist + guest rate limiting         |
| community_layer  | Static Assets + Links  | Connects to AI Dev: Trifecta builder community   |
```

---

## ⚡ Architecture Strengths

- **End-to-end orchestration** → Strategy → Planning → Execution → Security  
- **Real-world integrations** → GitHub + Hugging Face + SQLAlchemy persistence  
- **Agent discipline** → Clear boundaries between roles (CIAN, Architect, DevBot, Security)  
- **Scalable design** → Extendable with new agents or external integrations  
- **Community layer** → Proof of adoption + real builders executing inside the system  