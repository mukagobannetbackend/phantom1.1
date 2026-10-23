The application creates tables on startup for a zero-friction first deploy. Flask-Migrate is included so a team can adopt versioned migrations as the schema evolves:

```bash
flask --app run.py db init
flask --app run.py db migrate -m "initial schema"
flask --app run.py db upgrade
```

Do not run destructive migration commands against the shared production database without a backup.