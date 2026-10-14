FROM python:3.13-slim

WORKDIR /app

# Dependencies first: this layer is rebuilt only when requirements.txt changes.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Gemini through Vertex AI. On Cloud Run the service account signs the calls,
# so the image holds no key.
ENV GOOGLE_GENAI_USE_VERTEXAI=TRUE \
    GOOGLE_CLOUD_LOCATION=global \
    ATLAS_MODEL=gemini-3.8-flash \
    PYTHONUNBUFFERED=1

CMD ["sh", "serve.sh"]
