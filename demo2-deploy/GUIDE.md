# Afternoon guide: Atlas on Cloud Run (2 hours)

This morning Atlas ran on one laptop for one person. The afternoon answers
one question: what happens when 100 people open it at once?

Before the session: Docker Desktop running, `gcloud` signed in, the
one-time setup from the README done, and the image built once so the base
layers are cached.

| time | step | what the room learns |
|---|---|---|
| 0:00 | The problem | one process, one machine, memory in RAM |
| 0:10 | 1. Containerize | a Dockerfile is a recipe anyone can run |
| 0:35 | 2. Deploy to Cloud Run | one command from folder to URL |
| 1:00 | 3. Scale | concurrency and instance limits, watched live |
| 1:25 | 4. Break it, then fix it | why memory has to leave the instance |
| 1:45 | 5. Cost and cleanup | what you pay for and how to stop |

## 0:00 The problem

Open `atlas/app.py` from this morning (`demo1-build`). Two lines decide
everything about this afternoon:

- `session_service=InMemorySessionService()` keeps every chat in the
  memory of one Python process.
- `app.run(port=5000, threaded=True)` is one process on one machine.

If that machine is busy, people wait. If it restarts, every chat is gone.

## 0:10 Step 1: containerize

Open the `Dockerfile` and read it top to bottom. It is short:

- `FROM python:3.13-slim`: start from a small Linux with Python.
- `COPY requirements.txt` and `RUN pip install` before the code, so a code
  change does not reinstall everything.
- `COPY . .`: the app.
- `ENV`: Gemini through Vertex AI. No key goes into the image.
- `CMD ["sh", "serve.sh"]`: what runs when the container starts.

Open `serve.sh`. The places server and the description agent start in the
background; the web app starts last, under gunicorn, on the port Cloud Run
hands it. Explain the gunicorn line once: one worker, sixteen threads.

Then the three changes in `atlas/app.py`, each marked `Change 1`, `2`, `3`.
Read the comments; they are the lesson.

Build it and run it:

```
docker build -t atlas .
```

```
docker run --rm -p 8080:8080 --env-file .env -e GOOGLE_APPLICATION_CREDENTIALS=/adc.json -v "$env:APPDATA\gcloud\application_default_credentials.json:/adc.json:ro" atlas
```

Open http://localhost:8080 and ask one question. Point at the top corner:
the model, and the four characters after "instance". Stop the container,
start it again, reload: a new name. That name is how we count instances
later.

## 0:35 Step 2: deploy to Cloud Run

```
gcloud run deploy atlas --source . --region us-central1 --no-allow-unauthenticated --memory 1Gi
```

While it builds (about three minutes), explain what the command does: it
uploads the folder, Cloud Build runs the same Dockerfile, the image lands
in Artifact Registry, and Cloud Run starts a revision from it.

- `--no-allow-unauthenticated` keeps strangers out. Every question costs
  model and search calls, so a public URL is a public wallet.
- `--memory 1Gi` because three Python processes share the instance.

Paste the service URL into a browser: 403. Then open the tunnel:

```
gcloud run services proxy atlas --region us-central1 --port 8081
```

Open http://localhost:8081 and ask the Eiffel Tower question. It is the
morning's app, running on Google's machines.

## 1:00 Step 3: scale

Two numbers control scaling. Draw them on a slide or a whiteboard.

- **Concurrency**: how many requests one instance handles at once. A turn
  of Atlas holds a request open for 20 seconds, so this should be small.
- **Max instances**: the ceiling. It is also the ceiling on your bill.

```
gcloud run services update atlas --region us-central1 --concurrency 4 --max-instances 5
```

Four at a time on five instances is room for twenty people. Send twenty:

```
python loadtest.py https://YOUR-SERVICE-URL --users 20
```

Each simulated user has a two-line chat, "Hi, my name is Asha." and "What
is my name?". From a rehearsal on 12 October 2026:

```
20 users, 5 instances answered
  21f6       ############### 15
  b812       ####### 7
  831d       ###### 6
  a3c3       ###### 6
  199d       ###### 6
remembered 3 of 20 users
a two-line chat took 5.5s at best, 20.9s in the middle, 87.6s at worst
```

Read it with the room:

- One instance became five, with nobody touching anything.
- `21f6` was already running, so it took the most. The others had to start
  first, which is the slow tail. That delay is a cold start.
- Open the Cloud Run console, Metrics tab, "Container instance count" to
  see the same thing as a graph. It lags by about a minute.

Run it a second time straight away: with five warm instances the middle
time drops. In rehearsal a single hello went from about 12 s to about 4 s.

Then ask what happens with 40 users on room for 20. Some requests come back
`HTTP 429` or `HTTP 500`: Cloud Run would not start a sixth instance. The
limit you set protected the bill, and the price was turning people away.
Rehearsal showed one such refusal even at exactly 20 users, while the new
instances were still starting.

Leave "remembered 3 of 20" on screen. That is the next step.

## 1:25 Step 4: break it, then fix it

Seventeen people told Atlas their name and it forgot. Nothing crashed. The
first message went to one instance and the second to another, and each
instance keeps its chats in its own memory.

Show Change 1 in `atlas/app.py` again. The fix is already there, behind a
variable:

```
gcloud run services update atlas --region us-central1 --set-env-vars ATLAS_SESSIONS=firestore
```

Same load test:

```
python loadtest.py https://YOUR-SERVICE-URL --users 20
```

Rehearsal:

```
20 users, 6 instances answered
  f4cb       ######### 9
  9f89       ######## 8
  1d1c       ######## 8
  817b       ######## 8
  4349       ###### 6
  HTTP 429   # 1
remembered 19 of 20 users
a two-line chat took 15.2s at best, 16.7s in the middle, 21.3s at worst
```

Nineteen remembered. The twentieth was the request Cloud Run refused, so
there was nothing to remember.

Open Firestore in the console and find the `adk-session` collection: one
document per chat, written by whichever instance was answering. The
instances are now interchangeable, which is what lets Cloud Run add and
remove them freely.

Finish in the browser through the tunnel: say where you are, then press
Food. The agent still knows where you are, and this time that knowledge is
a Firestore document, not one instance's memory.

## 1:45 Step 5: cost and cleanup

What this service costs:

- **Nothing while idle.** With no requests, Cloud Run scales to zero.
- **Instance time** while requests are being served.
- **Model tokens** for every agent step.
- **Search grounding**, per request. Each full Atlas question makes three.
  This is the largest line, and the reason the load test only says hello.
- **Firestore**: a handful of small writes per chat.

Two settings worth mentioning and not turning on today:

- `--min-instances 1` removes the cold start and is billed around the clock.
- `--allow-unauthenticated` makes the URL public. Do it for a launch, with
  a max-instances ceiling and a budget alert in place first.

Clean up:

```
gcloud run services delete atlas --region us-central1
```

## If something goes wrong

| what you see | why | what to do |
|---|---|---|
| `docker build` cannot connect | Docker Desktop is not running | start it and wait for the whale to settle |
| A question asked in the first seconds after a start fails | the places server and the description agent are still starting | ask again |
| 403 in the browser | the service is private | use the `gcloud run services proxy` tunnel |
| A tool row says the map service refused the request | OpenStreetMap's free service turns away some cloud addresses | ask again; a new instance often has a different address |
| The load test prints `HTTP 429` or `HTTP 500` | more requests than instances times concurrency | that is the lesson of step 3, not a bug |
| "remembered" stays low after the Firestore switch | the new revision is not serving yet | wait for the update command to finish, then rerun |
