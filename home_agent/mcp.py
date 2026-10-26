"""Dependency-free stdio MCP server for Hermes. Human approval is never a tool."""
import json
import os
import sys

from .contracts import tool_schemas
from .errors import AppError
from .service import DEFAULT_DB, HomeAgent


def dispatch(app, request, actor):
    if not isinstance(request, dict) or request.get("jsonrpc") != "2.0":
        return {"jsonrpc": "2.0", "id": None, "error": {"code": -32600, "message": "Invalid request"}}
    if "id" not in request:
        return None
    response = {"jsonrpc": "2.0", "id": request["id"]}
    method = request.get("method")
    params = request.get("params") or {}
    if not isinstance(params, dict):
        return {**response, "error": {"code": -32602, "message": "Expected object params"}}
    if method == "initialize":
        version = params.get("protocolVersion")
        return {**response, "result": {"protocolVersion": version if version in {"2024-11-05", "2025-03-26", "2025-06-18"} else "2025-03-26",
                "capabilities": {"tools": {"listChanged": False}}, "serverInfo": {"name": "home-agent", "version": "0.1.0"},
                "instructions": "Fixtures and sandbox only. Human approvals and meal completion happen in the local console."}}
    if method == "ping":
        return {**response, "result": {}}
    if method == "tools/list":
        tools = tool_schemas(actor)
        tools.append({"name": "task_status", "description": "Read a task result, respecting the configured household role.",
                      "inputSchema": {"type": "object", "properties": {"task_id": {"type": "string"}},
                                      "required": ["task_id"], "additionalProperties": False}})
        return {**response, "result": {"tools": tools}}
    if method == "tools/call":
        try:
            name, args = params.get("name"), params.get("arguments", {})
            if name == "task_status":
                if not isinstance(args, dict) or set(args) != {"task_id"} or not isinstance(args["task_id"], str):
                    raise AppError("Only task_id is accepted.")
                result = app.task(args["task_id"], actor)
            else:
                result = app.tool(name, args, actor)
            return {**response, "result": {"content": [{"type": "text", "text": json.dumps(result, ensure_ascii=False)}], "isError": False}}
        except AppError as error:
            return {**response, "result": {"content": [{"type": "text", "text": str(error)}], "isError": True}}
    return {**response, "error": {"code": -32601, "message": "Method not found"}}


def main():
    actor = os.environ.get("HOME_AGENT_ROLE", "cook")
    HomeAgent._actor(actor)
    app = HomeAgent(os.environ.get("HOME_AGENT_DB", str(DEFAULT_DB)))
    if hasattr(sys.stdin, "reconfigure"):
        sys.stdin.reconfigure(encoding="utf-8")
        sys.stdout.reconfigure(encoding="utf-8")
    while True:
        line = sys.stdin.readline(1_000_001)
        if not line:
            break
        try:
            if len(line) > 1_000_000:
                break
            request = json.loads(line)
            if isinstance(request, list):
                response = [r for item in request if (r := dispatch(app, item, actor)) is not None]
            else:
                response = dispatch(app, request, actor)
        except (ValueError, TypeError):
            response = {"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": "Parse error"}}
        except Exception:
            response = {"jsonrpc": "2.0", "id": None, "error": {"code": -32603, "message": "Internal error"}}
        if response is not None:
            print(json.dumps(response, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
