from flask import Flask, render_template, request, redirect, flash, session, jsonify, url_for
import mysql.connector
import hashlib
import random
import smtplib
import os
import cv2
import numpy as np
import base64
import time

app = Flask(__name__)
app.secret_key = "replace_with_a_strong_secret"

# ---------------- DB config ----------------
DB_CONFIG = {
    "host": "127.0.0.1",
    "user": "root",
    "password": "root",
    "database": "eauth",
    "port": 3307
}

# ---------------- SMTP ----------------
SMTP_EMAIL = "Your_email@gmail.com"
SMTP_APP_PASSWORD = "your_app_password_here"
SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587

# ---------------- Face config ----------------
DATASET_DIR = "face_dataset"
RECOGNIZER_FILE = "recognizer.yml"
os.makedirs(DATASET_DIR, exist_ok=True)
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

recognizer = cv2.face.LBPHFaceRecognizer_create()

# ---------------- DB helper ----------------
def get_db():
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()
    return conn, cursor

# ---------------- OTP mailer ----------------
def send_otp(email, otp):
    try:
        subject = "Your OTP for E-Authentication"
        body = f"Hello,\n\nYour OTP is: {otp}\nThis OTP is valid for 5 minutes.\n\nThank you."
        message = f"Subject: {subject}\n\n{body}"
        server = smtplib.SMTP(SMTP_HOST, SMTP_PORT)
        server.starttls()
        server.login(SMTP_EMAIL, SMTP_APP_PASSWORD)
        server.sendmail(SMTP_EMAIL, email, message)
        server.quit()
        print(f"OTP sent successfully to {email}")
        return True
    except Exception as e:
        print("EMAIL ERROR:", e)
        return False

# ---------------- Train face model ----------------
def train_all_faces():
    files = [f for f in os.listdir(DATASET_DIR) if f.lower().endswith(".jpg")]
    faces, labels = [], []
    for f in sorted(files):
        img = cv2.imread(os.path.join(DATASET_DIR, f), cv2.IMREAD_GRAYSCALE)
        if img is None:
            continue
        parts = f.split("_")
        if len(parts) < 3:
            continue
        label = int(parts[1])
        faces.append(img)
        labels.append(label)
    if faces:
        recognizer.train(faces, np.array(labels))
        recognizer.save(RECOGNIZER_FILE)
        return True
    return False

# ---------------- API: capture face ----------------
@app.route("/api/capture_face/<int:user_id>", methods=["POST"])
def api_capture_face(user_id):
    payload = request.json
    if not payload or "image" not in payload:
        return jsonify({"error": "no_image"}), 400
    try:
        header, encoded = payload["image"].split(",", 1)
        img_bytes = base64.b64decode(encoded)
        nparr = np.frombuffer(img_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    except Exception:
        return jsonify({"error": "invalid_image"}), 400

    faces = face_cascade.detectMultiScale(gray, 1.3, 5)
    saved = 0
    existing = len([n for n in os.listdir(DATASET_DIR) if n.startswith(f"user_{user_id}_")])
    idx = existing
    for (x, y, w, h) in faces:
        idx += 1
        face_img = gray[y:y+h, x:x+w]
        cv2.imwrite(os.path.join(DATASET_DIR, f"user_{user_id}_{idx}.jpg"), face_img)
        saved += 1

    total = len([n for n in os.listdir(DATASET_DIR) if n.startswith(f"user_{user_id}_")])
    done = False
    if total >= 12:
        done = train_all_faces()
    return jsonify({"saved": saved, "total": total, "done": done})

# ---------------- API: verify face ----------------
@app.route("/api/verify_face/<int:user_id>", methods=["POST"])
def api_verify_face(user_id):
    if not os.path.exists(RECOGNIZER_FILE):
        return jsonify({"recognized": False, "reason": "no_model"})
    payload = request.json
    if not payload or "image" not in payload:
        return jsonify({"recognized": False, "reason": "no_data"})
    try:
        header, encoded = payload["image"].split(",", 1)
        img_bytes = base64.b64decode(encoded)
        nparr = np.frombuffer(img_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)
    except Exception:
        return jsonify({"recognized": False, "reason": "invalid_image"})

    faces = face_cascade.detectMultiScale(img, 1.2, 5)
    if len(faces) == 0:
        return jsonify({"recognized": False, "reason": "no_face"})

    recognizer.read(RECOGNIZER_FILE)
    for (x, y, w, h) in faces:
        roi = img[y:y+h, x:x+w]
        label, conf = recognizer.predict(roi)
        if label == user_id and conf < 65:
            session["user_id"] = user_id
            return jsonify({"recognized": True, "conf": float(conf)})
        else:
            return jsonify({"recognized": False, "conf": float(conf), "label": int(label)})
    return jsonify({"recognized": False})

# ---------------- Pages ----------------
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/register", methods=["GET","POST"])
def register():
    if request.method=="POST":
        name = request.form.get("name","").strip()
        email = request.form.get("email","").strip().lower()
        password = request.form.get("password","")
        if not name or not email or not password:
            flash("All fields are required","danger")
            return redirect(url_for("register"))
        pwd_hash = hashlib.sha256(password.encode()).hexdigest()
        conn, cursor = get_db()
        try:
            cursor.execute("INSERT INTO users (name,email,password_hash) VALUES (%s,%s,%s)", (name,email,pwd_hash))
            conn.commit()
            cursor.execute("SELECT id FROM users WHERE email=%s", (email,))
            user_id = cursor.fetchone()[0]
            flash("Registered successfully! Proceed to face registration.","success")
            return redirect(url_for("face_register", user_id=user_id))
        except mysql.connector.IntegrityError:
            flash("Email already registered","danger")
            return redirect(url_for("register"))
        finally:
            cursor.close()
            conn.close()
    return render_template("register.html")

@app.route("/face_register/<int:user_id>")
def face_register(user_id):
    return render_template("face_register.html", user_id=user_id)

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method=="POST":
        email = request.form.get("email","").strip().lower()
        password = request.form.get("password","")
        pwd_hash = hashlib.sha256(password.encode()).hexdigest()
        conn, cursor = get_db()
        cursor.execute("SELECT id FROM users WHERE email=%s AND password_hash=%s",(email,pwd_hash))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        if not user:
            flash("Invalid email or password","danger")
            return redirect(url_for("login"))

        otp = str(random.randint(100000,999999))
        session["otp"] = otp
        session["otp_time"] = time.time()
        session["pending_user_id"] = user[0]
        session["email"] = email
        send_otp(email, otp)
        flash("OTP sent to your email (5 min validity)","info")
        return redirect(url_for("otp"))
    return render_template("login.html")

@app.route("/otp", methods=["GET","POST"])
def otp():
    if "otp" not in session:
        flash("Session expired. Login again","danger")
        return redirect(url_for("login"))
    if request.method=="POST":
        if "submit_otp" in request.form:
            entered = request.form.get("otp","")
            if entered == session.get("otp") and time.time()-session.get("otp_time",0)<300:
                flash("OTP verified! Proceed to face verification","success")
                return redirect(url_for("face_verify", user_id=session["pending_user_id"]))
            else:
                flash("Invalid or expired OTP","danger")
        elif "resend_otp" in request.form:
            otp = str(random.randint(100000,999999))
            session["otp"] = otp
            session["otp_time"] = time.time()
            send_otp(session.get("email"), otp)
            flash("New OTP sent!","info")
    return render_template("otp.html")

@app.route("/face_verify/<int:user_id>")
def face_verify(user_id):
    return render_template("face_verify.html", user_id=user_id)

@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        flash("Login required","danger")
        return redirect(url_for("login"))
    user_id = session["user_id"]
    conn, cursor = get_db()
    cursor.execute("SELECT name,email,created_at FROM users WHERE id=%s",(user_id,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    return render_template("dashboard.html", user=user)

@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out","info")
    return redirect(url_for("index"))

# ---------------- Admin ----------------
@app.route("/admin_login", methods=["GET","POST"])
def admin_login():
    if request.method=="POST":
        username = request.form.get("username","").strip()
        password = request.form.get("password","").strip()
        if username=="admin" and password=="root":
            session["admin_id"] = 1
            flash("Admin logged in","success")
            return redirect(url_for("admin_dashboard"))
        flash("Invalid credentials","danger")
    return render_template("admin_login.html")

@app.route("/admin_dashboard")
def admin_dashboard():
    if "admin_id" not in session:
        return redirect(url_for("admin_login"))
    conn, cursor = get_db()
    cursor.execute("SELECT id,name,email,created_at FROM users")
    users = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template("admin_dashboard.html", users=users)

@app.route("/delete_user/<int:user_id>", methods=["POST","GET"])
def delete_user(user_id):
    if "admin_id" not in session:
        return redirect(url_for("admin_login"))
    for f in os.listdir(DATASET_DIR):
        if f.startswith(f"user_{user_id}_"):
            try:
                os.remove(os.path.join(DATASET_DIR, f))
            except: pass
    conn, cursor = get_db()
    cursor.execute("DELETE FROM users WHERE id=%s",(user_id,))
    conn.commit()
    cursor.close()
    conn.close()
    train_all_faces()
    flash("User deleted and model updated","success")
    return redirect(url_for("admin_dashboard"))

# ---------------- Run ----------------
if __name__=="__main__":
    app.run(debug=True)
