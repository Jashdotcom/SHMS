# Smart Hostel Management System (SHMS)

SHMS is a Django-based hostel management platform for student room booking, bed allocation, payments, complaints, service requests, announcements, analytics, invoices, APIs, and real-time notifications.

## Highlights

- Role-based access for students and administrators
- Room booking with bed availability, QR codes, cancellation, and expiry handling
- Payment tracking with late fees and PDF invoice/receipt generation
- Complaint and service request management with file uploads
- Announcement publishing with email and in-app notifications
- Analytics dashboard powered by Chart.js
- Django REST Framework API with JWT authentication
- Django Channels websocket notifications
- SQLite for development and PostgreSQL-ready production settings

## Tech Stack

- Python 3.14
- Django 6
- Django REST Framework
- Simple JWT
- Django Channels and Daphne
- Bootstrap 5
- Chart.js
- ReportLab
- OpenPyXL

## Setup

1. Clone the repository and enter the project.

```bash
git clone https://github.com/Jashdotcom/SHMS.git
cd SHMS
```

2. Create and activate a virtual environment.

```bash
python -m venv .venv
.venv\Scripts\activate
```

3. Install dependencies.

```bash
pip install -r requirements.txt
```

4. Create a local environment file.

```bash
copy .env.example .env
```

5. Apply migrations and create an admin user.

```bash
python manage.py migrate
python manage.py createsuperuser
```

6. Run the development server.

```bash
python manage.py runserver
```

Open `http://127.0.0.1:8000/`.

## Environment Variables

Use `.env.example` as the source of truth for local configuration.

```env
SECRET_KEY=replace-me
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=
REDIS_URL=
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
DEFAULT_FROM_EMAIL=no-reply@shms.local
BOOKING_EXPIRY_HOURS=24
```

Leave `DATABASE_URL` empty to use SQLite. Set it to a PostgreSQL URL in production. Leave `REDIS_URL` empty for the in-memory development channel layer; set it for production websocket scaling.

## API

Base path: `/api/`

- `POST /api/token/`
- `POST /api/token/refresh/`
- `GET /api/bookings/`
- `POST /api/bookings/`
- `GET /api/rooms/`
- `GET /api/payments/`
- `GET /api/announcements/`
- `GET /api/services/`

Example JWT request:

```bash
curl -X POST http://127.0.0.1:8000/api/token/ -H "Content-Type: application/json" -d "{\"username\":\"admin\",\"password\":\"your-password\"}"
```

## Booking Expiry

Expire unpaid bookings manually with:

```bash
python manage.py expire_unpaid_bookings
```

Schedule the command with Windows Task Scheduler, cron, or your hosting provider's scheduler.

## Verification

Useful local checks:

```bash
python manage.py check
python manage.py migrate
python manage.py runserver
```

Manual flows to verify:

- Admin and student login
- Student room booking and cancellation
- Admin bed/payment management
- Complaint uploads
- Announcement publishing
- Payment invoice PDF downloads
- JWT token creation and API access
- Realtime notification bell updates
- Console email output during development

## Deployment

### Render

Set `DEBUG=False`, a secure `SECRET_KEY`, and `ALLOWED_HOSTS` to your Render
hostname (for example, `your-service.onrender.com`). Leave `DATABASE_URL` empty
to keep the application's existing SQLite configuration.

Set the Render **Build Command** to:

```bash
pip install -r requirements.txt && python manage.py collectstatic --noinput
```

WhiteNoise serves the collected static files in production. Use the existing
ASGI start command for the service; no separate static-file service or route is
needed. Configure Redis via `REDIS_URL` only when multi-process websocket
delivery is required, and schedule `expire_unpaid_bookings` as appropriate.

## License

This project is intended for educational and internal deployment use unless a separate license is added.
