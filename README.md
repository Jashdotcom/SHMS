# Smart Hostel Management System (SHMS)

<<<<<<< HEAD
A web-based application to simplify and automate hostel operations such as **room booking, payment tracking, service management, announcements, and reporting** with role-based access for **students and administrators**.

---

#  Features 

## 👨‍🎓 Student

* View available rooms & beds
* Book rooms with real-time bed availability
* View booking history
* Cancel bookings
* View payment status (Paid / Unpaid / Partial)
* Download payment receipt in **PDF format**
* Raise service/complaint requests
* View announcements from admin
=======
SHMS is a Django-based hostel management platform for student bookings, bed allocation, payments, complaints, announcements, service requests, analytics, invoices, and API access.

## Highlights

- Role-based access for students and administrators
- Booking workflow with QR codes and automatic expiry handling
- Payment tracking with late fees and professional PDF invoices
- Complaint and service request management with file uploads
- Analytics dashboard with Chart.js and date filters
- Email notifications and real-time in-app notifications
- Django REST Framework API with JWT authentication
- Deployment-ready settings with `.env` support and PostgreSQL compatibility

## Tech Stack

- Django 6
- Python 3.14
- SQLite for development
- PostgreSQL for production
- Bootstrap 5
- Chart.js
- Django REST Framework
- Django Channels
- ReportLab
- OpenPyXL
>>>>>>> 8c3ff29 (implement new features)

## Screenshots

<<<<<<< HEAD
## 👨‍💼 Admin

* Manage rooms and bed capacity
* Track bookings with filters (Today / Tomorrow / Date)
* Update payment status
* Download payment receipts
* Manage service & complaint requests
* Post announcements for students
* Export booking data in **Excel format**
* Role-based UI (restricted access to student features)
=======
Add screenshots here after capturing the upgraded UI:

- Dashboard analytics
- Booking form and QR code
- Booking history filters
- Payments and invoice PDF
- Complaints with uploads
- Service request management
>>>>>>> 8c3ff29 (implement new features)

## Installation

<<<<<<< HEAD
## 🧠 Key Highlights

* ✅ Dynamic bed allocation based on availability
* ✅ Role-based access control (Admin vs Student)
* ✅ PDF receipt generation using ReportLab
* ✅ Excel export for booking reports (admin only)
* ✅ Announcement system for communication
* ✅ Clean and user-friendly interface
* ✅ Accurate booking records (no duplicate entries)

---

## 📢 Announcement System

* Admin can:
  * Create announcements (e.g., maintenance, notices)
  * Update or delete announcements
* Students can:
  * View announcements on dashboard

---

## 📊 Excel Export Feature

* Admin can download all booking data in **Excel (.xlsx)** format
* Includes:
  * Student Name
  * Booked On
  * Room Number
  * Bed Number
  * From Date
  * To Date
  * Status
* Features:
  * Auto-adjusted column width
  * Proper date formatting
  * Clean and readable layout
  * No duplicate entries

---

## 💳 Payment System

* This project uses a **simulated (dummy) payment system**
* No real payment gateway or QR-based transactions are implemented
* Payment statuses are handled manually:

  * Paid
  * Unpaid
  * Partial

* Admin updates payment status
* Students can view status and download receipts

> ⚠️ Note: This system is for academic/demo purposes and does not process real payments.

---

## 🛠️ Tech Stack

* **Frontend:** HTML, CSS, JavaScript
* **Backend:** Django (Python)
* **Database:** SQLite
* **PDF Generation:** ReportLab
* **Excel Export:** OpenPyXL

---

## 📸 Screenshots

### 🛏️ Room Booking
![Room Booking](https://github.com/user-attachments/assets/aa737466-9c73-4401-bd5d-185bda16ce3e)

### 📋 Booking History
![Booking History](https://github.com/user-attachments/assets/d9cc8ee7-88e3-4fbe-a80b-1798b0d96ec3)

### 💳 Payments
![Payments](https://github.com/user-attachments/assets/2b45c0bf-7e74-4a1a-8c1b-a6eaa5a04dd4)

### 🧾 Receipt
![Receipt](https://github.com/user-attachments/assets/65521260-847a-45f0-a0af-4952c4116719)

---

## ⚙️ Installation & Setup

1. Clone the repository:
=======
1. Clone the repository.
>>>>>>> 8c3ff29 (implement new features)

'bash
git clone https://github.com/Jashdotcom/SHMS.git
cd SHMS

<<<<<<< HEAD
2. Create virtual environment:
   python -m venv venv

3. Activate virtual environment:
   venv\Scripts\activate   # Windows

4. Install dependencies:
   pip install -r requirements.txt
=======
2. Create and activate a virtual environment.

```bash
python -m venv venv
venv\Scripts\activate
```

3. Install dependencies.
>>>>>>> 8c3ff29 (implement new features)

6. Apply migrations:
   python manage.py migrate
   
7. Run server:
   python manage.py runserver

<<<<<<< HEAD
8. Open in browser:
   http://127.0.0.1:8000/
=======
4. Create the environment file.

```bash
copy .env.example .env
```

5. Apply migrations.

```bash
python manage.py migrate
```

6. Create a superuser.

```bash
python manage.py createsuperuser
```

7. Run the development server.

```bash
python manage.py runserver
```

## Environment Variables

Use these values in `.env`:

```env
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=
REDIS_URL=
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_USE_SSL=False
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=
DEFAULT_FROM_EMAIL=no-reply@shms.local
BOOKING_EXPIRY_HOURS=24
```

## API Documentation

Base path: `/api/`

Authentication endpoints:

- `POST /api/token/`
- `POST /api/token/refresh/`

Core resources:

- `GET /api/bookings/`
- `POST /api/bookings/`
- `GET /api/rooms/`
- `GET /api/payments/`
- `POST /api/payments/`
- `GET /api/announcements/`
- `POST /api/announcements/`
- `GET /api/services/`
- `POST /api/services/`

Example JWT request:

```bash
curl -X POST http://127.0.0.1:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"admin\",\"password\":\"your-password\"}"
```

## Booking Expiry Command

Expire unpaid bookings manually with:

```bash
python manage.py expire_unpaid_bookings
```

Schedule it with Windows Task Scheduler, cron, or a hosted scheduler.

## Testing

Run the built-in Django check:

```bash
python manage.py check
```

Suggested manual verification:

- Create a booking and verify QR generation
- Update a payment and confirm the invoice PDF changes
- Post an announcement and verify email and notification delivery
- Submit a complaint with image and attachment uploads
- Run `expire_unpaid_bookings` and verify room/bed availability is restored

## Deployment

1. Set `DEBUG=False`.
2. Configure `SECRET_KEY`, `ALLOWED_HOSTS`, `DATABASE_URL`, and email settings.
3. Use PostgreSQL in production via `DATABASE_URL`.
4. Run migrations and collect static files.

```bash
python manage.py migrate
python manage.py collectstatic
```

5. Serve the app with a production WSGI/ASGI server such as Gunicorn, Uvicorn, or Daphne behind Nginx.
6. Configure static and media file serving.
7. Schedule the booking expiry command.
8. Verify email delivery, JWT authentication, and websocket access.

## Suggested Commit Messages

- `feat: add analytics dashboard and chart filters`
- `feat: add email notifications and reusable templates`
- `feat: add drf api with jwt auth`
- `feat: add websocket notifications and bell ui`
- `feat: add complaint and service attachment uploads`
- `feat: add invoice pdf generation and booking expiry command`
- `feat: harden settings for production deployment`
- `docs: rewrite README for production setup`

## License

This project is intended for educational and internal deployment use unless a separate license is added.
>>>>>>> 8c3ff29 (implement new features)
