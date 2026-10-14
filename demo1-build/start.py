# Start Atlas: pick a model, then run the places server, the description agent and the web app.
# Run: python start.py          (asks which model)
#      python start.py gemma    (or: gemini)

import os
import subprocess
import sys

MODELS = {
    "gemini": "gemini-3.8-flash",                 # Vertex AI, needs gcloud login and billing
    "gemma": "ollama_chat/atlas-gemma",     # this laptop, needs Ollama running
}
SERVICES = ["mcp_server/server.py", "description_agent/agent.py", "atlas/app.py"]


def main():
    choice = sys.argv[1] if len(sys.argv) > 1 else input("Model: gemini (Google Cloud) or gemma (this laptop)? [gemini] ")
    choice = choice.strip().lower() or "gemini"
    if choice not in MODELS:
        sys.exit(f"Unknown model '{choice}'. Use gemini or gemma.")

    here = os.path.dirname(os.path.abspath(__file__))
    env = {**os.environ, "ATLAS_MODEL": MODELS[choice]}
    running = [subprocess.Popen([sys.executable, os.path.join(here, s)], env=env) for s in SERVICES]
    print(f"\nAtlas is starting on http://localhost:5000 with {MODELS[choice]}. Ctrl+C stops everything.\n")
    try:
        running[-1].wait()
    except KeyboardInterrupt:
        pass
    finally:
        for process in running:
            process.terminate()


if __name__ == "__main__":
    main()
