from flask import Flask, render_template, Response, jsonify, request
import cv2
import numpy as np
import face_recognition as face_rec
import os
import threading
import pandas as pd
from datetime import datetime

app = Flask(__name__)

face_detection_enabled = False

base_path = 'images'
if not os.path.exists(base_path):
    os.makedirs(base_path)

studentImg = []
studentName = []

for student_folder in os.listdir(base_path):
    student_folder_path = os.path.join(base_path, student_folder)
    if os.path.isdir(student_folder_path):
        for img_file in os.listdir(student_folder_path):
            if img_file.endswith('.jpg'):
                currentImg = cv2.imread(os.path.join(student_folder_path, img_file))
                studentImg.append(currentImg)
                name = os.path.splitext(img_file)[0].rsplit('_', 1)[0]
                studentName.append(name)


def findEncoding(images):
    encoding_list = []
    for img in images:
        img = cv2.resize(img, (0, 0), None, 0.25, 0.25)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encodeimg = face_rec.face_encodings(img)
        if encodeimg:
            encoding_list.append(encodeimg[0])
    return encoding_list


encode_list = findEncoding(studentImg)

vid = cv2.VideoCapture(0)

def record_attendance(name):
    file_name = "attendance.xlsx"
    now = datetime.now()
    date_today = now.strftime("%Y-%m-%d")

    # Check if the file exists
    if os.path.exists(file_name):
        df = pd.read_excel(file_name)
    else:
        df = pd.DataFrame(columns=["Name", "Date"])

    # Prevent duplicate entries for the same person on the same day
    if not ((df["Name"] == name) & (df["Date"] == date_today)).any():
        new_entry = pd.DataFrame({"Name": [name], "Date": [date_today]})
        df = pd.concat([df, new_entry], ignore_index=True)
        df.to_excel(file_name, index=False)
        print(f"Attendance recorded: {name} on {date_today}")

def generate_frames():  #compares camera and folder images if matches
    global face_detection_enabled

    while True:
        success, frame = vid.read()
        if not success:
            break

        frame = cv2.flip(frame, 1)  # Flip the frame for a mirrored effect

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
                    name = studentName[best_match_index].upper()  # Display only studentName (without number)
                    record_attendance(name)
                    y1, x2, y2, x1 = face_loc
                    y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4  # Scale back to original size

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


@app.route('/register_student', methods=['POST'])
def register_student_api():
    global face_detection_enabled, vid

    data = request.json
    id_number = data.get("idNumber", "").strip()
    student_name = data.get("studentName", "").strip()

    if not id_number or not student_name:
        return jsonify({"message": "Missing Student ID or Name!"}), 400

    into_student_folder = os.path.join(base_path, f"{student_name}_{id_number}")
    if not os.path.exists(into_student_folder):
        os.makedirs(into_student_folder)

    face_detection_enabled = True
    count = 0

    while count < 100:
        success, frame = vid.read()
        if not success:
            return jsonify({"message": "Camera error!"}), 500

        frame = cv2.flip(frame, 1)

        faces = face_rec.face_locations(frame)
        if faces:
            filename = os.path.join(into_student_folder, f"{student_name}_{id_number}_{count}.jpg")
            cv2.imwrite(filename, frame)
            count += 1
            print(f"Captured {count}/100 images for {student_name} ({id_number})")

        cv2.waitKey(10)

        if  0xFF == ord('q'):
            break

    face_detection_enabled = False
    print(f"Registration complete for {student_name} ({id_number})!")

    # Release and reinitialize the camera
    vid.release()
    cv2.destroyAllWindows()
    vid = cv2.VideoCapture(0)  # Reopen camera

    return jsonify({"message": f"Registration successful for {student_name} ({id_number})!"})


@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    app.run(debug=True)
