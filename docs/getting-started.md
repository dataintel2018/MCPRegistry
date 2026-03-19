# Getting Started

## Prerequisites

- Python 3.10+
- [uv](https://github.com/astral-sh/uv) (recommended for running scripts)
- Git

## Installation

### 1. Clone the repository

```bash
git clone <repo-url>
cd MCPRegistry
```

### 2. Set up a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
pip install streamlit
```

`requirements.txt` includes:
- `mcp` — Model Context Protocol SDK
- `rich` — Terminal output formatting
- `requests` — HTTP client

### 4. Run the application

```bash
streamlit run MCPRegistry.py
```

The app opens at `http://localhost:8501` in your browser.

## Dev Container (VS Code)

If you use VS Code with the Dev Containers extension, the repository includes a `.devcontainer/devcontainer.json` that:
- Uses a Python 3.10 base image
- Installs all dependencies automatically
- Forwards port 8501
- Starts the app on container attach

Open the repo in VS Code and select **"Reopen in Container"** to use it.

The dev container starts the app with CORS and XSRF protection disabled for local development:

```bash
streamlit run MCPRegistry.py --server.enableCORS false --server.enableXsrfProtection false
```

## Quick Test

To verify everything works, start the bundled demo MCP server in one terminal:

```bash
uv run OneMCPServer.py
```

Then launch MCPRegistry, select the **stdio** protocol, choose the **Demo** server from the saved servers dropdown, and click **Connect to stdio Server**.
