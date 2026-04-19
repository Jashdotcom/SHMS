# 🏨 Smart Hostel Management System (SHMS)

A web-based application to simplify and automate hostel operations such as **room booking, payment tracking, and service management** with role-based access for **students and administrators**.


# 🚀 Features 

 ## 👨‍🎓 Student

* View available rooms & beds
* Book rooms with real-time bed availability
* View booking history
* Cancel bookings
* View payment status (Paid / Unpaid / Partial)
* Download payment receipt in **PDF format**
* Raise service/complaint requests

---

 ## 👨‍💼 Admin

* Manage rooms and bed capacity
* Track bookings with filters (Today / Tomorrow / Date)
* Update payment status
* Download payment receipts
* Manage service & complaint requests
* Role-based UI (restricted access to student features)

---

## 🧠 Key Highlights

* ✅ Dynamic bed allocation based on availability
* ✅ Role-based access control (Admin vs Student)
* ✅ PDF receipt generation using ReportLab
* ✅ Real-time booking and payment tracking
* ✅ Clean and user-friendly interface

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
```

2. Create virtual environment:

```bash
python -m venv venv
```

3. Activate virtual environment:

```bash
venv\Scripts\activate   # Windows
```

4. Install dependencies:

```bash
pip install -r requirements.txt
```

5. Apply migrations:

```bash
python manage.py migrate
```

6. Run server:

```bash
python manage.py runserver
```

7. Open in browser:

```
http://127.0.0.1:8000/
```

---

## 🔐 Roles & Access

| Feature          | Student | Admin |
| ---------------- | ------- | ----- |
| Book Room        | ✅       | ❌     |
| View Bookings    | ❌       | ✅     |
| Download Receipt | ✅       | ✅     |
| Update Payments  | ❌       | ✅     |
| Manage Services  | ❌       | ✅     |

---

## 📄 PDF Receipt Feature

* Students can download payment receipts
* Admin can also download receipts
* Includes:

  * Student details
  * Amount paid (₹)
  * Late fee
  * Payment status

---

## 🔮 Future Enhancements

* Online payment gateway integration
* Mobile application
* Email/SMS notifications
* Analytics dashboard

---

## 👨‍💻 Author

**Jash Mistry**
GitHub: https://github.com/Jashdotcom

---

## ⭐ Acknowledgement

This project was developed as part of academic learning to demonstrate real-world hostel management automation.

---

## 📌 License

This project is for educational purposes only.
