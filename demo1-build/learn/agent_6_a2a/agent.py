# Agent 6 of 7: the recommendation agent picks the spots, a second agent writes about them.
# The description agent is a separate service; the recommendation agent reaches it over A2A.
# Start both first:  python mcp_server/server.py   and   python description_agent/agent.py
# Run: adk web learn   then pick agent_6_a2a

import os

from dotenv import load_dotenv
from google.adk.agents import Agent
from google.adk.agents.remote_a2a_agent import AGENT_CARD_WELL_KNOWN_PATH, RemoteA2aAgent
from google.adk.tools.agent_tool import AgentTool
from google.adk.tools.mcp_tool import McpToolset, StreamableHTTPConnectionParams

load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".env"))

places = McpToolset(
    connection_params=StreamableHTTPConnectionParams(url="http://localhost:8001/mcp", timeout=60),
)

description_agent = RemoteA2aAgent(
    name="description_agent",
    description="Describes one real place in a few checked sentences. Send one place per request.",
    agent_card="http://localhost:8002" + AGENT_CARD_WELL_KNOWN_PATH,
)

root_agent = Agent(
    name="agent_6_a2a",
    model=os.getenv("ATLAS_MODEL", "gemini-3.8-flash"),
    description="A local guide that asks a description agent agent about each spot.",
    instruction=(
        "You are Atlas, a local guide. People tell you where they are and "
        "what they are after: food, coffee, fun, shopping, outdoors, schools "
        "or essentials.\n"
        "Call geocode to find them, then nearby_places for what they want. "
        "Choose the three most interesting results. Ask the description agent "
        "about each one, one request per place, giving the name, type, city "
        "and coordinates. Reply with each place, its distance, and the "
        "description_agent's description unchanged. Only name places the tools "
        "returned."
    ),
    tools=[places, AgentTool(description_agent)],
)
