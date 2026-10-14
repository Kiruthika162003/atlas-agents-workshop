# Agent 3 of 7: same agent, same tools, but the tools now live in an MCP
# server. This file has no map code left in it.
# Start the server first:  python mcp_server/server.py
# Run: adk web learn   then pick agent_3_mcp

import os

from dotenv import load_dotenv
from google.adk.agents import Agent
from google.adk.tools.mcp_tool import McpToolset, StreamableHTTPConnectionParams

load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".env"))

places = McpToolset(
    connection_params=StreamableHTTPConnectionParams(url="http://localhost:8001/mcp", timeout=60),
)

root_agent = Agent(
    name="agent_3_mcp",
    model=os.getenv("ATLAS_MODEL", "gemini-3.8-flash"),
    description="A local guide whose map tools come from an MCP server.",
    instruction=(
        "You are Atlas, a local guide. People tell you where they are and "
        "what they are after: food, coffee, fun, shopping, outdoors, schools "
        "or essentials.\n"
        "Call geocode to find them, then nearby_places for what they want. "
        "Recommend the three most interesting results with their distance, "
        "in under 80 words. Only name places the tools returned, and say "
        "nothing about them that the tools did not."
    ),
    tools=[places],
)
