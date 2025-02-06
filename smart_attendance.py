import numpy as np
from encodings.punycode import selective_find

import cv2
import numpy as npy
import face_recognition as face_rec
import os

def resize(img, size) :
    width = int(img.shape[1]*size)
    height = int(img.shape[0] * size)
    dimension = (width,height)
    return cv2.resize(img, dimension, interpolation=cv2.INTER_AREA)

path = 'images'
studentImg= []
studentName = []
myList = os.listdir(path)
# print(myList)

for cl in myList :
    currentImg = cv2.imread(f'{path}/{cl}')
    studentImg.append(currentImg)
    studentName.append(os.path.splitext(cl)[0])

# print(studentName)

def findEncoding(images) :
    encoding_list = []
    for img in images :
        img = resize(img, 0.3)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encodeimg = face_rec.face_encodings(img)[0]
        encoding_list.append(encodeimg)
    return encoding_list

encode_list = findEncoding(studentImg)

vid = cv2.VideoCapture(0)


while True :
    success, frame = vid.read()
    frames = cv2.resize(frame, (0,0) , None, 0.25, 0.25)
    frames = cv2.cvtColor(frames, cv2.COLOR_BGR2RGB)


    face_in_frame = face_rec.face_locations(frames)
    encode_in_frame = face_rec.face_encodings(frames, face_in_frame)

    for encodeFace, faceloc in zip(encode_in_frame, face_in_frame) :
        matches = face_rec.compare_faces(encode_list, encodeFace)
        facedis = face_rec.face_distance(encode_list, encodeFace)
        print(facedis)
        matchIndex = np.argmin(facedis)

        if matches[matchIndex] :
            name = studentName[matchIndex].upper()
            y1, x2, y2, x1 = faceloc
            y1, x2, y2, x1 = y1*4, x2*4, y2*4, x1*4
            cv2.rectangle(frame,(x1,y1), (x2,y2), (255,0,0), 2)
            cv2.rectangle(frame, (x1, y2-25), (x2,y2), (255,0,0), cv2.FILLED)
            cv2.putText(frame, name,(x1+6, y2-6), cv2.FONT_HERSHEY_COMPLEX, 0.5, (255,255,255), 2)

    cv2.imshow('video',frame)
    cv2.waitKey(1)