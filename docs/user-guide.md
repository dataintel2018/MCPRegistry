# User Guide

The MCPRegistry UI has two tabs: **Connect to Server** and **Manage Servers**.

## Tab 1: Connect to Server

### HTTP Protocol

1. Select **HTTP** from the Protocol radio buttons.
2. Either:
   - Type a server URL directly (default: `http://localhost:8000`), or
   - Pick a saved HTTP server from the **Select from saved HTTP servers** dropdown.
3. Click **Connect to HTTP Server**.

On success, the app displays:
- A **Server Information** section with the raw JSON response from the server's `/server_info` endpoint.
- An **Available Tools** section listing each tool in a collapsible expander.
- A **Download Tools as JSON** button to export all tool definitions.

### stdio Protocol

1. Select **stdio** from the Protocol radio buttons.
2. Pick a saved stdio server from the **Select from saved stdio servers** dropdown.
   - The **Demo** server (bundled) runs `uv run OneMCPServer.py`.
3. Click **Connect to stdio Server**.

On success, the app displays the same server info and tool listing as the HTTP flow. Each tool can be expanded to see its full schema. Tools can be exported as JSON.

> **Note:** stdio connections launch a subprocess. The connection is established fresh on each button click.

## Tab 2: Manage Servers

### Viewing Saved Servers

All persisted servers are listed with columns for:
- **Name** — the server's display name
- **Protocol** — `http` or `stdio`
- **Command / URL** — the connection command or URL
- **Program / URL** — the program arguments or URL (repeated for HTTP)

### Deleting a Server

Click the **Delete** button on any row to remove that server from `mcp_servers.json`.

### Adding a New Server

1. Select the protocol (**HTTP** or **stdio**).
2. Fill in the form:
   - **HTTP**: Server Name + Server URL
   - **stdio**: Server Name + Command + server_program (absolute path to the script)
3. Click **Add Server**.

The server is saved to `mcp_servers.json` and immediately appears in the list and the connect dropdowns.

## Downloading Tool Definitions

After connecting to any server, a **Download Tools as JSON** button appears below the tools list. Clicking it downloads a `mcp_tools.json` file containing all tool definitions including names, descriptions, and input schemas.
