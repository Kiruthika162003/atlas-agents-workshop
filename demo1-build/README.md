# Demo 1: build Atlas

Tell it where you are and what you are after. A recommendation agent picks
three places, a description agent describes each one from checked sources, and
the map draws the walking route to all three. Works anywhere OpenStreetMap has
data.

New to all of this? Follow the [attendee guide](../guide/Atlas-Attendee-Guide.pdf).
It starts from an empty laptop.

```
browser ── web app ── recommendation agent ──MCP──> places server
                              │                      geocode, nearby_places, walking_route
                              ├──A2A──> description agent ── Google Search (Gemini)
                              │                               or Wikipedia (Gemma)
                              └──skill── walking-tour
```

| folder | what it is | port |
|---|---|---|
| `learn/` | seven small agents for `adk web`, each one step further | 8000 |
| `mcp_server/` | the map tools as an MCP server, with an optional lock | 8001 |
| `description_agent/` | the second agent, served over A2A | 8002 |
| `skills/` | the walking tour skill, one file | |
| `atlas/` | the web app and the recommendation agent behind it | 5000 |

## Setup

```
python -m venv .venv
```

```
.venv\Scripts\activate
```

```
pip install -r requirements.txt
```

```
copy .env.example .env
```

On macOS and Linux the second line is `source .venv/bin/activate` and the last
is `cp .env.example .env`. Put your Google Cloud project ID in `.env`, sign in
with `gcloud auth application-default login`, then check everything:

```
python check.py
```

It tests Python, the packages, your sign-in, a real call to Gemini and the map
service, and tells you what to fix if one of them fails.

## Run the app

```
python start.py
```

It asks `gemini` or `gemma`, starts the three programs, and serves the map on
http://localhost:5000. Things to try:

- "I'm at Grand Central Market, Los Angeles. Find me food."
- "Find me mexican food." or the **Only …** buttons, to narrow a search
- a follow-up about a place: "What does Guisados serve for vegetarians?"
- click a grey dot, then **Add to my picks**
- **More** for coffee, shopping, outdoors and essentials
- "Plan me a walking tour of fun things."

Every step the agent takes appears in the chat with a tag: `mcp` for the
places server, `a2a` for the description agent, `skill` for the walking tour.

| on a card | where it comes from |
|---|---|
| name, type, address, opening hours, website | the OpenStreetMap listing |
| distance, walking time, the route line | the `walking_route` tool |
| Directions button | a Google Maps link built from two coordinates |
| the description and "Checked against" links | the description agent, grounded in Google Search |

## Learn it step by step

```
adk web learn
```

| pick | the one new idea | needs running |
|---|---|---|
| `agent_1_simple` | a model with instructions, nothing else | |
| `agent_2_tools` | three Python functions as tools | |
| `agent_3_mcp` | the same functions, served by `mcp_server/` | the places server |
| `agent_4_mcp_auth` | the server only lets in Google accounts you name | the places server, locked |
| `agent_5_remote_mcp` | the same server, running in the cloud | a deployed places server |
| `agent_6_a2a` | a second agent describes each place | the places server and the description agent |
| `agent_7_skills` | a walking tour, learned from one file | the places server |

Start the places server open or locked:

```
python mcp_server/server.py
```

```
python mcp_server/server.py --allow you@gmail.com
```

Knock on it the way a stranger would, then with your Google login:

```
python mcp_server/knock.py
```

```
python mcp_server/knock.py --login
```

Start the description agent:

```
python description_agent/agent.py
```

## Run it without Google Cloud

Install [Ollama](https://ollama.com), then pull Gemma and build the copy with
a larger context window. It is a 6 GB download and fits an 8 GB graphics card.

```
ollama pull gemma4:e4b-it-qat
```

```
ollama create atlas-gemma -f Modelfile
```

Choose `gemma` when `start.py` asks. For the lessons, set
`ATLAS_MODEL=ollama_chat/atlas-gemma` in `.env`.

## Good to know

- Places and routes come from free OpenStreetMap services that ask for light
  use, about one request a second. Fine for a workshop, not for production.
- On Gemini the description agent checks every place with Google Search and
  lists the pages it used. Grounded calls are billed on top of tokens. On Gemma
  it reads English Wikipedia instead.
- Thinking is switched off for both agents on Gemini. It added about four
  seconds to each of roughly ten calls a turn.
- The map app talks to the places server without a login, so run the server
  unlocked when you use the map.
