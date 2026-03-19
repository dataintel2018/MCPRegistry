# Architecture

## File Overview

```
MCPRegistry/
├── MCPRegistry.py         # Main Streamlit application
├── OneMCPServer.py        # Demo MCP server
├── OneMCPClient.py        # Demo MCP client (reference)
├── mcp_servers.json       # Persisted server configurations
├── requirements.txt       # Python dependencies
└── .devcontainer/
    └── devcontainer.json  # VS Code Dev Container config
```

## MCPRegistry.py

The main application. Organized into three sections:

### Persistence helpers

**`load_saved_servers() -> Dict`** (`MCPRegistry.py:15`)
Reads `mcp_servers.json` from the working directory. Returns an empty dict if the file does not exist or cannot be parsed.

**`save_servers(servers) -> bool`** (`MCPRegistry.py:26`)
Writes the given dict to `mcp_servers.json` with 2-space indentation. Returns `True` on success.

### MCPClient class (`MCPRegistry.py:36`)

Handles communication with MCP servers over both supported protocols.

**Constructor** — `__init__(server_url, command, program, protocol)`

| Parameter | Used by | Description |
|-----------|---------|-------------|
| `server_url` | HTTP | Base URL of the server |
| `command` | stdio | Executable to launch (e.g. `uv`) |
| `program` | stdio | Arguments list (e.g. `["run", "OneMCPServer.py"]`) |
| `protocol` | both | `"http"` or `"stdio"` |

For stdio, the constructor hardcodes `StdioServerParameters` to launch `uv run OneMCPServer.py`. (See known limitations below.)

**`get_server_info() -> Dict`** (`MCPRegistry.py:100`)
- HTTP: `GET /server_info` on the server URL.
- stdio: Returns a static `{"action": "server_info"}` placeholder.

**`connect_to_server(server_script_path) -> Dict`** (`MCPRegistry.py:70`) *(async)*
Connects via stdio transport to a `.py` or `.js` script. Initializes the MCP session and returns server info. This method is currently unused by the UI; `list_tools` handles connection for stdio.

**`list_tools() -> List`** (`MCPRegistry.py:113`) *(async for stdio)*
- HTTP: `GET /list_tools`, returns the `"tools"` array from the JSON response.
- stdio: Opens a fresh stdio transport, initializes a `ClientSession`, and calls `session.list_tools()`.

### Streamlit UI — `main()` (`MCPRegistry.py:132`)

The app is structured around two `st.tabs`:

**Tab 1 — Connect to Server**
- Protocol radio button selects HTTP or stdio branch.
- HTTP branch: URL text input + saved server dropdown → connect button → display server info + tools.
- stdio branch: saved server dropdown (no manual input) → connect button → `asyncio.run(list_tools())` → display tools.

**Tab 2 — Manage Servers**
- Lists all entries in `st.session_state.saved_servers` with a per-row Delete button.
- Form to add a new HTTP or stdio server that writes to `mcp_servers.json`.

### Session state

| Key | Type | Purpose |
|-----|------|---------|
| `client` | `MCPClient \| None` | Active client instance |
| `saved_servers` | `Dict` | In-memory mirror of `mcp_servers.json` |

### Exit handler (`MCPRegistry.py:375`)

`on_exit()` is registered with `atexit` to call `client.cleanup()` when the app process exits.

## Known Limitations

- The stdio `MCPClient.__init__` ignores the `command` and `program` arguments and hardcodes `uv run OneMCPServer.py`. Any stdio server added via the UI uses these same hardcoded parameters.
- The `connect_to_server` method (which accepts a script path) is not invoked by the UI.
- HTTP `list_tools` is not async, but stdio `list_tools` is; the UI calls them differently.
- Server info for stdio always returns `{"action": "server_info"}` rather than real server metadata.
