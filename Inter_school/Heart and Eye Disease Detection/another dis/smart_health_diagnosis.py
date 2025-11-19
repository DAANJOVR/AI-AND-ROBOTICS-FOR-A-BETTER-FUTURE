import cv2
import joblib
import numpy as np
import tkinter as tk
from tkinter import messagebox
from threading import Thread
import os


# --- Helper function to find model/cascade files ---
def find_resource(filename):
    """Checks current directory and common cascade paths for files."""
    if os.path.exists(filename):
        return filename

    # Try finding the Haar cascade path if the user only has the filename
    if 'haarcascade_eye.xml' in filename:
        try:
            return cv2.data.haarcascades + filename
        except AttributeError:
            # Fallback if cv2.data is not available
            pass
    return filename


# Load trained heart model
# NOTE: Ensure 'heart_model.pkl' is in the same directory as this script.
try:
    model = joblib.load(find_resource("heart_model.pkl"))
except FileNotFoundError:
    print("WARNING: heart_model.pkl not found. Heart prediction will fail.")
    model = None


# ---------------- HEART DISEASE PREDICTION ----------------
def predict_heart():
    if model is None:
        messagebox.showerror("Error", "Heart model file (heart_model.pkl) not found. Cannot predict.")
        result_label.config(text="Model Missing", fg="red")
        return

    try:
        # Access entries using the global variables created in the UI section
        age = float(entry_age.get())
        sex = 1 if entry_sex.get().lower() == 'm' else 0
        trestbps = float(entry_bp.get())
        chol = float(entry_chol.get())
        fbs = int(entry_fbs.get())
        thalach = float(entry_thalach.get())
        exang = int(entry_exang.get())
        oldpeak = float(entry_oldpeak.get())

        # NOTE: Feature array structure MUST match the model's training data.
        features = np.array([[age, sex, 0, trestbps, chol, fbs, 0, thalach, exang, oldpeak, 0, 0, 0]])
        prediction = model.predict_proba(features)[0][1] * 100

        result_label.config(text=f"Heart Disease Probability: {prediction:.1f}%", fg="yellow")
    except Exception as e:
        messagebox.showerror("Input Error", f"Please check your inputs!\n\n{e}")


# ---------------- EYE DISEASE DETECTION ----------------
def start_eye_detection():
    def detect_eyes():
        cascade_path = find_resource('haarcascade_eye.xml')
        eye_cascade = cv2.CascadeClassifier(cascade_path)

        if eye_cascade.empty():
            print(f"ERROR: Could not load eye cascade classifier from {cascade_path}")
            return

        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("ERROR: Could not open video stream/camera.")
            return

        # --- Color Threshold Definitions (HSV) ---
        lower_red_1 = np.array([0, 100, 100])
        upper_red_1 = np.array([10, 255, 255])
        lower_red_2 = np.array([160, 100, 100])
        upper_red_2 = np.array([180, 255, 255])
        lower_yellow = np.array([20, 100, 100])
        upper_yellow = np.array([30, 255, 255])

        # --- Detection Constants ---
        COLOR_THRESHOLD_PERCENT = 0.05
        NORMAL_PUPIL_RADIUS_MIN = 8
        NORMAL_PUPIL_RADIUS_MAX = 20

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            eyes = eye_cascade.detectMultiScale(gray, 1.3, 5)

            # --- Eye Analysis Flags ---
            is_red_eye_detected = False
            is_yellow_eye_detected = False
            pupil_state = None  # Can be 'constricted', 'dilated', or None

            for (x, y, w, h) in eyes:
                eye_roi = frame[y:y + h, x:x + w]
                gray_roi = gray[y:y + h, x:x + w]

                if eye_roi.size == 0:
                    continue

                hsv_roi = cv2.cvtColor(eye_roi, cv2.COLOR_BGR2HSV)
                total_pixel_count = w * h

                # --- Red Eye Detection ---
                mask_red_1 = cv2.inRange(hsv_roi, lower_red_1, upper_red_1)
                mask_red_2 = cv2.inRange(hsv_roi, lower_red_2, upper_red_2)
                red_mask = mask_red_1 + mask_red_2
                red_pixel_count = np.sum(red_mask > 0)
                if total_pixel_count > 0 and (red_pixel_count / total_pixel_count) > COLOR_THRESHOLD_PERCENT:
                    is_red_eye_detected = True

                # --- Yellow Eye Detection (Jaundice) ---
                mask_yellow = cv2.inRange(hsv_roi, lower_yellow, upper_yellow)
                yellow_pixel_count = np.sum(mask_yellow > 0)
                if total_pixel_count > 0 and (yellow_pixel_count / total_pixel_count) > COLOR_THRESHOLD_PERCENT:
                    is_yellow_eye_detected = True

                # --- Pupil Size/Anomaly Detection ---
                pupil_state = None
                circles = cv2.HoughCircles(gray_roi, cv2.HOUGH_GRADIENT, 1, 20,
                                           param1=50, param2=30, minRadius=5, maxRadius=30)

                if circles is not None:
                    circles = np.uint16(np.around(circles))
                    for i in circles[0, :]:
                        pupil_radius = i[2]

                        if pupil_radius < NORMAL_PUPIL_RADIUS_MIN:
                            pupil_state = 'constricted'
                        elif pupil_radius > NORMAL_PUPIL_RADIUS_MAX:
                            pupil_state = 'dilated'

                        # Draw the detected pupil
                        cv2.circle(frame, (x + i[0], y + i[1]), i[2], (0, 255, 0), 2)
                        cv2.circle(frame, (x + i[0], y + i[1]), 2, (0, 0, 255), 3)
                        break

                        # --- Drawing Rectangles and Text based on individual detection ---
                display_color = (0, 255, 255)  # Default
                display_text = "Eye Detected"

                if is_red_eye_detected:
                    display_color = (0, 0, 255)  # Red
                    display_text = "Red Eye Detected"
                elif is_yellow_eye_detected:
                    display_color = (0, 255, 255)  # Yellow
                    display_text = "Yellow Eye Detected"

                    # Priority for Pupil State over generic 'Eye Detected' for the bounding box
                if pupil_state == 'dilated':
                    display_text += ", Dilated Pupil"
                    display_color = (255, 0, 255)  # Magenta
                elif pupil_state == 'constricted':
                    display_text += ", Constricted Pupil"
                    display_color = (255, 0, 255)  # Magenta

                cv2.rectangle(frame, (x, y), (x + w, y + h), display_color, 2)
                cv2.putText(frame, display_text, (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.6, display_color, 2)

            # --- Final Consolidated Health Status Message (FIXED PRIORITY) ---
            overall_health_status = "Looking for Eyes..."
            overall_color = (255, 255, 255)  # White

            if len(eyes) == 0:
                overall_health_status = "Looking for Eyes..."
                overall_color = (255, 255, 255)
            # 1. Prioritize Pupil State (Miosis/Mydriasis)
            elif pupil_state == 'dilated':
                overall_health_status = "⚠️ DILATED PUPIL DETECTED (Mydriasis)"
                overall_color = (255, 0, 255)  # Magenta
            elif pupil_state == 'constricted':
                overall_health_status = "⚠️ CONSTRICTED PUPIL DETECTED (Miosis)"
                overall_color = (255, 0, 255)  # Magenta
            # 2. Check for Color Anomalies
            elif is_red_eye_detected:
                overall_health_status = "⚠️ POSSIBLE RED EYE ISSUE"
                overall_color = (0, 0, 255)  # Red
            elif is_yellow_eye_detected:
                overall_health_status = "⚠️ POSSIBLE YELLOW EYE ISSUE (Jaundice)"
                overall_color = (0, 255, 255)  # Yellow
            # 3. Default Normal Status
            else:
                overall_health_status = "✅ Eye(s) Detected - Appears Normal"
                overall_color = (0, 255, 0)  # Green

            cv2.putText(frame, overall_health_status, (10, frame.shape[0] - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, overall_color, 2)

            cv2.imshow("Eye Disease Detection", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()

    Thread(target=detect_eyes, daemon=True).start()


# ---------------- UI ----------------
root = tk.Tk()
root.title("Smart Health Diagnosis System")
root.geometry("620x700")
root.configure(bg="#121212")

title = tk.Label(root, text="🧠 Smart Health Diagnosis System",
                 font=("Helvetica", 18, "bold"), fg="#00E5FF", bg="#121212")
title.pack(pady=10)

# --- HEART INPUT SECTION ---
frame = tk.Frame(root, bg="#1E1E1E", padx=15, pady=15, relief="groove", bd=2)
frame.pack(pady=10)

tk.Label(frame, text="Heart Health Prediction", font=("Helvetica", 14, "bold"), fg="white", bg="#1E1E1E").pack(pady=5)

fields = [
    ("Age:", "entry_age"),
    ("Sex (M/F):", "entry_sex"),
    ("Resting BP (mmHg):", "entry_bp"),
    ("Cholesterol (mg/dL):", "entry_chol"),
    ("Fasting Blood Sugar >120? (1/0):", "entry_fbs"),
    ("Max Heart Rate:", "entry_thalach"),
    ("Exercise Angina (1/0):", "entry_exang"),
    ("ST Depression:", "entry_oldpeak"),
]

entries = {}

# Create entries and assign them to globals
for label_text, var_name in fields:
    lbl = tk.Label(frame, text=label_text, fg="#A0A0A0", bg="#1E1E1E", font=("Segoe UI", 10, "bold"), anchor="w")
    lbl.pack(fill="x")
    ent = tk.Entry(frame, width=20, font=("Segoe UI", 10))
    ent.pack(pady=3)
    entries[var_name] = ent
    globals()[var_name] = ent

predict_btn = tk.Button(frame, text="Predict Heart Disease", command=predict_heart,
                        bg="#00E676", fg="black", font=("Segoe UI", 10, "bold"),
                        relief="flat", padx=10, pady=5)
predict_btn.pack(pady=10)

result_label = tk.Label(frame, text="", fg="white", bg="#1E1E1E", font=("Helvetica", 11, "bold"))
result_label.pack(pady=5)

# --- EYE SECTION ---
eye_btn = tk.Button(root, text="Start Eye Disease Detection", command=start_eye_detection,
                    bg="#2979FF", fg="white", font=("Segoe UI", 12, "bold"),
                    relief="flat", padx=20, pady=8)
eye_btn.pack(pady=20)

hint = tk.Label(root,
                text="Press 'Q' to close camera window\nDetection is for demonstration only and does not replace medical advice.",
                fg="#F44336", bg="#121212", font=("Segoe UI", 9, "bold"))
hint.pack()

root.mainloop()