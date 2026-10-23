# PhantomVault Pro

PhantomVault Pro is a Flask/PostgreSQL trading screenshot vault, journal, top-down analysis workspace, process-quality coach, and performance analytics app.

## Run locally

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
flask --app run.py init-db
python run.py
```

Open `http://127.0.0.1:5000`. The default local database is SQLite; set `DATABASE_URL` to a PostgreSQL connection string for production.

## Tests

```bash
pytest -q
```

The suite covers public health checks, registration and login, protected dashboard access, trade lifecycle and analytics, screenshot persistence, versioned coach reviews, and cross-user ownership isolation.

## Deploy to Render

Use **New → Blueprint** in Render and select this repository, or create a Python web service with build command `pip install -r requirements.txt` and start command `gunicorn -w 2 -b 0.0.0.0:$PORT run:app`. The included `render.yaml` provisions a PostgreSQL database and wires `DATABASE_URL`. Add a long random `SECRET_KEY` if you do not let Render generate one.

For durable screenshots, configure `CLOUDINARY_URL` in Render. Without it, uploads use the local `instance/uploads` folder, which is suitable for development only and is not durable across Render deploys. For the exact Cloudinary and Render steps, read [DEPLOYMENT.md](DEPLOYMENT.md). For AI coaching, set `OPENAI_API_KEY`, optionally `OPENAI_BASE_URL`, and `AI_MODEL`. The built-in rule-based coach works without an AI key and is intentionally evidence-first.

## CI/CD

`.github/workflows/ci-cd.yml` runs compile checks and pytest on Python 3.11 and 3.12 for every pull request and push to `main`. It can optionally call a Render deploy hook after tests pass. Enable that path by adding the GitHub Actions secret `RENDER_DEPLOY_HOOK_URL` and repository variable `RENDER_DEPLOY_ENABLED=true`. Render native Git auto-deploy remains available if you leave the variable unset.

## Security notes

Passwords are hashed with Werkzeug. Routes filter records by authenticated user ownership. CSRF protection, secure session flags, input validation, upload extension and size limits, and a public `/health` endpoint are enabled. Keep secrets in Render environment variables and never commit `.env`.

## Product modules

Authentication, dashboard, screenshot vault, trade workspaces, journal entries, top-down analysis checklist, versioned AI reviews, analytics, and CSV export are all wired in this first complete deployable build.
