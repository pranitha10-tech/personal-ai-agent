
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client

from mcp_servers.server_config import MCP_SERVERS


TOOL_SERVER_MAP = {}


async def discover_tools():
    """
    Discover tools from all configured MCP servers.
    """

    discovered_tools = []
    TOOL_SERVER_MAP.clear()

    for server_name, config in MCP_SERVERS.items():

        server_url = config["url"]

        print(f"Connecting to {server_name}: {server_url}")

        try:
            async with streamable_http_client(
                server_url
            ) as (read_stream, write_stream, _):

                async with ClientSession(
                    read_stream,
                    write_stream
                ) as session:

                    await session.initialize()

                    response = await session.list_tools()

                    for tool in response.tools:

                        if tool.name in TOOL_SERVER_MAP:
                            raise ValueError(
                                f"Duplicate MCP tool name: {tool.name}"
                            )

                        TOOL_SERVER_MAP[tool.name] = server_name

                        discovered_tools.append({
                            "name": tool.name,
                            "server": server_name,
                            "description": tool.description,
                            "input_schema": tool.inputSchema
                        })

            print(f"{server_name} discovery successful")

        except Exception as error:
            print(f"Could not connect to {server_name}: {error}")

    return discovered_tools


async def execute_tool(tool_name: str, arguments: dict):
    """
    Execute a tool on its corresponding MCP server.
    """
    print("executing tool")
    if tool_name not in TOOL_SERVER_MAP:
        await discover_tools()

    server_name = TOOL_SERVER_MAP.get(tool_name)

    if not server_name:
        raise ValueError(
            f"Tool '{tool_name}' is not available."
        )

    if server_name not in MCP_SERVERS:
        raise ValueError(f"Server '{server_name}' is not available")

    server_url = MCP_SERVERS[server_name]["url"]

    print(f"Executing {tool_name} through {server_name}")

    async with streamable_http_client(
        server_url
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

            if result.isError:
                raise RuntimeError(
                    f"MCP tool execution failed: {result.content}"
                )

            return result
