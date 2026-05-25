# A2A — Agent-to-Agent Protocol: Learning Project

A progressive hands-on exploration of the **Agent-to-Agent (A2A) protocol**, demonstrating how to build distributed AI agent systems where agents discover each other and delegate tasks dynamically.

The project is structured in three versions, each building on the previous to introduce more sophisticated patterns.

---

## What is A2A?

The A2A protocol is a standardized way for AI agents to:
- **Advertise themselves** via a discovery endpoint (`/.well-known/agent.json`)
- **Accept tasks** via a JSON-RPC 2.0 interface
- **Delegate work** to other agents by calling their task endpoints

This enables composing complex workflows from modular, independently-running agents.

---

## Repository Structure

```
A2A-Protocol/
├── simple_version/          # v1: Baseline Flask and FastAPI agent (no LLM)
├── version_2_adk_agent/     # v2: Single LLM agent using Google ADK
└── version_3_multi_agent/   # v3: Multi-agent orchestration with dynamic discovery
```

---

## Versions at a Glance

| Version | Description                                     | Key Concepts |
|---------|-------------------------------------------------|--------------|
| v1 | Simple Flask-based and FastAPI based time agent | A2A discovery, JSON-RPC basics |
| v2 | Single Gemini-powered agent                     | Google ADK, LLM integration, sessions |
| v3 | Multi-agent orchestration                       | Agent discovery, tool-calling router, delegation |

---

## Prerequisites

- Python 3.11 or higher (tested on 3.13.3)
- A [Google]API key (for Gemini LLM, required for v2 and v3)

---

## Setup

```bash
# Clone and enter the repo
git clone <repo-url>
cd A2A

# Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate   # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set your Google API key
export GOOGLE_API_KEY="your-api-key-here"
```





**What to observe:**
- ADK's `Runner` manages sessions and conversation memory across turns
- Time/date queries are handled without hitting the LLM
- All other queries are forwarded to Gemini


## A2A Protocol Reference

### Discovery endpoint

```
GET /.well-known/agent.json
```

Returns an `AgentCard` describing the agent's name, description, URL, and skills.

### Task endpoint

```
POST /
Content-Type: application/json

{
  "jsonrpc": "2.0",
  "id": "1",
  "method": "tasks/send",
  "params": {
    "id": "<task-id>",
    "sessionId": "<session-id>",
    "message": {
      "role": "user",
      "parts": [{ "text": "your query here" }]
    }
  }
}
```

---

## Key Technologies

| Technology                               | Role |
|------------------------------------------|------|
| [Google ADK](https://google.github.io/adk-docs/) | Agent framework (sessions, memory, tool-calling) |
| [Gemini](https://ai.google.dev/)         | LLM powering the agents |
| [Starlette](https://www.starlette.io/)   | Async ASGI web server |
| [Pydantic](https://docs.pydantic.dev/)   | Data validation for A2A protocol models |
| [httpx](https://www.python-httpx.org/)   | Async HTTP client for agent-to-agent calls |
| [asyncclick](https://github.com/click-contrib/asyncclick) | Async CLI framework |
| [Fast-API](https://fastapi.tiangolo.com/)| Baseline HTTP server (v1 only) |

---

## Learning Path

If you're new to A2A and multi-agent systems, work through the versions in order:

1. **v1** — Understand the raw A2A protocol (discovery + JSON-RPC task API)
2. **v2** — See how a real LLM agent plugs into the protocol via Google ADK
3. **v3** — Explore orchestration: dynamic discovery, tool-based routing, and agent composition


## Steps to run

**v1**
```bash
1. **Run Server**  uvicorn simple_version.server.tells_time_serve:app
2. **Run Client**  python -m simple_version.client.time_client
```

**v2**
```bash
1. **Run Server**  python -m version_2_adk_agent.agents.google_adk
2. **Run Client**  python -m version_2_adk_agent.app.cmd.cmd --agent http://localhost:10002 
```

**v3**
```bash
1. **Run Server1** python -m version_3_multi_agent.agents.explain_agent --host localhost --port 10000
2. **Run Server2** python -m version_3_multi_agent.agents.trip_planner --host localhost --port 10001
3. **Run Server3** python -m version_3_multi_agent.agents.host_agent.entry --host localhost --port 10002
4. **Run Client** python -m version_3_multi_agent.app.cmd.cmd --agent http://localhost:10002
```
