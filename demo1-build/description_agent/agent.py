# The description agent: give it one place, get back a short description you can trust.
# It runs as its own service and speaks A2A, so any agent can call it.
# Run: python description_agent/agent.py   (serves http://localhost:8002)

import os
import re
import unicodedata

import requests
import uvicorn
from dotenv import load_dotenv
from google.adk.a2a.utils.agent_to_a2a import to_a2a
from google.adk.agents import Agent
from google.adk.models import Gemini
from google.adk.tools import google_search
from google.genai import types

load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".env"))

MODEL = os.getenv("ATLAS_MODEL", "gemini-3.8-flash")

WIKIPEDIA = "https://en.wikipedia.org/w/api.php"
INTRO = {"action": "query", "format": "json", "prop": "extracts",
         "exintro": 1, "explaintext": 1, "exsentences": 5, "exlimit": "max"}


def look_up(place: str, city: str, lat: float, lon: float) -> dict:
    """Find the Wikipedia article about a place.

    Args:
        place: the name of the place, e.g. "Bradbury Building".
        city: the city it is in, e.g. "Los Angeles".
        lat: its latitude.
        lon: its longitude.
    """
    wanted = _words(place)
    nearby = {"generator": "geosearch", "ggscoord": f"{lat}|{lon}", "ggsradius": 400, "ggslimit": 20}
    by_name = {"generator": "search", "gsrsearch": f"{place} {city}", "gsrlimit": 3}

    # Among articles pinned near the spot, sharing most of the shorter name is
    # enough. A search by name can land anywhere, so there the whole title has to fit.
    for search, shorter_or_longer in ((nearby, min), (by_name, max)):
        reply = requests.get(
            WIKIPEDIA, params={**INTRO, **search},
            headers={"User-Agent": "atlas-workshop/1.0"}, timeout=10,
        )
        if not reply.ok:    # Wikipedia is rate limiting us; carry on without it
            continue
        pages = reply.json().get("query", {}).get("pages", {})
        for page in sorted(pages.values(), key=lambda p: p.get("index", 0)):
            title = _words(page["title"])
            if not (title and wanted and page.get("extract")):
                continue
            if len(title & wanted) / shorter_or_longer(len(title), len(wanted)) >= 0.6:
                return {"found": True, "title": page["title"], "summary": page["extract"]}
    return {"found": False, "note": "No article about this place. Do not guess facts."}


def _words(name: str) -> set:
    """The meaningful words of a name, lower case and without accents."""
    plain = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode().lower()
    return set(re.findall(r"\w+", plain)) - {"the", "of", "and", "a", "de", "la", "le", "du"}


# Descriptions already written, so a place asked about twice comes back at once
# instead of being searched again. Follow-up questions are always researched.
remembered = {}


def _asked(callback_context) -> str:
    """The request as one key: the place name, or the whole text when it holds a question."""
    asked = callback_context.user_content
    text = " ".join(part.text or "" for part in asked.parts) if asked and asked.parts else ""
    text = " ".join(text.lower().split())
    return text if "?" in text else text.split(",")[0]


def answer_from_memory(callback_context):
    """Skip the search when this place has been described already."""
    known = remembered.get(_asked(callback_context))
    return types.Content(role="model", parts=[types.Part(text=known)]) if known else None


def remember(callback_context, llm_response):
    """Keep a finished description, not a step where the model asks for a tool."""
    parts = llm_response.content.parts if llm_response.content else []
    text = "".join(part.text or "" for part in parts)
    if text.strip() and not any(part.function_call for part in parts):
        remembered[_asked(callback_context)] = text


def add_sources(callback_context, llm_response):
    """List the pages Google Search used under the description, so readers can check it."""
    grounding = llm_response.grounding_metadata
    if grounding and grounding.grounding_chunks and llm_response.content:
        pages = [f"{chunk.web.title} {chunk.web.uri}" for chunk in grounding.grounding_chunks[:3] if chunk.web]
        llm_response.content.parts.append(types.Part(text="\nSources:\n" + "\n".join(pages)))
    remember(callback_context, llm_response)
    return llm_response


if MODEL.startswith("gemini"):
    # On Gemini the tool is Google Search. It runs inside the model call, so
    # one call both searches and writes. Thinking is switched off: it added
    # about four seconds a call and the answers were no better.
    brain = dict(
        model=Gemini(model=MODEL, retry_options=types.HttpRetryOptions(attempts=4, initial_delay=2)),
        tools=[google_search],
        after_model_callback=add_sources,
        generate_content_config=types.GenerateContentConfig(
            thinking_config=types.ThinkingConfig(thinking_budget=0),
        ),
    )
else:
    # A local model has no built-in search. Its tool is look_up, the plain
    # Python function above, which reads Wikipedia.
    brain = dict(model=MODEL, tools=[look_up], after_model_callback=remember)

root_agent = Agent(
    name="description_agent",
    description="Describes one real place in a few checked sentences.",
    instruction=(
        "You are given one place from a map listing: its name, type and "
        "whatever else is known, such as cuisine, address, city and "
        "coordinates. Always check the place with your tool first. What "
        "you write next depends on the request.\n\n"
        "A listing on its own: describe the place for someone deciding "
        "whether to walk there, in two or three short sentences of plain text:\n"
        "- what it is, and what it is known for: a signature dish, a "
        "collection, an award, a piece of history\n"
        "- one practical tip for a visitor\n\n"
        "A listing followed by a question, such as what it serves or "
        "whether it suits an allergy or a diet: answer only that question, "
        "in two to four sentences, and do not describe the place again. "
        "For allergies and diets, report only what the sources say and "
        "tell the visitor to confirm with the staff before ordering.\n\n"
        "Every fact has to come from the tool result or the listing. If the "
        "tool finds nothing about this exact place, write one or two "
        "sentences from the listing alone and say that little is published "
        "about it. Never guess dishes, dates, prices, awards or people."
    ),
    before_agent_callback=answer_from_memory,
    **brain,
)

app = to_a2a(root_agent, port=8002)

if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8002)
