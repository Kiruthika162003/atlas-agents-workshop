# The Atlas web app: a map, a chat box, and the recommendation agent behind them.
# Same app as demo 1, with the three changes that make it ready for Cloud Run.
# Run locally: python atlas/app.py   (then open http://localhost:5000)

import asyncio
import json
import os
import queue
import threading
import uuid

from flask import Flask, Response, render_template, request
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from recommendation_agent import MODEL, root_agent

app = Flask(__name__)

# Change 1: where conversations live. In memory, each instance only knows the
# chats it served itself, so a follow-up that lands on another instance has
# lost its history. Firestore is shared by all of them.
if os.getenv("ATLAS_SESSIONS") == "firestore":
    from google.adk.integrations.firestore.firestore_session_service import FirestoreSessionService
    sessions = FirestoreSessionService()
else:
    sessions = InMemorySessionService()

runner = Runner(agent=root_agent, app_name="atlas", session_service=sessions, auto_create_session=True)

# ADK is async and Flask is not. The agent lives on one event loop in a side
# thread, so its MCP and A2A connections stay open between requests.
loop = asyncio.new_event_loop()
threading.Thread(target=loop.run_forever, daemon=True).start()

# How each tool reaches the agent. The page shows this as a tag on every call.
# Anything not listed here comes from the skill toolset.
VIA = {"geocode": "mcp", "nearby_places": "mcp", "walking_route": "mcp", "description_agent": "a2a"}

# Change 2: a name for this instance, sent with every reply, so the page and
# the load test can show how many instances are answering.
INSTANCE = uuid.uuid4().hex[:4]


@app.after_request
def name_the_instance(response):
    response.headers["X-Atlas-Instance"] = INSTANCE
    return response


@app.get("/")
def home():
    return render_template("index.html", model=MODEL.split("/")[-1], instance=INSTANCE)


@app.post("/chat")
def chat():
    """Run one turn and stream what the agent does, one JSON object per line."""
    body = request.get_json()
    message = types.Content(role="user", parts=[types.Part(text=body["text"])])
    steps = queue.Queue()

    async def run_turn():
        stories_shown = False
        try:
            async for event in runner.run_async(user_id="visitor", session_id=body["session"], new_message=message):
                for part in event.content.parts if event.content else []:
                    if call := part.function_call:
                        steps.put({"call": call.name, "id": call.id, "via": VIA.get(call.name, "skill"), "args": call.args})
                    elif reply := part.function_response:
                        steps.put({"result": reply.name, "id": reply.id, "data": plain(reply.response)})
                        stories_shown = stories_shown or reply.name == "description_agent"
                    # Once the descriptions are on the map, a wrap-up would only repeat them.
                    # And "done" is the agent's way of saying the map already shows everything.
                    elif part.text and not part.thought and not stories_shown and part.text.strip().lower() != "done":
                        steps.put({"text": part.text})
        except Exception as error:
            steps.put({"error": str(error).strip().splitlines()[-1]})
        steps.put(None)

    asyncio.run_coroutine_threadsafe(run_turn(), loop)
    return Response((json.dumps(step) + "\n" for step in iter(steps.get, None)), mimetype="application/x-ndjson")


def plain(response: dict):
    """MCP hands back a tool's return value as JSON text; the page wants the value."""
    if "content" not in response:
        return response.get("result", response)
    text = response["content"][0]["text"]
    try:
        return json.loads(text)
    except ValueError:
        return text


if __name__ == "__main__":
    # Change 3: Cloud Run chooses the port. In the container gunicorn reads it
    # (see serve.sh); this line keeps `python atlas/app.py` working locally.
    app.run(port=int(os.getenv("PORT", 5000)), threaded=True)
