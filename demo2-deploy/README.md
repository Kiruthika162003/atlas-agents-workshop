# Demo 2: put Atlas on Cloud Run

The app from demo 1, in a container, on Cloud Run, scaling with traffic and
keeping its chats in Firestore. `GUIDE.md` has the order to teach it in.

## What changed from demo 1

The agents, the MCP server and the page are the same. Three small changes
in `atlas/app.py` make the app ready for the cloud, each marked with a
comment:

1. Chats can live in Firestore, not in the memory of one instance.
2. Every reply names the instance that sent it.
3. The port comes from the `PORT` variable.

New files: `Dockerfile`, `serve.sh` (starts the three processes inside the
container), and `loadtest.py`.

## One-time setup

```
gcloud services enable run.googleapis.com cloudbuild.googleapis.com artifactregistry.googleapis.com firestore.googleapis.com aiplatform.googleapis.com
```

```
gcloud firestore databases create --location us-central1
```

Skip the second command if the project already has a Firestore database.

## Run the container on your laptop

```
copy .env.example .env
```

Put your project id in `.env`, then build and run. The run command lends
the container your gcloud login so it can call Gemini.

```
docker build -t atlas .
```

PowerShell:

```
docker run --rm -p 8080:8080 --env-file .env -e GOOGLE_APPLICATION_CREDENTIALS=/adc.json -v "$env:APPDATA\gcloud\application_default_credentials.json:/adc.json:ro" atlas
```

macOS or Linux:

```
docker run --rm -p 8080:8080 --env-file .env -e GOOGLE_APPLICATION_CREDENTIALS=/adc.json -v ~/.config/gcloud/application_default_credentials.json:/adc.json:ro atlas
```

Open http://localhost:8080.

## Deploy

```
gcloud run deploy atlas --source . --region us-central1 --no-allow-unauthenticated --memory 1Gi
```

The service is private. Open it through a tunnel that signs you in:

```
gcloud run services proxy atlas --region us-central1 --port 8081
```

Then http://localhost:8081.

## Scale it

```
gcloud run services update atlas --region us-central1 --concurrency 4 --max-instances 5
```

```
python loadtest.py https://YOUR-SERVICE-URL --users 20
```

## Share the memory

```
gcloud run services update atlas --region us-central1 --set-env-vars ATLAS_SESSIONS=firestore
```

Run the load test again and compare the "remembered" line.

## Clean up

```
gcloud run services delete atlas --region us-central1
```

Cloud Run charges nothing while no one is using the service, so deleting it
is about tidiness. The container image stays in Artifact Registry until you
delete it there.

## Good to know

- The service account Cloud Run uses needs the Vertex AI User and Cloud
  Datastore User roles. The default compute account often has them through
  Editor.
- OpenStreetMap's free search service sometimes refuses requests from cloud
  addresses. When it does, the tool row on the page says so. For a real
  product, swap the two functions in `mcp_server/server.py` for a paid
  places API.
- Each full question makes three Google Search grounded calls, which are
  billed per request on top of tokens. The load test avoids them on purpose.
