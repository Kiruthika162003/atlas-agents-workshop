# Agent 7 of 7: the recommendation agent learns a new job without a longer prompt.
# A skill is a folder with a SKILL.md: a description the agent always sees, and
# instructions it only loads when a request needs them.
# Start the server first:  python mcp_server/server.py
# Run: adk web learn   then pick agent_7_skills, and ask for a walking tour

import os

from dotenv import load_dotenv
from google.adk.agents import Agent
from google.adk.skills import load_skill_from_dir
from google.adk.tools.mcp_tool import McpToolset, StreamableHTTPConnectionParams
from google.adk.tools.skill_toolset import SkillToolset

HERE = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(HERE, "..", "..", ".env"))

places = McpToolset(
    connection_params=StreamableHTTPConnectionParams(url="http://localhost:8001/mcp", timeout=60),
)

skills = SkillToolset(skills=[load_skill_from_dir(os.path.join(HERE, "..", "..", "skills", "walking-tour"))])

root_agent = Agent(
    name="agent_7_skills",
    model=os.getenv("ATLAS_MODEL", "gemini-3.8-flash"),
    description="A local guide that can pick up new jobs from skill files.",
    instruction=(
        "You are Atlas, a local guide. People tell you where they are and "
        "what they are after: food, coffee, fun, shopping, outdoors, schools "
        "or essentials.\n"
        "Call geocode to find them, then nearby_places for what they want. "
        "Recommend the three most interesting results with their distance, "
        "in under 80 words. Only name places the tools returned, and say "
        "nothing about them that the tools did not.\n"
        "If a request matches one of your skills, load that skill and "
        "follow it exactly."
    ),
    tools=[places, skills],
)
