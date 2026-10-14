# A small load test. Every user has a two-line chat at the same moment:
# "Hi, my name is Asha." and then "What is my name?"
# It shows how many instances answered, and how many users were remembered.
# Neither line needs a tool or a search, so 20 users cost a few cents.
# Run: python loadtest.py https://your-service-url --users 20

import argparse
import json
import subprocess
import time
import uuid
from collections import Counter
from concurrent.futures import ThreadPoolExecutor

import requests

NAMES = ["Asha", "Bruno", "Chen", "Divya", "Emeka", "Farah", "Goran", "Hana", "Imran", "Julia"]


def identity_token() -> str:
    """A private Cloud Run service wants proof of who is calling."""
    asked = subprocess.run("gcloud auth print-identity-token", shell=True, capture_output=True, text=True)
    return asked.stdout.strip()


def say(url: str, headers: dict, session: str, text: str) -> tuple:
    """Send one chat line. Returns the instance that answered and what it said."""
    try:
        reply = requests.post(f"{url}/chat", json={"session": session, "text": text}, headers=headers, timeout=120)
    except requests.RequestException as error:
        return type(error).__name__, ""
    if not reply.ok:
        return f"HTTP {reply.status_code}", ""
    said = [json.loads(line).get("text", "") for line in reply.text.splitlines() if line]
    return reply.headers.get("X-Atlas-Instance", "?"), " ".join(said)


def one_user(url: str, headers: dict, name: str) -> dict:
    session = uuid.uuid4().hex
    start = time.time()
    first, _ = say(url, headers, session, f"Hi, my name is {name}.")
    second, answer = say(url, headers, session, "What is my name? Answer with the name only.")
    return {"instances": [first, second], "remembered": name in answer, "seconds": time.time() - start}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("url")
    parser.add_argument("--users", type=int, default=20, help="chats running at the same time")
    args = parser.parse_args()

    url = args.url.rstrip("/")
    token = identity_token()
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    names = [NAMES[i % len(NAMES)] for i in range(args.users)]

    with ThreadPoolExecutor(args.users) as pool:
        users = list(pool.map(lambda name: one_user(url, headers, name), names))

    answered = Counter(instance for user in users for instance in user["instances"])
    times = sorted(user["seconds"] for user in users)
    print(f"{args.users} users, {len(answered)} instances answered")
    for instance, count in answered.most_common():
        print(f"  {instance:10} {'#' * count} {count}")
    print(f"remembered {sum(user['remembered'] for user in users)} of {args.users} users")
    print(f"a two-line chat took {times[0]:.1f}s at best, {times[len(times) // 2]:.1f}s in the middle, {times[-1]:.1f}s at worst")


if __name__ == "__main__":
    main()
