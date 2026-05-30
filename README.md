<div align="center">

# Taiga MCP Server

**A production-ready [Model Context Protocol](https://modelcontextprotocol.io) server that connects AI assistants to [Taiga](https://taiga.io) project management.**

Manage projects, sprints, user stories, tasks, and issues in Taiga directly from Claude, Claude Code, or any MCP-compatible client — through natural language.

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![FastMCP](https://img.shields.io/badge/Built%20with-FastMCP-6E40C9)](https://github.com/jlowin/fastmcp)
[![Protocol](https://img.shields.io/badge/MCP-Streamable%20HTTP-00A98F)](https://modelcontextprotocol.io)
[![Taiga API](https://img.shields.io/badge/Taiga-REST%20API%20v1-83BD1E?logo=taiga&logoColor=white)](https://docs.taiga.io/api.html)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](#-license)

</div>

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Architecture](#-architecture)
- [Prerequisites](#-prerequisites)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Running the Server](#-running-the-server)
- [Running with Docker](#-running-with-docker)
- [Connecting an MCP Client](#-connecting-an-mcp-client)
- [Available Tools](#-available-tools)
- [Usage Examples](#-usage-examples)
- [Project Structure](#-project-structure)
- [Extending the Server](#-extending-the-server)
- [Troubleshooting](#-troubleshooting)
- [Security](#-security)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🔎 Overview

The **Taiga MCP Server** exposes the [Taiga](https://taiga.io) agile project management platform as a set of structured tools that Large Language Models can call autonomously. Built on [FastMCP](https://github.com/jlowin/fastmcp), it lets an AI agent read and write to your Taiga workspace — creating sprints, drafting user stories, triaging issues, leaving comments, and querying project metadata — without leaving the chat.

It speaks the **Streamable HTTP** MCP transport and authenticates against the **Taiga REST API v1** using either a username/password pair or a pre-issued auth token.

> **Use case:** Ask Claude *"Create a sprint for next week, add three user stories for the login feature, and assign them to the current sprint"* — and have it executed in Taiga.

---

## ✨ Features

- **🗂️ Full project lifecycle** — list, inspect, and create projects (by ID or slug).
- **🏃 Sprint management** — create and query milestones (sprints) with start/finish dates.
- **📝 User stories** — create, read, list, and update stories with status and milestone assignment.
- **✅ Tasks** — break stories down into tasks, reassign, and move through workflow statuses.
- **🐞 Issue tracking** — file, fetch, list, and update issues with priority, severity, and type.
- **💬 Comments & history** — add comments to any resource and pull full activity timelines.
- **🔍 Full-text search** — search across stories, tasks, issues, and wiki pages in a project.
- **🏷️ Workflow metadata** — enumerate statuses, priorities, and project members on demand.
- **🔐 Flexible auth** — token-based or credential-based authentication via environment variables.
- **🧩 Clean, extensible design** — a thin REST client plus a tool registry, easy to grow.

---

## 🏛️ Architecture

```
┌──────────────────┐     MCP / Streamable HTTP      ┌───────────────────────┐
│   MCP Client      │  ───────────────────────────► │   Taiga MCP Server     │
│ (Claude, Claude   │   http://127.0.0.1:8000/mcp   │      (Server.py)       │
│  Code, IDE, …)    │  ◄─────────────────────────── │   FastMCP + tools      │
└──────────────────┘         tool results           └───────────┬───────────┘
                                                                  │ REST API v1
                                                                  │ (Bearer token)
                                                                  ▼
                                                       ┌───────────────────────┐
                                                       │     Taiga Instance     │
                                                       │  (taiga.io / self-host)│
                                                       └───────────────────────┘
```

| Layer | Responsibility |
|-------|----------------|
| **`Server.py`** | Bootstraps FastMCP, builds the Taiga client from env config, registers tools, runs the HTTP transport. |
| **`Functions/Taiga/client.py`** | `TaigaClient` — a typed wrapper over the Taiga REST API v1 (auth, projects, sprints, stories, tasks, issues, wiki, search, webhooks). |
| **`Functions/Taiga/tools.py`** | `register_tools()` — maps client methods to `@mcp.tool()` definitions exposed to the LLM. |

---

## 📦 Prerequisites

- **Python 3.10+**
- A reachable **Taiga instance** — either [taiga.io](https://taiga.io) cloud or a self-hosted deployment.
- Valid **Taiga credentials** (username + password) or an **auth token**.
- An **MCP-compatible client** (e.g. Claude Code, Claude Desktop, or any IDE with MCP support).

---

## 🚀 Installation

### Option A — Batch script (Windows)

```bat
InstallRequirments.bat
```

This creates a virtual environment in `.venv` and installs all dependencies.

### Option B — Manual

```bat
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

> On macOS/Linux, activate with `source .venv/bin/activate`.

**Dependencies** (`requirements.txt`):

| Package | Purpose |
|---------|---------|
| `mcp` | FastMCP server framework & MCP protocol |
| `requests` | HTTP client for the Taiga REST API |
| `python-dotenv` | Loads configuration from `.env` |

---

## ⚙️ Configuration

The server is configured entirely through environment variables, loaded from a `.env` file in the project root. Copy the example and fill in your values:

```bat
copy .env.example .env
```

```ini
# Base URL of your Taiga instance (no trailing /api/v1 — it's added automatically)
TAIGA_BASE_URL=https://taiga.maskai.pro

# --- Option 1: username / password authentication ---
TAIGA_USERNAME=you@example.com
TAIGA_PASSWORD=your-password

# --- Option 2: token authentication (takes precedence if set) ---
# TAIGA_TOKEN=your-auth-token
```

### Authentication precedence

| Variable(s) set | Behavior |
|-----------------|----------|
| `TAIGA_TOKEN` | Used directly as a Bearer token. |
| `TAIGA_USERNAME` + `TAIGA_PASSWORD` | The server logs in and stores the returned token. |
| Neither | Startup fails with a clear error in stderr. |

> ⚠️ `TAIGA_BASE_URL` is **required**. Never commit your real `.env` — it is already covered by `.gitignore`.

---

## ▶️ Running the Server

```bat
.venv\Scripts\activate
python Server.py
```

On success the server listens on:

```
http://127.0.0.1:8000/mcp
```

If the Taiga client fails to initialize (bad credentials, unreachable host), the error is printed to **stderr** and the process keeps running so the failure is visible to the client.

| Setting | Default | Override |
|---------|---------|----------|
| Host | `127.0.0.1` | `MCP_HOST` env var |
| Port | `8000` | `MCP_PORT` env var |
| Path | `/mcp` | `Server.py` |
| Transport | `streamable-http` | `Server.py` |

> The host/port are read from the `MCP_HOST` / `MCP_PORT` environment variables, falling back to the defaults above. The Docker image sets `MCP_HOST=0.0.0.0` so the port is reachable from the host.

---

## 🐳 Running with Docker

The repository ships with a `Dockerfile` and `docker-compose.yml` for containerized deployment. The image runs as a non-root user and binds to `0.0.0.0` inside the container.

### Using Docker Compose (recommended)

Make sure your `.env` file is populated (see [Configuration](#-configuration)), then:

```bash
docker compose up -d --build
```

The server is published on `http://127.0.0.1:8000/mcp`. View logs and stop with:

```bash
docker compose logs -f
docker compose down
```

### Using the Docker CLI

```bash
# Build the image
docker build -t taiga-mcp-server .

# Run it, passing configuration from your .env file
docker run -d --name taiga-mcp-server \
  --env-file .env \
  -p 8000:8000 \
  taiga-mcp-server
```

> The container reads the same environment variables as the local setup — `TAIGA_BASE_URL`, plus either `TAIGA_TOKEN` or `TAIGA_USERNAME`/`TAIGA_PASSWORD`. `MCP_HOST`/`MCP_PORT` are preset for container networking.

---

## 🔌 Connecting an MCP Client

### Claude Code

Register the running server over HTTP:

```bash
claude mcp add --transport http taiga http://127.0.0.1:8000/mcp
```

### Generic MCP client config

```json
{
  "mcpServers": {
    "taiga": {
      "type": "http",
      "url": "http://127.0.0.1:8000/mcp"
    }
  }
}
```

Once connected, the client will discover all `taiga_*` tools automatically.

---

## 🧰 Available Tools

The server registers **25 tools**, all prefixed `taiga_`.

### Account

| Tool | Description |
|------|-------------|
| `taiga_get_me` | Return the authenticated user's profile. |

### Projects

| Tool | Description |
|------|-------------|
| `taiga_list_projects` | List projects, optionally filtered by member ID. |
| `taiga_get_project` | Get full project details by ID. |
| `taiga_get_project_by_slug` | Get a project by its URL slug. |
| `taiga_create_project` | Create a new project. |

### Milestones (Sprints)

| Tool | Description |
|------|-------------|
| `taiga_list_milestones` | List sprints, optionally filtering by open/closed. |
| `taiga_get_milestone` | Get a single sprint by ID. |
| `taiga_create_milestone` | Create a sprint (`YYYY-MM-DD` dates). |

### User Stories

| Tool | Description |
|------|-------------|
| `taiga_list_userstories` | List stories, filterable by milestone or status. |
| `taiga_get_userstory` | Get a single story by ID. |
| `taiga_create_userstory` | Create a story with optional milestone/status. |
| `taiga_update_userstory` | Update a story (requires its `version`). |

### Tasks

| Tool | Description |
|------|-------------|
| `taiga_list_tasks` | List tasks, filterable by milestone or story. |
| `taiga_get_task` | Get a single task by ID. |
| `taiga_create_task` | Create a task under a project/story/sprint. |
| `taiga_update_task` | Update a task (requires its `version`). |

### Issues

| Tool | Description |
|------|-------------|
| `taiga_list_issues` | List issues, filterable by status or priority. |
| `taiga_get_issue` | Get a single issue by ID. |
| `taiga_create_issue` | Create an issue with priority/severity/type. |
| `taiga_update_issue` | Update an issue (requires its `version`). |

### Comments, History & Search

| Tool | Description |
|------|-------------|
| `taiga_add_comment` | Comment on a story/task/issue/epic/wiki. |
| `taiga_get_history` | Get the activity & comment history for a resource. |
| `taiga_search` | Full-text search across a project. |

### Metadata

| Tool | Description |
|------|-------------|
| `taiga_list_userstory_statuses` | List user story statuses for a project. |
| `taiga_list_task_statuses` | List task statuses for a project. |
| `taiga_list_issue_statuses` | List issue statuses for a project. |
| `taiga_list_priorities` | List issue priorities for a project. |
| `taiga_list_members` | List project members. |

> 💡 **About `version`:** Taiga uses optimistic concurrency. Update tools require the resource's current `version` (obtained from the matching `get`/`list` tool) to prevent lost updates.

---

## 💬 Usage Examples

Once the server is connected, drive it in natural language:

> **"List all my Taiga projects and show me the open sprints for the one called 'Mobile App'."**

> **"Create a user story 'As a user, I can reset my password' in project 42, and put it in the current sprint."**

> **"File a high-priority issue about the broken checkout flow in project 42, then add a comment with the reproduction steps."**

> **"Search project 42 for anything related to 'authentication' and summarize the open items."**

The assistant chains the relevant tools — e.g. `taiga_get_project_by_slug` → `taiga_list_milestones` → `taiga_create_userstory` — and reports back.

---

## 🗂️ Project Structure

```
MyMcp/
├── Server.py                  # Entry point — FastMCP setup, client wiring, run()
├── Functions/
│   ├── __init__.py
│   └── Taiga/
│       ├── __init__.py
│       ├── client.py          # TaigaClient — REST API v1 wrapper
│       └── tools.py           # register_tools() — MCP tool definitions
├── requirements.txt           # Python dependencies
├── Dockerfile                 # Container image definition
├── docker-compose.yml         # One-command containerized run
├── .dockerignore              # Build context exclusions
├── .env.example               # Configuration template
├── InstallRequirments.bat     # Create venv + install deps (Windows)
├── LauncheServer.bat          # Activate the venv (Windows)
├── CLAUDE.md                  # Guidance for Claude Code in this repo
└── README.md
```

---

## 🧩 Extending the Server

The `TaigaClient` already implements many endpoints not yet exposed as tools — **epics**, **wiki pages**, **memberships**, **roles**, **webhooks**, **bulk creation**, **severities**, **points**, and more. To surface any of them:

1. Add a method to `Functions/Taiga/client.py` (if not already present).
2. Wrap it in `Functions/Taiga/tools.py` inside `register_tools()`:

```python
@mcp.tool()
def taiga_list_epics(project_id: int) -> list:
    """List epics in a project."""
    return client.list_epics(project_id)
```

3. Restart the server — the tool is discovered automatically.

> The docstring becomes the tool description shown to the LLM, so write it clearly and describe each parameter.

---

## 🛠️ Troubleshooting

| Symptom | Likely cause & fix |
|---------|--------------------|
| `Taiga client init failed: TAIGA_BASE_URL is not set` | Create a `.env` with `TAIGA_BASE_URL`. |
| `Set either TAIGA_TOKEN or both TAIGA_USERNAME and TAIGA_PASSWORD` | Provide credentials or a token in `.env`. |
| `[401] Not authenticated` | Token expired/invalid, or wrong username/password. |
| `[404] ...` on a tool call | Wrong `project_id`/resource ID — verify with a `list`/`get` tool first. |
| Update fails with a version error | Re-fetch the resource and pass its current `version`. |
| Client can't connect | Confirm the server is running and the URL is `http://127.0.0.1:8000/mcp`. |

---

## 🔐 Security

- **Secrets stay local.** Credentials live only in `.env`, which is git-ignored. Never commit real tokens or passwords.
- **Prefer tokens over passwords** where possible, and rotate them periodically.
- **Bind to localhost.** The server listens on `127.0.0.1` by default. Do not expose it publicly without an authenticating reverse proxy and TLS.
- **Least privilege.** Use a Taiga account scoped to only the projects the agent needs.

---

## 🤝 Contributing

Contributions are welcome:

1. Fork the repository and create a feature branch.
2. Add or extend tools following the patterns in `Functions/Taiga/`.
3. Keep docstrings descriptive — they are the agent-facing API.
4. Open a pull request with a clear summary of the change.

---

## 📄 License

Released under the **MIT License**. See [`LICENSE`](LICENSE) for details.

---

<div align="center">

Built with ❤️ on [FastMCP](https://github.com/jlowin/fastmcp) · Powered by the [Taiga REST API](https://docs.taiga.io/api.html)

</div>
