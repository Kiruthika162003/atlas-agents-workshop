# Agent 4 of 7: the same agent, but the tool server now has a lock on it.
# The agent shows a Google sign-in token; the server lets it in only if the
# account is on its list. This is MCP auth: OAuth tokens, checked by the server.
# Start the server locked:  python mcp_server/server.py --allow you@gmail.com
# Run: adk web learn   then pick agent_4_mcp_auth

import os
import subprocess

from dotenv import load_dotenv
from google.adk.agents import Agent
from google.adk.tools.mcp_tool import McpToolset, StreamableHTTPConnectionParams

load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".env"))


def google_token() -> str:
    """The identity token for whoever is signed in to gcloud. It is good for an hour."""
    asked = subprocess.run("gcloud auth print-identity-token", shell=True, capture_output=True, text=True)
    return asked.stdout.strip()


places = McpToolset(
    connection_params=StreamableHTTPConnectionParams(
        url="http://localhost:8001/mcp",
        headers={"Authorization": f"Bearer {google_token()}"},
        timeout=60,
    ),
)

root_agent = Agent(
    name="agent_4_mcp_auth",
    model=os.getenv("ATLAS_MODEL", "gemini-3.8-flash"),
    description="A local guide whose map tools sit behind a login.",
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
