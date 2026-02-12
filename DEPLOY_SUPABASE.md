Supabase Deployment Guide

This project can run with Supabase (Postgres) or with local SQLite for development.

1) Required environment variables (for Supabase):

- USE_SUPABASE=True
- DB_HOST=db.<your>.pooler.supabase.co  # use the Pooler endpoint
- DB_PORT=5432
- DB_NAME=postgres
- DB_USER=postgres
- DB_PASSWORD=<your_db_password>
- SECRET_KEY=<your_secret>
- DEBUG=False
- ALLOWED_HOSTS=yourdomain.com,localhost,127.0.0.1

2) Steps to deploy (example workflow):

- Install dependencies (ensure `psycopg2-binary` is in requirements.txt):

```bash
pip install -r requirements.txt
```

- Migrate DB:

```bash
python manage.py migrate
```

- Collect static files:

```bash
python manage.py collectstatic --noinput
```

- Run the application (production example using gunicorn):

```bash
gunicorn restaurant_project.wsgi
```

3) Troubleshooting

- If you see DNS resolution errors for the pooler endpoint, try the Pooler endpoint first. If your host can't resolve pooler, ensure:
  - You copied the exact pooling host from Supabase dashboard
  - Your deployment environment allows outbound DNS and TCP connections to Supabase

- If connection still fails, verify the Supabase project is active in the Supabase dashboard.

4) Local testing

- To test locally without Supabase, leave `USE_SUPABASE` unset or false and the app will use `db.sqlite3`.

5) Security

- Keep `SECRET_KEY` secret and use `DEBUG=False` in production.
- Ensure `ALLOWED_HOSTS` includes your deployment domain(s).
