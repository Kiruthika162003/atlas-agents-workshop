"""Knock on the places server the way a stranger would.

No login:          python mcp_server/knock.py
With your login:   python mcp_server/knock.py --login
"""

import argparse
import asyncio
import logging
import subprocess
import warnings

warnings.filterwarnings("ignore")    # keep the output to our own two lines
logging.disable(logging.CRITICAL)

from google.adk.tools.mcp_tool import McpToolset, StreamableHTTPConnectionParams

options = argparse.ArgumentParser()
options.add_argument("--url", default="http://localhost:8001/mcp")
options.add_argument("--login", action="store_true", help="send the Google sign-in token from gcloud")
args = options.parse_args()

headers = {}
if args.login:
    asked = subprocess.run("gcloud auth print-identity-token", shell=True, capture_output=True, text=True)
    headers = {"Authorization": f"Bearer {asked.stdout.strip()}"}


async def knock():
    server = McpToolset(connection_params=StreamableHTTPConnectionParams(url=args.url, headers=headers, timeout=30))
    try:
        tools = await server.get_tools()
        if not tools:
            raise ConnectionError
    except Exception:
        print("Refused. The server wants a login it accepts (HTTP 401).")
        return
    print("Let in. Tools on offer:", ", ".join(tool.name for tool in tools))
    geocode = next(tool for tool in tools if tool.name == "geocode")
    found = await geocode.run_async(args={"place": "Eiffel Tower, Paris"}, tool_context=None)
    print("Called geocode('Eiffel Tower, Paris') ->", found["content"][0]["text"].replace("\n", " "))
    await server.close()


asyncio.run(knock())
