
from mcp.server.fastmcp import FastMCP

from services.filesystem_service import (
    list_directory,
    get_file_info,
    read_file
)


# ==================================================
# 1. CREATE FILESYSTEM MCP SERVER
# ==================================================

mcp = FastMCP("Universal Agent Filesystem Server")


# ==================================================
# 2. LIST DIRECTORY
# ==================================================

@mcp.tool()
def list_directory_tool(path: str) -> list:
    """
    List files and folders inside the specified directory.
    Accepts an absolute path or a path relative to the
    current working directory.
    """

    return list_directory(path)


# ==================================================
# 3. GET FILE INFORMATION
# ==================================================

@mcp.tool()
def get_file_info_tool(path: str) -> dict:
    """
    Get information about a file or directory.
    """

    return get_file_info(path)


# ==================================================
# 4. READ FILE
# ==================================================

@mcp.tool()
def read_file_tool(path: str) -> str:
    """
    Read the text content of a file.
    """

    return read_file(path)
