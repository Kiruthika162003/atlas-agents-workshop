#!/bin/sh
# One container, three processes. The places server and the description agent stay
# on localhost; only the web app listens on the port Cloud Run gives us.

python mcp_server/server.py &
python description_agent/agent.py &

# One worker so every request shares the agent's event loop; threads carry the
# concurrent requests. Keep --threads at or above the Cloud Run concurrency.
exec gunicorn --chdir atlas --bind :${PORT:-8080} --workers 1 --threads 16 --timeout 0 app:app
