"""Check your setup, one thing at a time. It stops at the first problem and says how to fix it.

Run: python check.py
"""

import os
import shutil
import sys


def ok(what):
    print(f"  [ ok ]  {what}")


def stop(what, fix):
    print(f"  [ FIX ] {what}\n          {fix}")
    sys.exit(1)


print("\nChecking your setup\n")

# 1. Python itself
version = f"{sys.version_info.major}.{sys.version_info.minor}"
if sys.version_info < (3, 11):
    stop(f"Python {version} is too old.", "Install Python 3.11 or newer from python.org/downloads.")
ok(f"Python {version}")

# 2. The packages from requirements.txt
try:
    import flask  # noqa: F401
    import google.adk  # noqa: F401
    import mcp  # noqa: F401
    import requests
    from dotenv import load_dotenv
except ImportError as missing:
    stop(f"A package is missing: {missing.name}.",
         "Switch on the virtual environment, then run: pip install -r requirements.txt")
ok("The packages are installed")

# 3. The settings file
here = os.path.dirname(os.path.abspath(__file__))
if not os.path.exists(os.path.join(here, ".env")):
    stop("There is no .env file in this folder.", "Copy .env.example to .env and put your Project ID in it.")
load_dotenv(os.path.join(here, ".env"))
project = os.getenv("GOOGLE_CLOUD_PROJECT", "")
if not project or project == "your-project-id":
    stop(".env still has the placeholder project.", "Open .env and set GOOGLE_CLOUD_PROJECT to your Project ID.")
ok(f"The settings file points at project {project}")

# 4. The Google Cloud command line tool
if not shutil.which("gcloud"):
    stop("The gcloud command was not found.",
         "Install the Google Cloud CLI, then close this terminal and open a new one.")
ok("gcloud is installed")

# 5. The sign-in that programs use
import google.auth
from google.auth.exceptions import DefaultCredentialsError

try:
    google.auth.default()
except DefaultCredentialsError:
    stop("Programs on this computer are not signed in to Google Cloud.",
         "Run: gcloud auth application-default login")
ok("Programs on this computer are signed in")

# 6. One real question to Gemini
from google import genai

model = os.getenv("ATLAS_MODEL", "gemini-3.8-flash")
if model.startswith("gemini"):
    try:
        client = genai.Client()
        reply = client.models.generate_content(model=model, contents="Reply with the single word: ready")
    except Exception as problem:
        text = str(problem)
        if "billing" in text.lower():
            stop("Gemini refused: billing is off for this project.", "Switch on billing for the project in the Cloud console.")
        if "has not been used" in text or "is disabled" in text:
            stop("Gemini refused: Vertex AI is not switched on for this project.",
                 "Run: gcloud services enable aiplatform.googleapis.com")
        if "429" in text:
            stop("Gemini is busy right now (429).", "Nothing is wrong on your side. Wait a minute and run this again.")
        stop("Gemini did not answer.", text.splitlines()[0][:200])
    ok(f"Gemini answered: {reply.text.strip()}   (model {model})")
else:
    ok(f"Using a local model, {model}. Skipping the Gemini check")

# 7. The free map service the tools rely on
try:
    found = requests.get("https://nominatim.openstreetmap.org/search",
                         params={"q": "Eiffel Tower, Paris", "format": "jsonv2", "limit": 1},
                         headers={"User-Agent": "atlas-workshop/1.0"}, timeout=15).json()
    ok(f"The map service answered: Eiffel Tower is at {float(found[0]['lat']):.4f}, {float(found[0]['lon']):.4f}")
except Exception:
    stop("The map service did not answer.", "Check your internet connection and run this again.")

print("\nEverything works. You are ready for step 1.\n")
