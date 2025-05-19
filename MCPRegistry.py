import streamlit as st
import requests
import json
import os
import subprocess
import threading
import time
import tempfile
from typing import List, Dict, Optional, Any, Union, Tuple
from mcp import ClientSession, StdioServerParameters, types
import asyncio
from mcp.client.stdio import stdio_client
from contextlib import AsyncExitStack

def load_saved_servers() -> Dict[str, Dict[str, str]]:
    """Load saved MCP servers from a JSON file"""
    try:
        if os.path.exists("mcp_servers.json"):
            with open("mcp_servers.json", "r") as f:
                return json.load(f)
        return {}
    except Exception as e:
        st.error(f"Error loading saved servers: {str(e)}")
        return {}

def save_servers(servers: Dict[str, Dict[str, str]]) -> bool:
    """Save MCP servers to a JSON file"""
    try:
        with open("mcp_servers.json", "w") as f:
            json.dump(servers, f, indent=2)
        return True
    except Exception as e:
        st.error(f"Error saving servers: {str(e)}")
        return False

class MCPClient:
    """Client for interacting with Model Context Protocol servers"""
    
    def __init__(self, server_url: str = None, command: str = None, program: str = None, protocol: str = "http"):
        """Initialize the MCP client
        
        Args:
            server_url: The URL for HTTP protocol servers
            command: The command to execute for stdio protocol servers
            arguments: The arguments to be passed to the command
            protocol: Either "http" or "stdio"
        """
        self.protocol = protocol
        self.process = None
        self.stop_event = None
        self.session = None
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()        


        if protocol == "http":
            self.server_url = server_url.rstrip("/") if server_url else None
        elif protocol == "stdio":
            self.command = command
            #command = "python"
            self.server_params = StdioServerParameters(
                command="uv",
                args=["run", "OneMCPServer.py"],
                env=None
            )
            #self.server_params = None
        else:
            raise ValueError(f"Unsupported protocol: {protocol}")

    async def connect_to_server(self, server_script_path: str):
        """Connect to an MCP server

        Args:
            server_script_path: Path to the server script (.py or .js)
        """
        is_python = server_script_path.endswith('.py')
        is_js = server_script_path.endswith('.js')
        if not (is_python or is_js):
            raise ValueError("Server script must be a .py or .js file")

        command = "python" if is_python else "node"
        # self.server_params = StdioServerParameters(
        #     command=command,
        #     args=[server_script_path],
        #     env=None
        # )

        stdio_transport = await self.exit_stack.enter_async_context(stdio_client(self.server_params))
        self.stdio, self.write = stdio_transport
        self.session = await self.exit_stack.enter_async_context(ClientSession(self.stdio, self.write))

        await self.session.initialize()

        # List available tools
        response = await self.session.list_tools()
        tools = response.tools
        print("\nConnected to server with tools:", [tool.name for tool in tools])
        return self.get_server_info()

    def get_server_info(self) -> Dict[str, Any]:
        """Get information about the MCP server"""
        if self.protocol == "http":
            try:
                response = requests.get(f"{self.server_url}/server_info")
                response.raise_for_status()
                return response.json()
            except requests.RequestException as e:
                st.error(f"Error getting server info: {str(e)}")
                return {}
        elif self.protocol == "stdio":
            return {"action": "server_info"}
    
    async def list_tools(self) -> List[Dict[str, Any]]:
        """List all tools available on the MCP server"""
        if self.protocol == "http":
            try:
                response = requests.get(f"{self.server_url}/list_tools")
                response.raise_for_status()
                return response.json().get("tools", [])
            except requests.RequestException as e:
                st.error(f"Error listing tools: {str(e)}")
                return []
        elif self.protocol == "stdio":
            stdio_transport =  await self.exit_stack.enter_async_context(stdio_client(self.server_params))
            self.stdio, self.write = stdio_transport
            self.session = await self.exit_stack.enter_async_context(ClientSession(self.stdio, self.write))
            await self.session.initialize()
            tools = await self.session.list_tools()
            return tools
        

def main():
    st.set_page_config(page_title="MCP Server Explorer", layout="wide")
    
    st.title("Model Context Protocol (MCP) Server Explorer")
    st.write("Connect to MCP servers and explore available tools")
    
    # Initialize session state for client
    if 'client' not in st.session_state:
        st.session_state.client = None
    
    # Load saved servers
    if 'saved_servers' not in st.session_state:
        st.session_state.saved_servers = load_saved_servers()
    
    # Create tabs for different sections
    tab1, tab2 = st.tabs(["Connect to Server", "Manage Servers"])
    
    with tab1:
        # Select protocol
        protocol = st.radio("Protocol", ["HTTP", "stdio"], horizontal=True)
        
        if protocol == "HTTP":
            # Input for MCP server URL
            server_url = st.text_input(
                "MCP Server URL",
                value="http://localhost:8000",
                placeholder="Enter the URL of the MCP server",
                key="server_url_input"
            )
            
            # Add a server selection dropdown
            http_servers = {name: details for name, details in st.session_state.saved_servers.items() 
                           if details.get("protocol") == "http"}
            
            server_options = [""] + list(http_servers.keys()) + ["Custom"]
            selected_server = st.selectbox(
                "Select from saved HTTP servers",
                server_options,
                index=0,
                key="http_server_select"
            )
            
            if selected_server and selected_server != "Custom":
                server_url = http_servers[selected_server]["url"]
                st.session_state.server_url_input = server_url
            
            # Initialize client only if connect button is pressed
            if st.button("Connect to HTTP Server"):
                if not server_url:
                    st.warning("Please enter a valid server URL")
                else:
                    # Clean up previous client if it exists
                    if st.session_state.client:
                        st.session_state.client.cleanup()
                    
                    st.session_state.client = MCPClient(server_url=server_url, protocol="http")
                    
                    # Get server info
                    with st.spinner("Connecting to server..."):
                        server_info = st.session_state.client.get_server_info()
                    
                    if server_info:
                        st.success(f"Successfully connected to MCP server at {server_url}")
                        
                        # Display server information
                        st.subheader("Server Information")
                        st.json(server_info)
                        
                        # Get tools
                        with st.spinner("Fetching available tools..."):
                            tools = st.session_state.client.list_tools()
                        
                        # Display tools
                        st.subheader("Available Tools")
                        if tools:
                            for i, tool in enumerate(tools, 1):
                                with st.expander(f"{i}. {tool.get('name', 'Unknown Tool')}"):
                                    st.json(tool)
                            
                            # Download tools as JSON
                            st.download_button(
                                label="Download Tools as JSON",
                                data=json.dumps(tools, indent=2),
                                file_name="mcp_tools.json",
                                mime="application/json"
                            )
                        else:
                            st.info("No tools available on this server")
                    else:
                        st.error(f"Failed to connect to MCP server at {server_url}")
        
        else:  # stdio protocol
            # # Input for command to execute
            # command = st.text_input(
            #     "Command to Execute",
            #     placeholder="Enter the command to start the MCP server",
            #     key="command_input"
            # )
            
            # Add a server selection dropdown
            stdio_servers = {name: details for name, details in st.session_state.saved_servers.items() 
                           if details.get("protocol") == "stdio"}
            
            server_options = [""] + list(stdio_servers.keys()) + ["Custom"]
            selected_server = st.selectbox(
                "Select from saved stdio servers",
                server_options,
                index=0,
                key="stdio_server_select"
            )
            
            if selected_server and selected_server != "Custom":
                command = stdio_servers[selected_server]["command"]
                program = stdio_servers[selected_server]["program"]
                #st.session_state.command_input = command
            
            # Initialize client only if connect button is pressed
            if st.button("Connect to stdio Server"):
                if not command:
                    st.warning("Please enter a valid command")
                else:
                    # Clean up previous client if it exists
                    if st.session_state.client:
                        st.session_state.client=None
                    
                    st.session_state.client = MCPClient(command=command, program=program, protocol="stdio")
                    
                    
                    # Get server info
                    with st.spinner("Connecting to server..."):
                        server_info = st.session_state.client.get_server_info()
                    
                    if server_info:
                        st.success(f"Successfully connected to stdio MCP server")
                        
                        # Display server information
                        st.subheader("Server Information")
                        st.json(server_info)
                        
                        # Get tools
                        with st.spinner("Fetching available tools..."):
                            response = asyncio.run(st.session_state.client.list_tools())
                        
                        # Display tools
                        st.subheader("Available Tools")
                        downloadable_json_tools = {}
                        if response:
                            for i, tool in enumerate(response.tools, 1):
                                with st.expander(f"{i}. {tool.name}"):
                                    st.json(tool)
                                    downloadable_json_tools.update({tool.name : tool.__dict__})

                            # Download tools as JSON
                            st.download_button(
                                label="Download Tools as JSON",
                                data=json.dumps(downloadable_json_tools, indent=2),
                                file_name="mcp_tools.json",
                                mime="application/json"
                            )
                        else:
                            st.info("No tools available on this server")
                    else:
                        st.error(f"Failed to connect to stdio MCP server. Check the command and try again.")
    
    with tab2:
        st.subheader("Manage MCP Servers")
        
        # Display current saved servers
        st.write("Currently saved servers:")
        
        if st.session_state.saved_servers:
            for i, (name, details) in enumerate(st.session_state.saved_servers.items()):
                col1, col2, col3, col4, col5 = st.columns([2, 1, 6, 5, 1])
                with col1:
                    st.text(name)
                with col2:
                    st.text(details.get("protocol", "http"))
                with col3:
                    if details.get("protocol") == "http":
                        st.text(details.get("url", ""))
                    else:
                        st.text(details.get("command", ""))
                with col4:
                    if details.get("protocol") == "http":
                        st.text(details.get("url", ""))
                    else:
                        st.text(details.get("program", ""))                        
                with col5:
                    if st.button("Delete", key=f"delete_{i}"):
                        del st.session_state.saved_servers[name]
                        save_servers(st.session_state.saved_servers)
                        st.rerun()
        else:
            st.info("No servers saved yet")
        
        # Add new server section
        st.subheader("Add New Server")
        
        # Protocol selection for new server
        new_protocol = st.radio("Protocol", ["HTTP", "stdio"], horizontal=True, key="new_protocol")
        
        with st.form("add_server_form"):
            new_server_name = st.text_input("Server Name", placeholder="Enter a name for the server")
            
            if new_protocol == "HTTP":
                new_server_url = st.text_input("Server URL", placeholder="Enter the URL of the server")
                #new_server_url = ""
                
            else:  # stdio
                new_server_command = st.text_input("Command", placeholder="Enter the command to start the server")
                new_server_program = st.text_input("server_program", placeholder="Enter the server program with absolute path")
                #new_server_command = ""
            
            submitted = st.form_submit_button("Add Server")
            if submitted:
                if not new_server_name:
                    st.warning("Please provide a name for the server")
                elif new_protocol == "HTTP" and not new_server_url:
                    st.warning("Please provide a URL for the HTTP server")
                elif new_protocol == "stdio" and not new_server_command:
                    st.warning("Please provide a command for the stdio server")
                elif new_protocol == "stdio" and not new_server_program:
                    st.warning("Please provide a server program with absolute path for the stdio server")                    
                else:
                    server_data = {
                        "protocol": new_protocol.lower(),
                    }
                    
                    if new_protocol == "HTTP":
                        server_data["url"] = new_server_url
                    else:
                        server_data["command"] = new_server_command
                        server_data["program"] = new_server_program
                    
                    st.session_state.saved_servers[new_server_name] = server_data
                    
                    if save_servers(st.session_state.saved_servers):
                        st.success(f"Server '{new_server_name}' added successfully")
                        st.rerun()
                    else:
                        st.error("Failed to save the server")

# Cleanup on app exit
def on_exit():
    if 'client' in st.session_state and st.session_state.client:
        st.session_state.client.cleanup()

# Register exit handler
import atexit
atexit.register(on_exit)

if __name__ == "__main__":
    main()
