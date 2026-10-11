# GLOBIS HR website — deployment & admin guide

## What changed
- **Fixed 500 errors** on /clients/ and /gallery/ (Cloudinary storage crashed pages when not configured). Image URLs can no longer crash a page.
- **Permanent media**: uploads go to **Cloudinary if configured, otherwise to the database**. CVs are always private (database, staff-only).
- **No Django admin needed**: staff portal at `/portal/` (jobs on/off, applications, clients, gallery photos/videos, branches + TikTok/Facebook/Instagram links, testimonials, contact messages, team accounts).
- **Public apply page** `/apply/` (+ `/jobs/`): no login; honeypot + signed timer + per-IP limit + duplicate check.
- New responsive design (no horizontal overflow), light/dark theme, floating WhatsApp button (+971 55 102 7642), WhatsApp job sharing.

## Render environment variables
| Variable | Purpose |
|---|---|
| `ADMIN_USERNAME`, `ADMIN_PASSWORD` | First admin account (created on deploy if missing). **Change the old password: it was committed in the repo.** |
| `CLOUDINARY_URL` (or `CLOUDINARY_CLOUD_NAME`, `CLOUDINARY_API_KEY`, `CLOUDINARY_API_SECRET`) | Permanent image/video storage on a CDN. Strongly recommended. |
| `DATABASE_URL` | Postgres (Render sets it when you attach the database). |
| `NOTIFY_EMAIL`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, `EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend` | Optional email alerts for new applications. |

## Media permanence
- With the Cloudinary variables set, new uploads live on Cloudinary (survive redeploys, CDN-fast).
- Without them, uploads are stored in Postgres (also survive redeploys). Render's *free* Postgres is time-limited (30 days when this was written; check Render's current policy), so for real permanence use Cloudinary and/or an always-free Postgres such as Neon or Supabase in `DATABASE_URL`.

## Keep the free web service awake
Free services sleep when idle (the cause of slow first loads). Point a free uptime monitor (e.g. UptimeRobot) at `https://globisconsultancy.com/healthz/` every 5 minutes.

## Portal
`/portal/`: sign in with the admin account. Main administrators add team accounts under **Team**.
`/admin/` (Django admin) remains as a hidden fallback for the main administrator.
