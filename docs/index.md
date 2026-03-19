# MCPRegistry Documentation

MCPRegistry is a web-based tool for registering, managing, and exploring **Model Context Protocol (MCP)** servers. It provides a Streamlit UI to connect to MCP servers, browse their available tools, and persist server configurations.

## Contents

- [Getting Started](getting-started.md) — Installation, setup, and running the app
- [User Guide](user-guide.md) — How to use the UI to connect and manage servers
- [Architecture](architecture.md) — Code structure and component overview
- [MCP Server Configuration](mcp-server-configuration.md) — Server config schema and examples
- [Example Files](example-files.md) — Reference for the bundled demo server and client

## What is MCP?

The [Model Context Protocol (MCP)](https://modelcontextprotocol.io) is an open protocol that allows AI models to interact with external tools and resources through a standardized interface. MCP servers expose **tools** (callable functions) and **resources** (data endpoints) that AI clients can discover and use.

MCPRegistry helps you:
- Connect to any MCP server over HTTP or stdio
- Inspect what tools a server exposes
- Save and manage multiple server configurations
- Export tool definitions as JSON
