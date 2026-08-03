"""MCP Stdio Client Manager for AI Capacity Planning Advisor.

Connects to mcp_db_server.py via stdio subprocess transport (StdioServerParameters).
Provides dynamic discovery of Tools, Resources, and Prompts, ensuring complete decoupling.
"""
import os
import sys
import json
import asyncio
from typing import Dict, Any, List, Optional
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


class MCPDatabaseClient:
    """Manager for communicating with the MCP SQLite Database Server over Stdio."""

    def __init__(self, server_script_path: Optional[str] = None, python_executable: Optional[str] = None):
        if not server_script_path:
            server_script_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "mcp_db_server.py")
        if not python_executable:
            venv_python = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "venv", "bin", "python")
            python_executable = venv_python if os.path.exists(venv_python) else sys.executable

        self.server_script_path = server_script_path
        self.python_executable = python_executable
        self.server_params = StdioServerParameters(
            command=self.python_executable,
            args=[self.server_script_path],
            env={**os.environ, "PYTHONUNBUFFERED": "1", "PYTHONPATH": os.path.dirname(os.path.dirname(os.path.abspath(__file__)))}
        )

    async def initialize_db_via_mcp(self) -> Dict[str, Any]:
        """Convenience method to run init_db tool over stdio transport."""
        return await self.call_tool("init_db", {})

    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Dynamically execute an MCP tool via stdio transport.
        
        Args:
            tool_name: Name of the tool to execute (e.g., 'insert_metrics', 'query_metrics').
            arguments: Arguments payload dictionary.
            
        Returns:
            Parsed JSON result dictionary.
        """
        async with stdio_client(self.server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                result = await session.call_tool(tool_name, arguments)
                if result.content and len(result.content) > 0:
                    text_content = result.content[0].text
                    try:
                        return json.loads(text_content)
                    except json.JSONDecodeError:
                        return {"status": "success", "raw_text": text_content}
                return {"status": "success", "content": []}

    async def list_tools(self) -> List[Dict[str, Any]]:
        """Dynamically discover available MCP Tools at runtime."""
        async with stdio_client(self.server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                tools_response = await session.list_tools()
                return [
                    {
                        "name": tool.name,
                        "description": tool.description,
                        "input_schema": tool.inputSchema
                    }
                    for tool in tools_response.tools
                ]

    async def list_resources(self) -> List[Dict[str, Any]]:
        """Dynamically discover available MCP Resources at runtime."""
        async with stdio_client(self.server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                resources_response = await session.list_resources()
                return [
                    {
                        "uri": str(resource.uri),
                        "name": resource.name,
                        "description": resource.description,
                        "mime_type": resource.mimeType
                    }
                    for resource in resources_response.resources
                ]

    async def read_resource(self, uri: str) -> str:
        """Passive read of context from an MCP Resource URI (e.g. 'schema://database')."""
        async with stdio_client(self.server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                resource_content = await session.read_resource(uri)
                if resource_content and len(resource_content.contents) > 0:
                    return resource_content.contents[0].text
                return ""

    async def list_prompts(self) -> List[Dict[str, Any]]:
        """Dynamically discover available MCP Prompts at runtime."""
        async with stdio_client(self.server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                prompts_response = await session.list_prompts()
                return [
                    {
                        "name": prompt.name,
                        "description": prompt.description,
                        "arguments": [
                            {"name": arg.name, "description": arg.description, "required": arg.required}
                            for arg in (prompt.arguments or [])
                        ]
                    }
                    for prompt in prompts_response.prompts
                ]

    async def get_prompt(self, name: str, arguments: Dict[str, str]) -> Dict[str, Any]:
        """Fetch a standardized prompt template from the MCP server."""
        async with stdio_client(self.server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                prompt_result = await session.get_prompt(name, arguments)
                return {
                    "description": prompt_result.description,
                    "messages": [
                        {"role": msg.role, "content": msg.content.text}
                        for msg in prompt_result.messages
                    ]
                }
