# Agent 5 of 7: the same agent again. The only thing that moved is the server:
# it now runs on Cloud Run, so the tools no longer depend on anyone's laptop.
# Put the server's address in .env as ATLAS_REMOTE_MCP, ending in /mcp
# Run: adk web learn   then pick agent_5_remote_mcp

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
        url=os.getenv("ATLAS_REMOTE_MCP", "https://your-service-url/mcp"),
        headers={"Authorization": f"Bearer {google_token()}"},
        timeout=60,
    ),
)

root_agent = Agent(
    name="agent_5_remote_mcp",
    model=os.getenv("ATLAS_MODEL", "gemini-3.8-flash"),
    description="A local guide whose map tools run in the cloud, behind a login.",
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
