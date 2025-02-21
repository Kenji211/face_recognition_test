import cv2
import numpy as np
import face_recognition as face_rec
import os
import pandas as pd
from datetime import datetime

# Resize function to reduce image size
def resize(img, size):
    width = int(img.shape[1] * size)
    height = int(img.shape[0] * size)
    dimension = (width, height)
    return cv2.resize(img, dimension, interpolation=cv2.INTER_AREA)

# Folder path for images
base_path = 'images'
if not os.path.exists(base_path):
    os.makedirs(base_path)

# Load existing images
studentImg = []
studentName = []

# Scan all student folders and images
for student_folder in os.listdir(base_path):
    student_folder_path = os.path.join(base_path, student_folder)
    if os.path.isdir(student_folder_path):
        for img_file in os.listdir(student_folder_path):
            if img_file.endswith('.jpg'):
                currentImg = cv2.imread(os.path.join(student_folder_path, img_file))
                studentImg.append(currentImg)

                # Extract student name without "_number"
                name = os.path.splitext(img_file)[0].rsplit('_', 1)[0]
                studentName.append(name)

# Function to encode faces
def findEncoding(images):
    encoding_list = []
    for img in images:
        img = resize(img, 0.3)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encodeimg = face_rec.face_encodings(img)
        if encodeimg:  # Ensure face is detected before appending
            encoding_list.append(encodeimg[0])
    return encoding_list

encode_list = findEncoding(studentImg)

# Initialize webcam
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


# Function to register a new student
def register_student():
    name = input("Enter student's name: ").strip()
    if not name:
        print("Invalid name! Try again.")
        return

    student_folder = os.path.join(base_path, name)
    if not os.path.exists(student_folder):
        os.makedirs(student_folder)

    count = 0
    while count < 50:
        success, frame = vid.read()
        if not success:
            print("Failed to capture image.")
            continue

        faces = face_rec.face_locations(frame)
        if faces:
            filename = os.path.join(student_folder, f"{name}_{count}.jpg")
            cv2.imwrite(filename, frame)
            count += 1
            print(f"Captured {count}/50 images for {name}")

        cv2.imshow("Registering...", frame)
        key = cv2.waitKey(1)  # This allows OpenCV to update the window
        if key == ord('q'):
            break

    print(f"Registration complete for {name}!")
    global studentImg, studentName, encode_list
    studentImg, studentName = [], []

    # Reload images
    for student_folder in os.listdir(base_path):
        student_folder_path = os.path.join(base_path, student_folder)
        if os.path.isdir(student_folder_path):
            for img_file in os.listdir(student_folder_path):
                if img_file.endswith('.jpg'):
                    currentImg = cv2.imread(os.path.join(student_folder_path, img_file))
                    studentImg.append(currentImg)
                    name = os.path.splitext(img_file)[0].rsplit('_', 1)[0]
                    studentName.append(name)

    encode_list = findEncoding(studentImg)

# Face Recognition Mode
def face_recognition_mode():
    while True:
        success, frame = vid.read()
        if not success:
            break

        frames = cv2.resize(frame, (0, 0), None, 0.25, 0.25)
        frames = cv2.cvtColor(frames, cv2.COLOR_BGR2RGB)

        face_in_frame = face_rec.face_locations(frames)
        encode_in_frame = face_rec.face_encodings(frames, face_in_frame)

        for encodeFace, faceloc in zip(encode_in_frame, face_in_frame):
            matches = face_rec.compare_faces(encode_list, encodeFace)
            facedis = face_rec.face_distance(encode_list, encodeFace)
            matchIndex = np.argmin(facedis) if len(facedis) > 0 else None

            if matchIndex is not None and matches[matchIndex]:
                name = studentName[matchIndex].upper()  # Display only studentName (without number)
                record_attendance(name)
                y1, x2, y2, x1 = faceloc
                y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)
                cv2.rectangle(frame, (x1, y2 - 25), (x2, y2), (255, 0, 0), cv2.FILLED)
                cv2.putText(frame, name, (x1 + 6, y2 - 6), cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 2)

        cv2.imshow("Face Recognition", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

# Main menu
while True:
    print("\n1. Register New Student")
    print("2. Face Recognition Mode")
    print("3. Exit")
    choice = input("Enter your choice: ")

    if choice == "1":
        register_student()
    elif choice == "2":
        face_recognition_mode()
    elif choice == "3":
        break
    else:
        print("Invalid choice. Try again.")

vid.release()
cv2.destroyAllWindows()
