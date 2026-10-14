# The recommendation agent: finds where you are and picks three spots worth the walk.
# Places come from the MCP server, the descriptions from the description agent over A2A.

import os

from dotenv import load_dotenv
from google.adk.agents import Agent
from google.adk.agents.remote_a2a_agent import AGENT_CARD_WELL_KNOWN_PATH, RemoteA2aAgent
from google.adk.models import Gemini
from google.adk.tools.agent_tool import AgentTool
from google.adk.skills import load_skill_from_dir
from google.adk.tools.mcp_tool import McpToolset, StreamableHTTPConnectionParams
from google.adk.tools.skill_toolset import SkillToolset
from google.genai import types

load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".env"))

MODEL = os.getenv("ATLAS_MODEL", "gemini-3.8-flash")

if MODEL.startswith("gemini"):
    # Retry when Vertex answers 429, and skip thinking: picking three places
    # from a list does not need it, and it added about four seconds a call.
    brain = dict(
        model=Gemini(model=MODEL, retry_options=types.HttpRetryOptions(attempts=4, initial_delay=2)),
        generate_content_config=types.GenerateContentConfig(
            thinking_config=types.ThinkingConfig(thinking_budget=0),
        ),
    )
else:
    brain = dict(model=MODEL)

places = McpToolset(
    connection_params=StreamableHTTPConnectionParams(url="http://localhost:8001/mcp", timeout=60),
)

description_agent = RemoteA2aAgent(
    name="description_agent",
    description="Describes one real place in a few checked sentences. Send one place per request.",
    agent_card="http://localhost:8002" + AGENT_CARD_WELL_KNOWN_PATH,
)

# A skill is a folder with a SKILL.md. The recommendation agent always sees its one-line
# description, and loads the full instructions only when a request needs them.
skills = SkillToolset(
    skills=[load_skill_from_dir(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "skills", "walking-tour"))],
)

root_agent = Agent(
    name="recommendation_agent",
    description="Recommends three nearby spots and has a description agent describe them.",
    instruction=(
        "You are Atlas, a local guide. People tell you where they are and "
        "what they are after: food, coffee, fun, shopping, outdoors, schools "
        "or essentials.\n\n"
        "1. If you do not have their coordinates yet, call geocode. If they "
        "gave coordinates, use them as they are. Keep using the same "
        "coordinates for later requests until they name a new place.\n"
        "2. If they have not said what they want, ask what they are after "
        "and name those seven kinds. Then stop.\n"
        "3. Call nearby_places for that kind. If they want one narrower "
        "thing inside it, such as only museums or only bookshops, pass it as "
        "`only`. If they named a cuisine, pass it. Look again with radius_m "
        "1500 when fewer than three come back.\n"
        "4. Choose three results that are different from each other. For "
        "food with no cuisine named, pick three different cuisines. Prefer "
        "places with character over chains, and keep them walkable.\n"
        "5. For each of the three places, make two calls. walking_route, "
        "from the person's coordinates to the place's. And the description agent, "
        "with a request that holds exactly one place: its name exactly as "
        "nearby_places gave it, then its type, cuisine, address, the city, "
        "latitude and longitude. Leave out whatever the listing does not "
        "have. Make all six calls together.\n"
        "6. The map draws each route and shows each description as it "
        "arrives. When everything is back, reply with the single word: "
        "done.\n\n"
        "Essentials are different: a pharmacy or a cash machine needs no "
        "story. Take the three nearest, call walking_route for each, skip "
        "the description agent, and reply with the single word: done.\n\n"
        "Follow-up questions about a place you already showed, such as what "
        "it serves, allergens, vegetarian options, prices or hours: do not "
        "answer from memory. Send the description agent one request with the "
        "place's name, address and city followed by the question, then "
        "reply with the single word: done. The map shows its answer.\n\n"
        "A request to add one place to their picks comes with that place's "
        "listing. Make the same two calls for it as in step 5, walking_route "
        "and the description agent, and reply with the single word: done. Do not "
        "search again.\n\n"
        "If a request matches one of your skills, such as a walking tour, "
        "load that skill and follow it in place of steps 3 to 6.\n\n"
        "Never make up a place, an address or coordinates. Only use what "
        "the tools return."
    ),
    tools=[places, AgentTool(description_agent), skills],
    **brain,
)
