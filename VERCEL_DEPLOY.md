# Deploy to Vercel

## One-click setup

1. Push this repo to GitHub.
2. Import the project at [vercel.com/new](https://vercel.com/new).
3. Leave **Root Directory** as `.` (repository root).
4. Vercel reads `vercel.json` automatically — no extra build settings needed.

## Environment variables (optional)

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENAI_API_KEY` | No | Enables GPT-based claim reasoning. Without it, rule-based fallback is used. |
| `REACT_APP_API_URL` | No | Only if API is on a different domain. Leave unset for same-origin deploy. |

## What gets deployed

- **Frontend**: React app from `frontend/` → static files
- **API**: FastAPI via `api/index.py` (Mangum) → `/api/*`, `/query/*`, `/upload/*`, etc.

## Local preview with Vercel CLI

```bash
npm i -g vercel
vercel dev
```

## Notes

- SQLite uses `/tmp/feedback.db` on Vercel (ephemeral between cold starts).
- Uploaded document vectors are in-memory per instance.
- Sample policy: `documents/sample_policy.pdf` is bundled with the API function.
