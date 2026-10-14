# Atlas agents workshop

Connect, communicate and extend your agents. We build Atlas, a map agent that
finds places near you, describes them from checked sources, and draws the walk
to each one. One step at a time: an agent, tools, MCP, MCP auth, A2A and
skills.

You leave with an agent that has tools, an MCP server with a login, a second
agent over A2A, a skill, and a map in front of them.

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

guide/     the attendee guide (PDF, and the HTML it is built from)
```

## What you need

- Python 3.11 or newer
- Git
- A Google Cloud project with billing on, and the `gcloud` CLI signed in
- Optional: [Ollama](https://ollama.com) and a graphics card, to run it on a
  local Gemma model with no cloud account

## Next: put it in production

The second session takes this same app to Cloud Run: a container, a private
deploy, autoscaling, a load test, and chats stored in Firestore. It has its
own repository and guide:
[atlas-on-cloud-run](https://github.com/Kiruthika162003/atlas-on-cloud-run).

## Rebuilding the guide

```
pip install playwright
```

```
python guide/make_pdf.py
```
