
import sys
import asyncio
from pathlib import Path

# Add the backend directory to Python's import path
BACKEND_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND_DIR))

from mcp_servers.mcp_registry import execute_tool


async def main():

    # ==========================================
    # 1. TEST LIST DIRECTORY
    # ==========================================

    print("\n========== LIST DIRECTORY ==========")

    result = await execute_tool(
        "list_directory_tool",
        {
            "path": "."
        }
    )

    print(result.content)


    # ==========================================
    # 2. TEST GET FILE INFORMATION
    # ==========================================

    print("\n========== FILE INFORMATION ==========")

    result = await execute_tool(
        "get_file_info_tool",
        {
            "path": "mcp_servers/server_config.py"
        }
    )

    print(result.content)


    # ==========================================
    # 3. TEST READ FILE
    # ==========================================

    print("\n========== READ FILE ==========")

    result = await execute_tool(
        "read_file_tool",
        {
            "path": "mcp_servers/server_config.py"
        }
    )

    print(result.content)


if __name__ == "__main__":
    asyncio.run(main())
