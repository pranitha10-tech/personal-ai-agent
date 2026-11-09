
import json
from typing import TypedDict, List, Dict, Any
import traceback

from langgraph.graph import StateGraph, START, END
from langgraph.types import interrupt, Command
from langgraph.checkpoint.memory import InMemorySaver

from services.llm_service import get_json_llm_response
from mcp_servers.mcp_registry import discover_tools, execute_tool


# ==================================================
# 1. AGENT STATE
# ==================================================

class AgentState(TypedDict):
    prompt: str
    system_prompt: str
    plan: str
    actions: List[Dict[str, Any]]
    clarification_required: bool
    clarification_question: str
    approved: bool
    status: str
    execution_results: List[Dict[str, Any]]


# ==================================================
# 2. PLANNING NODE
# ==================================================

async def planning_node(state: AgentState):

    try:
        print("\n========== PLANNING NODE STARTED ==========")
        # Discover available MCP tools
        available_tools = await discover_tools()

        print("\n========== AVAILABLE MCP TOOLS ==========")
        print(json.dumps(available_tools, indent=4))
        print("=========================================\n")

        if not available_tools:
            raise ValueError("No MCP tools are currently available.")

        tool_catalog = json.dumps(
            available_tools,
            indent=4
        )

        planning_prompt = f"""
{state["system_prompt"]}

USER TASK:
{state["prompt"]}

AVAILABLE MCP TOOLS:
{tool_catalog}

YOUR RESPONSIBILITY:
Understand the user's task and create a structured execution plan.

IMPORTANT RULES:

1. Support general computer tasks.
2. Do not assume a particular operating system or application.
3. Use only the tools listed in AVAILABLE MCP TOOLS.
4. The tool field must exactly match an available tool name.
5. Never invent tools or capabilities.
6. Follow each tool's input schema when creating parameters.
7. If no available tool can perform the requested task,
   request clarification or explain the limitation.
8. Break complex tasks into logical actions.
9. Every action requires user approval.
10. Never claim that an action has already been executed.
11. Do not create arbitrary terminal commands.

RETURN JSON WITH EXACTLY THIS STRUCTURE:

{{
    "task_summary": "Short description of the task",
    "clarification_required": false,
    "clarification_question": "",
    "actions": [
        {{
            "id": 1,
            "description": "Description of the action",
            "tool": "Exact MCP tool name",
            "operation": "Operation to perform",
            "parameters": {{}},
            "expected_result": "Expected outcome",
            "requires_approval": true
        }}
    ]
}}

If clarification is needed, return an empty actions array.

Return valid JSON only. Do not include Markdown or code fences.
"""

        raw_response = await get_json_llm_response(planning_prompt)

        print("\n========== GEMINI JSON RESPONSE ==========")
        print(raw_response)
        print("==========================================")

        data = json.loads(raw_response)

        if not isinstance(data, dict):
            raise ValueError("Gemini response must be a JSON object")

        actions = data.get("actions", [])

        if not isinstance(actions, list):
            raise ValueError("'actions' must be a JSON array")

        clarification_required = data.get(
            "clarification_required", False
        )

        if not isinstance(clarification_required, bool):
            raise ValueError("clarification_required must be boolean")

        if clarification_required and actions:
            raise ValueError(
                "Clarification response must not contain actions"
            )

        if not clarification_required and not actions:
            raise ValueError(
                "Gemini returned no actions for a task that needs a plan"
            )

        # Build a set of real tool names
        available_tool_names = {
            tool["name"] for tool in available_tools
        }

        validated_actions = []

        for index, action in enumerate(actions, start=1):

            if not isinstance(action, dict):
                raise ValueError(
                    f"Action {index} must be a JSON object"
                )

            required_fields = [
                "description",
                "tool",
                "operation",
                "parameters",
                "expected_result"
            ]

            for field in required_fields:
                if field not in action:
                    raise ValueError(
                        f"Action {index} is missing '{field}'"
                    )

            if action["tool"] not in available_tool_names:
                raise ValueError(
                    f"Unknown MCP tool: {action['tool']}"
                )

            if not isinstance(action["parameters"], dict):
                raise ValueError(
                    f"Action {index} parameters must be an object"
                )

            validated_actions.append({
                "id": index,
                "description": str(action["description"]),
                "tool": action["tool"],
                "operation": str(action["operation"]),
                "parameters": action["parameters"],
                "expected_result": str(action["expected_result"]),
                "requires_approval": True
            })

        return {
            "plan": data.get(
                "task_summary",
                "Task execution plan"
            ),
            "actions": validated_actions,
            "clarification_required": clarification_required,
            "clarification_question": data.get(
                "clarification_question", ""
            ),
            "approved": False,
            "status": (
                "clarification_required"
                if clarification_required
                else "waiting_for_approval"
            )
        }

    
    except Exception as error:

        print("\n========== PLANNING ERROR ==========")
        print("Error:", repr(error))

        traceback.print_exception(
            type(error),
            error,
            error.__traceback__
        )

        print("===================================")

        return {
            "plan": "",
            "actions": [],
            "clarification_required": False,
            "clarification_question": "",
            "approved": False,
            "status": "planning_failed"
        }


# ==================================================
# 3. ROUTE AFTER PLANNING
# ==================================================

def route_after_planning(state: AgentState):

    if state["status"] == "planning_failed":
        return END

    if state["clarification_required"]:
        return END

    return "approval"


# ==================================================
# 4. APPROVAL NODE
# ==================================================

def approval_node(state: AgentState):

    decision = interrupt({
        "message": "Review the proposed task plan.",
        "plan": state["plan"],
        "actions": state["actions"],
        "question": "Do you approve this plan?"
    })

    if decision.get("approved") is True:

        return {
            "approved": True,
            "status": "plan_approved"
        }

    return {
        "approved": False,
        "status": "plan_rejected"
    }


# ==================================================
# 5. ROUTE AFTER APPROVAL
# ==================================================

def route_after_approval(state: AgentState):

    if state["approved"] is True:
        return "execution"

    return END


# ==================================================
# 6. EXECUTION NODE
# ==================================================

async def execution_node(state: AgentState):

    execution_results = []

    try:

        # Additional safety check
        if state["approved"] is not True:
            raise PermissionError(
                "Tool execution requires user approval."
            )

        for action in state["actions"]:

            if action["requires_approval"] is not True:
                raise PermissionError(
                    "Action does not have approval enabled."
                )

            tool_name = action["tool"]
            parameters = action["parameters"]

            print(f"\nExecuting MCP tool: {tool_name}")

            result = await execute_tool(
                tool_name,
                parameters
            )

            content = []

            for item in result.content:

                if hasattr(item, "text"):
                    content.append(item.text)
                else:
                    content.append(str(item))

            if result.isError:
                raise RuntimeError(
                    f"Tool {tool_name} returned an error: {content}"
                )

            execution_results.append({
                "action_id": action["id"],
                "tool": tool_name,
                "status": "success",
                "result": content
            })

        return {
            "execution_results": execution_results,
            "status": "execution_completed"
        }

    except Exception as error:

        print("Execution error:", str(error))

        return {
            "execution_results": execution_results + [{
                "status": "failed",
                "error": str(error)
            }],
            "status": "execution_failed"
        }


# ==================================================
# 7. BUILD GRAPH
# ==================================================

builder = StateGraph(AgentState)

builder.add_node("planning", planning_node)
builder.add_node("approval", approval_node)
builder.add_node("execution", execution_node)

builder.add_edge(START, "planning")

builder.add_conditional_edges(
    "planning",
    route_after_planning
)

builder.add_conditional_edges(
    "approval",
    route_after_approval
)

builder.add_edge("execution", END)

memory = InMemorySaver()

agent_graph = builder.compile(checkpointer=memory)


# ==================================================
# 8. RUN AGENT
# ==================================================

async def run_agent(
    prompt: str,
    thread_id: str,
    system_prompt: str
):

    config = {
        "configurable": {
            "thread_id": thread_id
        }
    }

    result = await agent_graph.ainvoke(
        {
            "prompt": prompt,
            "system_prompt": system_prompt,
            "plan": "",
            "actions": [],
            "clarification_required": False,
            "clarification_question": "",
            "approved": False,
            "status": "started",
            "execution_results": []
        },
        config=config
    )

    return result


# ==================================================
# 9. RESUME AGENT
# ==================================================

async def resume_agent(thread_id: str, approved: bool):

    config = {
        "configurable": {
            "thread_id": thread_id
        }
    }

    result = await agent_graph.ainvoke(
        Command(resume={"approved": approved}),
        config=config
    )

    return result
