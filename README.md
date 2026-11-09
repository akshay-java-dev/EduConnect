<<<<<<< HEAD
# EduConnect — Flask full starter

## Included
- Admin and student authentication with role-based route protection.
- Public registration always creates a student account.
- Admin dashboard, subjects, PDF notes, video URLs, exam builder and manual grading.
- MCQ auto-marking, written answer marking, exam timer and submission.
- Responsive Bootstrap UI, animated dark theme and basic PWA shell.
- SQLite local development and PostgreSQL/Supabase deployment configuration.

## Run on Windows / VS Code
```powershell
py -3.11 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
flask --app run.py init-db
flask --app run.py create-admin
python run.py
```
Open http://127.0.0.1:5000

If activation is blocked, run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`, then activate again.

## Supabase shared database
Create a Supabase project → Project Settings → Database → Connection string. Put the PostgreSQL URI in `.env` as `DATABASE_URL=...`. Never share or commit `.env`. For Render, set the same `DATABASE_URL` and a strong `SECRET_KEY` in environment variables.

## Render deployment
Push to GitHub, create a Render Web Service, build command `pip install -r requirements.txt`, start command `gunicorn run:app`. Add `DATABASE_URL` and `SECRET_KEY`. In Render Shell run `flask --app run.py init-db`, then `flask --app run.py create-admin`.

## Important production limitations
- Uploaded PDFs are stored on local disk in `instance/uploads`. Render disks are ephemeral unless persistent storage is configured. Use Supabase Storage or another persistent object store before public production use.
- PWA caches static files only; exams are not offline-capable.
- The exam timer is browser-assisted. High-stakes exams need stronger server-side attempt/deadline enforcement, audit logs and testing.
- `create_all()` is only for first-time setup. Use database migrations before schema changes.
- Add password reset, email verification, rate limiting, backups, file scanning and privacy/security review before real public launch.
=======
# EduConnect
Student Learning and Online Examination Platform
>>>>>>> e2cb4aecff09cbd7983c762c898418c050d375d9
