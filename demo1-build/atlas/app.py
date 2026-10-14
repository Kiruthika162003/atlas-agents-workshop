# The Atlas web app: a map, a chat box, and the recommendation agent behind them.
# Run: python atlas/app.py   (then open http://localhost:5000)

import asyncio
import json
import queue
import threading

from flask import Flask, Response, render_template, request
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from recommendation_agent import MODEL, root_agent

app = Flask(__name__)
runner = Runner(
    agent=root_agent,
    app_name="atlas",
    session_service=InMemorySessionService(),
    auto_create_session=True,
)

# ADK is async and Flask is not. The agent lives on one event loop in a side
# thread, so its MCP and A2A connections stay open between requests.
loop = asyncio.new_event_loop()
threading.Thread(target=loop.run_forever, daemon=True).start()

# How each tool reaches the agent. The page shows this as a tag on every call.
# Anything not listed here comes from the skill toolset.
VIA = {"geocode": "mcp", "nearby_places": "mcp", "walking_route": "mcp", "description_agent": "a2a"}


@app.get("/")
def home():
    return render_template("index.html", model=MODEL.split("/")[-1])


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
    app.run(port=5000, threaded=True)
