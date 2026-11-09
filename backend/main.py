
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
import uuid

from agent.graph import run_agent, resume_agent


# ==================================================
# 1. APPLICATION CONFIGURATION
# ==================================================

app = FastAPI(
    title="Universal Voice AI Agent",
    description=(
        "A cross-platform AI desktop agent that understands "
        "voice and text commands and performs supported tasks."
    ),
    version="1.0.0"
)


# ==================================================
# 2. UNIVERSAL AGENT INSTRUCTIONS
# ==================================================

SYSTEM_PROMPT = """
You are a UNIVERSAL AI DESKTOP AGENT.

Your purpose is to understand the user's instructions
and help complete any supported computer task.

You are NOT limited to coding, programming, or IDE tasks.

You must be capable of understanding requests involving:

1. Desktop application management
2. Browser automation
3. Internet research
4. Product and price comparisons
5. File and folder management
6. Document creation and editing
7. Spreadsheet operations
8. Programming and software development
9. IDE interactions
10. Terminal operations
11. System and application settings
12. Other supported computer workflows

GENERAL BEHAVIOUR:

- Understand the actual intention of the user.
- Focus on the expected outcome, not just keywords.
- Do not assume a particular application.
- Do not assume a particular browser or IDE.
- Do not assume every task is a coding task.
- Support simple and complex multi-step requests.
- Break complex requests into logical actions.
- Choose tools according to the task.
- Use multiple tools when necessary.
- Avoid unnecessary actions.
- Never invent available applications or capabilities.
- Ask questions if essential information is missing.
- Consider the user's operating system.
- Support Windows, macOS and Linux through
  platform-specific capabilities.

AVAILABLE TOOL CATEGORIES:

1. desktop
   Opening and interacting with desktop applications.

2. browser
   Browser navigation, website interaction and searching.

3. filesystem
   Creating, reading, editing and organizing files.

4. terminal
   Command-line operations.

5. ide
   Interacting with supported IDEs and code editors.

6. documents
   Creating and editing documents and spreadsheets.

7. web_research
   Researching and comparing information online.

IMPORTANT EXECUTION RULES:

- You are responsible for planning, not directly
  executing computer operations.
- Never claim that an action has been completed
  during the planning stage.
- Every executable action requires user approval.
- Do not silently perform operations.
- Do not invent tools that are unavailable.
- Do not generate arbitrary terminal commands.
- Identify potentially destructive operations.
- Ask for clarification when the request is ambiguous.
- Explain unavailable capabilities honestly.

OUTPUT REQUIREMENTS:

Return a structured task plan.

Each action must contain:

- id
- description
- tool
- operation
- parameters
- expected_result
- requires_approval

The plan must represent the user's actual request.

Do not use fixed examples as templates.

Determine every action dynamically from the
current user request and available capabilities.
"""


# ==================================================
# 3. REQUEST MODELS
# ==================================================

class ChatRequest(BaseModel):
    prompt: str = Field(..., min_length=1)


class ApprovalRequest(BaseModel):
    thread_id: str
    approved: bool


class ClarificationRequest(BaseModel):
    thread_id: str
    clarification: str = Field(..., min_length=1)


# ==================================================
# 4. HOME ENDPOINT
# ==================================================

@app.get("/")
def home():

    return {
        "message": "Universal Voice AI Agent is running",
        "status": "online",
        "version": "1.0.0"
    }


# ==================================================
# 5. HEALTH CHECK
# ==================================================

@app.get("/health")
def health():

    return {
        "status": "healthy",
        "service": "Universal Voice AI Agent"
    }


# ==================================================
# 6. CHAT ENDPOINT
# ==================================================

@app.post("/chat")
async def chat(request: ChatRequest):

    try:

        thread_id = str(uuid.uuid4())

        result = await run_agent(
            prompt=request.prompt,
            thread_id=thread_id,
            system_prompt=SYSTEM_PROMPT
        )

        interruptions = result.get("__interrupt__", [])
        print("\n========== COMPLETE GRAPH RESULT ==========")
        print(result)
        print("===========================================\n")

        print("\n========== INTERRUPT OBJECT ==========")
        interruptions = result.get("__interrupt__", [])

        # Approval required
        if interruptions:

            return {
                "thread_id": thread_id,
                "status": "pending_approval",
                "approval_request": interruptions[0].value
            }

        # Clarification required
        if result["status"] == "clarification_required":
            
            return {
                "thread_id": thread_id,
                "status": "clarification_required",
                "question": result["clarification_question"]
            }

        # Planning failed
        if result["status"] == "planning_failed":

            return {
                "thread_id": thread_id,
                "status": "planning_failed",
                "message": result["plan"]
            }

        return {
            "thread_id": thread_id,
            "status": result["status"],
            "plan": result["plan"],
            "actions": result["actions"]
        }

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=f"Agent error: {str(error)}"
        )


# ==================================================
# 7. APPROVAL ENDPOINT
# ==================================================

@app.post("/approve")
async def approve_plan(request: ApprovalRequest):
    try:
        result = await resume_agent(
            thread_id=request.thread_id,
            approved=request.approved
        )

        return {
            "thread_id": request.thread_id,
            "status": result.get("status", "unknown"),
            "approved": result.get("approved", False),
            "plan": result.get("plan", ""),
            "actions": result.get("actions", [])
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Approval error: {str(e)}"
        )

# ==================================================
# 8. CLARIFICATION ENDPOINT
# ==================================================

@app.post("/clarify")
def clarify(request: ClarificationRequest):

    raise HTTPException(
        status_code=501,
        detail=(
            "Clarification workflow has not been "
            "implemented yet."
        )
    )
