
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client


UTILITY_SERVER_URL = "http://127.0.0.1:8001/mcp"


async def discover_tools():
    """
    Connect to the utility MCP server
    and discover its available tools.
    """

    async with streamable_http_client(
        UTILITY_SERVER_URL
    ) as (read_stream, write_stream, _):

        async with ClientSession(
            read_stream,
            write_stream
        ) as session:

            await session.initialize()

            response = await session.list_tools()

            discovered_tools = []

            for tool in response.tools:
                discovered_tools.append({
                    "name": tool.name,
                    "description": tool.description,
                    "input_schema": tool.inputSchema
                })

            return discovered_tools


async def execute_tool(tool_name: str, arguments: dict):
    """
    Execute a tool on the utility MCP server.
    """

    async with streamable_http_client(
        UTILITY_SERVER_URL
    ) as (read_stream, write_stream, _):

        async with ClientSession(
            read_stream,
            write_stream
        ) as session:

            await session.initialize()

            result = await session.call_tool(
                tool_name,
                arguments
            )

            return result
