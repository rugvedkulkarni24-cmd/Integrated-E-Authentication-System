# 🔐 Integrated E-Authentication System

A **secure multi-factor authentication web application** that combines **Email & Password**, **Email-based OTP (2FA)**, and **Biometric Face Recognition** to provide a strong and modern authentication solution.

This project is developed as **Mini Project – I** for **Third Year in B.tech Computer Engineering (DBATU University)** and focuses on real-world security challenges and practical implementation.

---

## 🚀 Features

* ✅ Secure user registration & login
* 🔑 Password hashing for credential security
* ✉️ Email-based **One-Time Password (OTP)** with expiration
* 🧠 **Face Recognition authentication** using OpenCV
* 🔐 Multi-Factor Authentication (MFA)
* 🏗️ Three-tier architecture (Frontend, Backend, Database)
* 👨‍💻 Admin dashboard for user management
* ⚡ Fast & user-friendly UI

---

## 🔄 Authentication Flow

1. **User Registration**

   * Name, Email & Password
   * Face enrollment using webcam (multiple samples)

2. **Login Process**

   * Email & password verification
   * OTP sent to registered email (valid for 5 minutes)
   * Live face verification via webcam

3. **Access Granted**

   * User redirected to secure dashboard

---

## 🛠️ Tech Stack

### Languages

* **Python** – Backend & face recognition
* **JavaScript** – Client-side camera & API calls
* **HTML5 & CSS3** – User Interface
* **SQL** – Database

### Frameworks & Libraries

* **Flask** – Backend web framework
* **OpenCV** – Face detection & recognition
* **NumPy** – Numerical processing
* **MySQL Connector** – Database connectivity
* **SMTP (Gmail)** – OTP email service
* **Bootstrap 5** – Responsive UI

---

## 🧩 Security Concepts Implemented

* Cryptographic password hashing
* Multi-Factor Authentication (MFA)
* Time-bound OTP validation
* Biometric authentication (Face Recognition)
* Session-based access control

---

## 🏗️ System Architecture

* **Presentation Layer**: HTML, CSS, Bootstrap, JavaScript, WebRTC
* **Application Layer**: Flask, authentication logic, OTP & face verification
* **Data Layer**: MySQL database

---

## 📊 Results & Performance

* 🎯 Face Recognition Accuracy: **~95%**
* ⏱️ Average biometric verification time: **~1.5 seconds**
* 🔐 Strong resistance to brute-force & credential stuffing attacks

---

## 📁 Project Structure

```
Integrated-E-Authentication-System/
│
├── app.py
├── requirements.txt
├── recognizer.yml
├── face_dataset/
├── static/
│   └── style.css
├── templates/
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   ├── otp.html
│   ├── face_register.html
│   ├── face_verify.html
│   ├── dashboard.html
│   └── admin_dashboard.html
└── README.md
```

---

## ▶️ How to Run the Project

1. Clone the repository

```bash
git clone https://github.com/your-username/Integrated-E-Authentication-System.git
cd Integrated-E-Authentication-System
```

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Configure database & email credentials in `app.py`

4. Run the application

```bash
python app.py
```

5. Open browser and visit

```
http://127.0.0.1:5000
```

---

## 🔮 Future Enhancements

* Liveness detection (blink / head movement)
* Passwordless authentication (FIDO2 / WebAuthn)
* Risk-based adaptive authentication
* Mobile application integration

---

## 👨‍🎓 Academic Details

* **Project Type**: Mini Project – I
* **Course**: B.E. Computer Engineering
* **University**: Dr. Babasaheb Ambedkar Technological University (DBATU)
* **Academic Year**: 2025–26

---

## 👥 Contributors

* **Rugved R. Kulkarni**
* Rohit V. Jadhav
* Mohammad Aayan S. Kalangade

---

⭐ If you like this project, don’t forget to **star** the repository!
