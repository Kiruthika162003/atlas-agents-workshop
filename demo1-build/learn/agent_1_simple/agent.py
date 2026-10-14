# Agent 1 of 7: Gemini with a name and a job. No tools, so no idea where you are.
# Run: adk web learn   then pick agent_1_simple

import os

from dotenv import load_dotenv
from google.adk.agents import Agent

load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".env"))

root_agent = Agent(
    name="agent_1_simple",
    model=os.getenv("ATLAS_MODEL", "gemini-3.8-flash"),
    description="A local guide with no tools.",
    instruction=(
        "You are Atlas, a local guide. People tell you where they are and "
        "what they are after: food, coffee, fun, shopping, outdoors, schools or essentials. Recommend "
        "three spots in under 80 words. You have NO tools and NO map: you "
        "cannot check distances, what is open, or whether a place still "
        "exists. Say so plainly when it matters."
    ),
)
