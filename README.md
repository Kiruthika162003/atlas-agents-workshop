# Atlas agents workshop

Two sessions, one app. In the first we build Atlas, a map agent that finds
places near you, describes them from checked sources, and draws the walk to
each one. In the second we put it in a container, run it on Cloud Run, and
watch it scale.

| session | folder | you leave with |
|---|---|---|
| Connect, communicate and extend your agents | [demo1-build](demo1-build) | an agent with tools, an MCP server with a login, a second agent over A2A, a skill, and a map in front of them |
| Auto-scale your AI agent on Cloud Run | [demo2-deploy](demo2-deploy) | the same app in Docker, on Cloud Run, autoscaling, with chats stored in Firestore |

## Start here

```
git clone https://github.com/Kiruthika162003/atlas-agents-workshop.git
```

```
cd atlas-agents-workshop/demo1-build
```

Then follow the [attendee guide](guide/Atlas-Attendee-Guide.pdf). It assumes
nothing: it covers installing Python, Git and the Google Cloud CLI, creating a
project with billing, signing in, checking the setup, and every step of the
build with screenshots.

Already set up? The short version is in [demo1-build/README.md](demo1-build/README.md).

## What is in the repository

```
demo1-build/
  learn/               seven small agents, one new idea each (adk web)
  mcp_server/          the map tools as an MCP server, with an optional lock
  description_agent/   the second agent, served over A2A
  skills/              the walking tour skill
  atlas/               the web app and the recommendation agent
  check.py             tests your setup and says what to fix
  start.py             runs the whole app, on Gemini or on a local Gemma

demo2-deploy/
  atlas/ mcp_server/ description_agent/ skills/    the app from demo 1, with three small changes
  Dockerfile  serve.sh                             the container
  loadtest.py                                      20 users at once, from your laptop

guide/     the attendee guide (PDF, and the HTML it is built from)
slides/    the decks for both sessions, and the scripts that build them
```

## What you need

- Python 3.11 or newer
- Git
- A Google Cloud project with billing on, and the `gcloud` CLI signed in
- Docker Desktop, for the second session
- Optional: [Ollama](https://ollama.com) and a graphics card, to run the first
  session on a local Gemma model with no cloud account

## Rebuilding the guide and the slides

```
pip install playwright python-pptx
```

```
python guide/make_pdf.py
```

```
python slides/morning.py
```

```
python slides/afternoon.py
```
