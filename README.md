# AI Dev Federation Dashboard ⚡

The **AI Dev Federation Dashboard** is a full end-to-end system demonstrating a **multi-agent orchestration layer** for AI-assisted development. It mirrors a software org with agents - **General Manager (CIAN), Architects, Security, and DevBot (engineer)** - working together to plan, validate, and execute.

This repo includes both the **frontend dashboard** (React + Tailwind) and the **backend services** (FastAPI + GitHub integrations + LLM) that power live demos and execution flows.

---

## 🌐 Live Demo

* **Production URL:** [https://aidevfederationdashboard.netlify.app/](https://aidevfederationdashboard.netlify.app/)
* **Repo Owner:** [Alex Seisler](https://github.com/AlexSeisler)

---

## ✨ Features

* 🧠 **CIAN (GM Agent)** → Strategic anchor, validates inputs, routes execution.
* 🏗️ **System Architect** → Generates DAGs, decomposes tasks, ensures security-first milestones.
* 🔐 **Security Architect** → Plans integration of security marked tasks
* 🤖 **DevBot** → Execution layer, performs repo file changes + patch lifecycle.
* 👥 **Trifecta Community** → Connected builder community showing adoption + execution.

---

## 📊 Capabilities

🚀 Demonstrates a **company-in-a-box model** - strategy → planning → security → execution → production.
💻 Enables **live repo navigation + patch application** via DevBot.
🌐 Connects with a growing builder community (AI Dev: Trifecta).
📂 Structured as a full solution for showcasing integrated AI development.

---

## 🛠 Tech Stack

**Frontend**

* React 19 + Vite 6.3
* Tailwind CSS + Framer Motion
* shadcn/ui components + Lucide icons

**Backend**

* FastAPI (Python)
* Hugging Face Router API → completions
* GitHub REST API → repo tree, file content, patching
* SQLAlchemy + SQLite → persistence (users, tasks, logs, memory)

---

## 📂 Repository Structure

```text
AI-Dev-Federation-Dashboard/
├── public/                     # Static assets (logos, banners, screenshots)
├── src/                        # React frontend
│   ├── components/             # UI components (views, widgets)
│   └── App.tsx                 # App entrypoint + routing
│
├── server/                     # FastAPI backend
│   ├── main.py                 # FastAPI app + middleware
│   ├── tasks.py                # In-memory task runner + Hugging Face integration
│   ├── hf_client.py            # Hugging Face API wrapper
│   ├── github_service.py       # GitHub API service + routes
│   ├── models.py               # SQLAlchemy ORM models
│   └── security.py             # Middleware (allowlist, rate limiting, audit)
│
├── docs/                       # Documentation (architecture, integrations, security)
├── package.json
├── requirements.txt
└── README.md
```

---

## 📖 Additional Documentation

* [ARCHITECTURE.md](./ARCHITECTURE.md) → Agent roles + orchestration design
* [INTEGRATIONS.md](./INTEGRATIONS.md) → Hugging Face, GitHub API, memory DB
* [SECURITY.md](./SECURITY.md) → Middleware, rate limiting, audit log

📌 Connected Layer: **AI Dev: Trifecta Community** → builders leveraging the Federation system.

---

📄 License
MIT — Open for educational and portfolio use.