# Speaker guide: 75 minutes

One question, asked again at every step, with one new idea each time:

> I'm at Grand Central Market in Los Angeles. Where should I eat?

Attendees have their own handout, `guide/Atlas-Attendee-Guide.pdf`. This page
is the order to present in.

Before the session: run `python check.py`, then ask the question once in the
map app so the first model call and the map tiles are warm.

| time | open | the one new idea | what the room sees |
|---|---|---|---|
| 0:00 | the finished map, 30 seconds | where we are going | pins, routes, descriptions |
| 0:05 | `agent_1_simple` | an agent is a model with a job | a confident answer, checked against nothing |
| 0:12 | `agent_2_tools` | a tool is a Python function | real places, and the tool calls in the Events tab |
| 0:20 | `agent_3_mcp` | MCP serves the tools | same answer; the agent file has no map code |
| 0:28 | `agent_4_mcp_auth` | who may call the tools | the break-in, the lock, the login |
| 0:42 | `agent_5_remote_mcp` | the server leaves the laptop | one line changes: the address |
| 0:50 | `agent_6_a2a` | asking another agent | the agent card, then three requests to it |
| 0:58 | `agent_7_skills` | a new job from one file | a walking tour |
| 1:05 | the map app | everything together | `mcp`, `a2a` and `skill` rows |
| 1:10 | recap and questions | | |

## Each step, the same four moves

1. **Predict.** "What will it say this time?" Take two answers from the room.
2. **Show the one change in the code.** A few lines, nothing else on screen.
3. **Ask the question.**
4. **Name what changed** in one sentence, and move on.

## Terminals to have open

| terminal | command | from |
|---|---|---|
| 1 | `adk web learn` | the start |
| 2 | `python mcp_server/server.py` | step 3 |
| 3 | `python mcp_server/knock.py` | step 4 |
| 3 | `python description_agent/agent.py` | step 6 |

## The auth step, in order

1. Server running open. In terminal 3: `python mcp_server/knock.py`. It is let in.
2. Stop the server. Start it with `python mcp_server/server.py --allow you@gmail.com`.
3. `python mcp_server/knock.py` again: refused, and the server logs `401`.
4. `python mcp_server/knock.py --login`: let in.
5. Pick `agent_4_mcp_auth` and ask the question.
6. Stop the server and start it open again. The later steps send no login.

## The map, at the end

Stop everything, then `python start.py`. Take a city from the audience. Then:

1. a follow-up question about one of the places
2. a grey dot, **Add to my picks**
3. **More**, then **Essentials**
4. "Plan me a walking tour of fun things."

## If something goes wrong

| what you see | what to do |
|---|---|
| `429` or "rate limited" | wait a few seconds and ask again |
| a row ends "failed: the map service refused" | wait a few seconds and ask again |
| an agent has no tools | the places server is stopped or still locked |
| Gemini keeps failing | `python start.py`, choose `gemma` |
