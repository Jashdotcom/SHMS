# Smart Hostel Management System (SHMS)

A full-stack Django-based hostel management platform designed to streamline student accommodation operations including room booking, bed allocation, payments, complaints, announcements, analytics, and real-time notifications.

🔗 **Live Demo:** https://shms-2kww.onrender.com
🔗 **GitHub Repository:** https://github.com/Jashdotcom/SHMS

---

# Features

## Student Features

* Student registration and authentication
* Room booking with real-time bed availability
* QR code generation for bookings
* Complaint submission and tracking
* Service request management
* Payment status tracking
* Real-time notification updates

## Admin Features

* Room and bed management
* Student management
* Booking approval and cancellation
* Payment management and invoice generation
* Complaint and service request handling
* Announcement publishing
* Analytics dashboard with occupancy/payment insights

---

# Key Features Implemented

* JWT Authentication
* Role-Based Access Control
* Real-Time WebSocket Notifications
* PDF Invoice Generation
* PostgreSQL Production Deployment
* REST APIs using Django REST Framework
* Responsive UI Design
* Automated Integration Testing
* QR Code Booking System
* Chart.js Analytics Dashboard

---

# Tech Stack

## Backend

* Python 3.14
* Django 6
* Django REST Framework
* Django Channels
* Simple JWT

## Frontend

* HTML5
* CSS3
* Bootstrap 5
* JavaScript
* Chart.js

## Database

* PostgreSQL
* SQLite (Development)

## Deployment & Tools

* Render
* Daphne
* Git & GitHub
* ReportLab
* OpenPyXL

---

# Project Screenshots

> Add screenshots here:

* Login Page:
  <img width="1917" height="867" alt="image" src="https://github.com/user-attachments/assets/4019ca9e-b54c-4922-a33f-ac2ac6ea7ed7" />

* Student Dashboard:
  <img width="1901" height="866" alt="image" src="https://github.com/user-attachments/assets/c22082a9-b3a0-4930-a310-29157dcdafd2" />

* Admin Dashboard:
  <img width="1897" height="867" alt="image" src="https://github.com/user-attachments/assets/621a3f65-846b-4418-ab1b-6833c0f369ab" />

* Booking System:
  <img width="1917" height="867" alt="image" src="https://github.com/user-attachments/assets/7e240ace-fcdf-481c-9675-5ed42e53f81d" />

* Analytics Dashboard:
  <img width="1902" height="867" alt="image" src="https://github.com/user-attachments/assets/d74706df-bc17-4178-b9e7-e7e6d7702dbc" />
  



---

# Installation & Setup

## Clone Repository

```bash
git clone https://github.com/Jashdotcom/SHMS.git
cd SHMS
```

## Create Virtual Environment

### Windows

```bash
python -m venv .venv
.venv\Scripts\activate
```

### Linux / macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
```

## Install Dependencies

```bash
pip install -r requirements.txt
```

## Configure Environment Variables

Create a `.env` file using `.env.example`.

Example:

```env
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

DATABASE_URL=
REDIS_URL=

EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
DEFAULT_FROM_EMAIL=no-reply@shms.local

BOOKING_EXPIRY_HOURS=24
```

---

# Database Setup

```bash
python manage.py migrate
python manage.py createsuperuser
```

---

# Run Development Server

```bash
python manage.py runserver
```

Open:

```text
http://127.0.0.1:8000/
```

---

# REST API

Base URL:

```text
/api/
```

## JWT Authentication

### Obtain Token

```http
POST /api/token/
```

### Refresh Token

```http
POST /api/token/refresh/
```

## Example Endpoints

* `GET /api/bookings/`
* `POST /api/bookings/`
* `GET /api/rooms/`
* `GET /api/payments/`
* `GET /api/announcements/`
* `GET /api/services/`

Example request:

```bash
curl -X POST http://127.0.0.1:8000/api/token/ \
-H "Content-Type: application/json" \
-d "{\"username\":\"admin\",\"password\":\"your-password\"}"
```

---

# Real-Time Notifications

SHMS uses Django Channels and WebSockets for:

* live notification updates
* announcement alerts
* booking notifications

Development mode uses in-memory channels.
Production deployment supports Redis-backed channels.

---

# Booking Expiry System

Automatically expire unpaid bookings:

```bash
python manage.py expire_unpaid_bookings
```

Can be scheduled using:

* cron jobs
* Task Scheduler
* hosting provider schedulers

---

# Verification Checklist

## Authentication

* Admin login
* Student login
* JWT token creation

## Booking System

* Room booking
* Booking cancellation
* QR generation

## Payments

* Payment updates
* Invoice PDF generation

## Complaints & Services

* Complaint uploads
* Service requests

## Notifications

* WebSocket notifications
* Announcement alerts

---

# Deployment

SHMS is deployed on Render using:

* PostgreSQL
* Daphne ASGI server
* Django Channels

## Production Configuration

Set:

```env
DEBUG=False
```

Configure:

* SECRET_KEY
* ALLOWED_HOSTS
* DATABASE_URL
* REDIS_URL
* Production email settings

## Collect Static Files

```bash
python manage.py collectstatic
```

---

# Project Status

Active development — deployed and production-ready for demonstration and portfolio purposes.

---

# Author

## Jash Mistry

* GitHub: https://github.com/Jashdotcom
* Project: SHMS (Smart Hostel Management System)

* > Note: The demo is hosted on Render free tier and may take 30–60 seconds to wake up after inactivity.
