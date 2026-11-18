
from contextlib import asynccontextmanager, AsyncExitStack

from fastapi import FastAPI

from mcp_servers.utility_server import mcp as utility_mcp
from mcp_servers.filesystem_server import mcp as filesystem_mcp


# ==================================================
# 1. CREATE MCP HTTP APPLICATIONS
# ==================================================

utility_app = utility_mcp.streamable_http_app()
filesystem_app = filesystem_mcp.streamable_http_app()


# ==================================================
# 2. MANAGE MCP SERVER LIFECYCLE
# ==================================================

@asynccontextmanager
async def lifespan(app: FastAPI):

    async with AsyncExitStack() as stack:

        await stack.enter_async_context(
            utility_mcp.session_manager.run()
        )

        print("Utility MCP server started")

        await stack.enter_async_context(
            filesystem_mcp.session_manager.run()
        )

        print("Filesystem MCP server started")

        yield

    print("MCP host shutting down")


# ==================================================
# 3. CREATE CENTRAL FASTAPI HOST
# ==================================================

app = FastAPI(
    title="Universal Agent MCP Host",
    lifespan=lifespan
)


# ==================================================
# 4. MOUNT MCP APPLICATIONS
# ==================================================

app.mount("/system", utility_app)
app.mount("/files", filesystem_app)


# ==================================================
# 5. ROOT ENDPOINT
# ==================================================

@app.get("/")
async def root():

    return {
        "message": "Universal Agent MCP Host",
        "status": "running",
        "endpoints": [
            "/system/mcp",
            "/files/mcp"
        ]
    }
