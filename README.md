# 🏨 Smart Hostel Management System (SHMS)

A web-based application to simplify and automate hostel operations such as **room booking, payment tracking, service management, announcements, and reporting** with role-based access for **students and administrators**.

---

# 🚀 Features 

## 👨‍🎓 Student

* View available rooms & beds
* Book rooms with real-time bed availability
* View booking history
* Cancel bookings
* View payment status (Paid / Unpaid / Partial)
* Download payment receipt in **PDF format**
* Raise service/complaint requests
* View announcements from admin

---

## 👨‍💼 Admin

* Manage rooms and bed capacity
* Track bookings with filters (Today / Tomorrow / Date)
* Update payment status
* Download payment receipts
* Manage service & complaint requests
* Post announcements for students
* Export booking data in **Excel format**
* Role-based UI (restricted access to student features)

---

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

```bash
git clone https://github.com/Jashdotcom/SHMS.git
cd SHMS
