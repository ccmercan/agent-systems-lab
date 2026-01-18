
# Agent Systems Lab

This repository contains a hands-on implementation of a **tool-using LLM agent system** inspired by **Model Context Protocol (MCP)** concepts.
The project focuses on **agent architecture, tool use, authentication, robustness, and validation**, built step by step.

The implementation intentionally avoids high-level frameworks in order to expose the **core mechanics of agent systems**.

---

## Overview

The system consists of two main components:

1. **MCP-style Tool Server (FastAPI)**

   * Exposes tools over HTTP
   * Handles authentication, validation, and execution
2. **LLM-driven Agent (Client)**

   * Discovers tools
   * Chooses which tool to use
   * Calls tools through a secure interface
   * Handles failures via reflexion and retries

The agent **does not execute code directly**.
Instead, it **proposes actions**, which are executed safely by the server.

---

## Project Structure

```
agent-systems-lab/
├── mcp_toys/
│   ├── http_server/
│   │   ├── server.py        # MCP-style tool server
│   │   └── __init__.py
│   ├── agent/
│   │   ├── agent.py         # LLM-driven agent client
│   │   └── __init__.py
├── pyproject.toml           # Poetry project configuration
├── poetry.lock
└── README.md
```

---

## Prerequisites

* Python **3.11+**
* Poetry
* Ollama (local LLM runtime)

### Install dependencies

```bash
poetry install
```

---

## Practice Breakdown (1–6)

### Practice 1 — MCP Tool Server

Implemented a FastAPI server that exposes tools using an MCP-like interface.

Endpoints:

* `GET /tools` → Tool discovery
* `POST /call` → Tool execution

Tools are registered with:

* name
* description
* input schema
* handler function

---

### Practice 2 — Authentication

Added API key authentication to protect tool execution.

* Tool discovery is public
* Tool execution requires `X-API-Key`

This enforces a **capability boundary** between the agent and tools.

---

### Practice 3 — LLM as an Agent

Implemented an agent that:

1. Fetches available tools
2. Uses an LLM to decide which tool to call
3. Executes the tool via HTTP
4. Returns the result

The LLM **does not run tools directly**.

---

### Practice 4 — Reflexion & Retries

Added robustness to the agent:

* Detects tool failures
* Feeds errors back to the LLM
* Retries with corrected tool calls
* Uses bounded retries to avoid infinite loops

This enables **self-correcting behavior**.

---

### Practice 5 — Multiple Tools & Disambiguation

Extended the server with multiple tools:

* `add_numbers`
* `subtract_numbers`
* `multiply_numbers`

The agent learns to:

* Choose the correct tool based on user intent
* Map natural language to correct arguments
* Recover from incorrect initial choices

---

### Practice 6 — Input Validation & Schema Enforcement

Strengthened safety at the server boundary by enforcing:

* Required arguments
* Argument types
* No extra arguments

Important design decision:

* **JSON-safe schemas** are exposed to the agent
* **Python types** are used internally for validation

This mirrors real MCP-style separation between protocol and runtime.

---

## Running the System

### 1. Start the MCP Tool Server

From the repository root:

```bash
poetry run uvicorn mcp_toys.http_server.server:app --reload
```

Server runs at:

```
http://127.0.0.1:8000
```

Swagger UI:

```
http://127.0.0.1:8000/docs
```

---

### 2. Run the Agent

In a separate terminal:

```bash
poetry run python mcp_toys/agent/agent.py
```

Example output:

```text
User: Add 3 and 4
Agent result: {'result': 7}

User: Subtract 10 from 3
Agent result: {'result': -7}
```

---

## Key Design Principles

* **LLMs propose actions, they do not execute them**
* **All execution happens behind a permissioned boundary**
* **Validation happens at the tool layer**
* **Agents are orchestration systems, not function callers**
* **Robustness is mandatory, not optional**

---

## What This Project Demonstrates

* Core agent architecture
* MCP-style tool discovery and invocation
* Secure tool execution
* LLM-driven decision making
* Reflexion-based recovery
* Schema-based safety enforcement

This project intentionally avoids abstractions to make agent behavior **transparent and debuggable**.

---

## License

Educational / experimental use.
