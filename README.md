# VoiceOrder Backend

FastAPI backend for the VoiceOrder AI phone ordering system. Receives Vapi end-of-call webhooks and stores orders in Supabase.

## Setup

```bash
uv sync
cp .env.example .env
# Fill in your Supabase and Vapi credentials in .env
```

## Run locally

```bash
uv run uvicorn main:app --reload --port 8000
```

## Deploy to Railway

1. Push this repo to GitHub
2. Connect the repo in Railway
3. Add environment variables: `SUPABASE_URL`, `SUPABASE_SERVICE_KEY`, `VAPI_SECRET`
4. Railway will auto-deploy using `railway.json`

## Endpoints

- `GET /health` — Health check
- `POST /orders` — Vapi webhook receiver
- `GET /orders?restaurant_id=swadeshi-frisco` — List orders
- `PATCH /orders/{order_id}/status` — Update order status
