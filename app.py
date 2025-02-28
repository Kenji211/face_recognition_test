from flask import Flask, render_template, Response, jsonify, request
import cv2
import numpy as np
import face_recognition as face_rec
import os
import pandas as pd
from datetime import datetime

app = Flask(__name__)

# Global Variables
face_detection_enabled = False
base_path = 'images'

# Ensure images directory exists
if not os.path.exists(base_path):
    os.makedirs(base_path)

# Load student images and names
studentImg = []
studentName = []

for student_folder in os.listdir(base_path):
    student_folder_path = os.path.join(base_path, student_folder)
    if os.path.isdir(student_folder_path):
        for img_file in os.listdir(student_folder_path):
            if img_file.endswith('.jpg'):
                currentImg = cv2.imread(os.path.join(student_folder_path, img_file))
                studentImg.append(currentImg)
                studentName.append(student_folder)  # Store folder name (e.g., "John Doe_12345")


# Function to encode faces
def findEncoding(images):
    encoding_list = []
    for img in images:
        img = cv2.resize(img, (0, 0), None, 0.25, 0.25)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encodeimg = face_rec.face_encodings(img)
        if encodeimg:
            encoding_list.append(encodeimg[0])
    return encoding_list


# Generate encodings for stored images
encode_list = findEncoding(studentImg)

# Initialize camera
vid = cv2.VideoCapture(0)


# Function to extract name and ID from folder name
def extract_name_id(folder_name):
    try:
        name, student_id = folder_name.rsplit('_', 1)
        return name.strip(), student_id.strip()
    except ValueError:
        return folder_name, "Unknown"


# Function to record attendance
def record_attendance(folder_name):
    file_name = "attendance.xlsx"
    now = datetime.now()
    current_date = now.strftime("%Y-%m-%d")

    student_name, student_id = extract_name_id(folder_name)

    if os.path.exists(file_name):
        df = pd.read_excel(file_name, index_col=None)
    else:
        df = pd.DataFrame(columns=["Name", "Student ID"])

    # Ensure the current date column exists
    if current_date not in df.columns:
        df[current_date] = ""

    # Check if student already exists in the record
    mask = (df["Name"] == student_name) & (df["Student ID"] == student_id)

    if mask.any():
        # Mark attendance if not already marked
        if df.loc[mask, current_date].isnull().all():
            df.loc[mask, current_date] = "Present"
            print(f"✅ Attendance updated for {student_name} (ID: {student_id}) on {current_date}")
    else:
        # Add new student record
        new_entry = {
            "Name": student_name,
            "Student ID": student_id,
            current_date: "Present"
        }
        df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)
        print(f"✅ Attendance recorded for {student_name} (ID: {student_id}) on {current_date}")

    # Save back to Excel
    df.to_excel(file_name, index=False)


# Function to process camera frames and detect faces
def generate_frames():
    global face_detection_enabled

    while True:
        success, frame = vid.read()
        if not success:
            break

        frame = cv2.flip(frame, 1)  # Mirror effect

        if face_detection_enabled:
            small_frame = cv2.resize(frame, (0, 0), None, 0.25, 0.25)
            small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

            face_locations = face_rec.face_locations(small_frame)
            encode_faces = face_rec.face_encodings(small_frame, face_locations)

            for face_loc, encode_face in zip(face_locations, encode_faces):
                matches = face_rec.compare_faces(encode_list, encode_face)
                face_distances = face_rec.face_distance(encode_list, encode_face)
                best_match_index = np.argmin(face_distances) if len(face_distances) > 0 else None

                if best_match_index is not None and matches[best_match_index]:
                    folder_name = studentName[best_match_index]  # Folder name
                    record_attendance(folder_name)

                    # Draw rectangle around detected face
                    y1, x2, y2, x1 = face_loc
                    y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


# Toggle face detection
@app.route('/toggle_detection', methods=['POST'])
def toggle_detection():
    global face_detection_enabled
    face_detection_enabled = not face_detection_enabled
    return jsonify({"face_detection_enabled": face_detection_enabled})


# Routes
@app.route('/')
def index():
    return render_template('attendance.html')


@app.route('/register')
def register():
    return render_template('register.html')


@app.route('/disable_detection', methods=['POST'])
def disable_detection():
    global face_detection_enabled
    face_detection_enabled = False
    return jsonify({"face_detection_enabled": face_detection_enabled})


# Stream video feed
@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)
