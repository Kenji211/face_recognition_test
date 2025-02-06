import cv2
import numpy as npy
import face_recognition as face_rec


def resize(img, size) :
    width = int(img.shape[1]*size)
    height = int(img.shape[0] * size)
    dimension = (width,height)
    return cv2.resize(img, dimension, interpolation=cv2.INTER_AREA)


#img declaration
ervon = face_rec.load_image_file('images/ervon.jpg')
ervon = cv2.cvtColor(ervon, cv2.COLOR_BGR2RGB)
ervon = resize(ervon, 0.70)

ervon_test = face_rec.load_image_file('images/niel.jpg')
ervon_test = cv2.cvtColor(ervon_test, cv2.COLOR_BGR2RGB)
ervon_test = resize(ervon_test, 0.70)

# #location finding
faceLocation_ervon = face_rec.face_locations(ervon)[0]
encode_ervon = face_rec.face_encodings(ervon)[0]
cv2.rectangle(ervon, (faceLocation_ervon[3], faceLocation_ervon[0]), (faceLocation_ervon[1], faceLocation_ervon[2]), (255, 0, 255), 3)

faceLocation_ervon_test = face_rec.face_locations(ervon_test)[0]
encode_ervon_test = face_rec.face_encodings(ervon_test)[0]
cv2.rectangle(ervon_test, (faceLocation_ervon_test[3], faceLocation_ervon_test[0]), (faceLocation_ervon_test[1], faceLocation_ervon_test[2]), (255, 0, 255), 3)


result = face_rec.compare_faces([encode_ervon], encode_ervon_test)
print(result)
cv2.putText(ervon_test, f'{result}',(50,50), cv2.FONT_HERSHEY_COMPLEX, 1,(0,0,255),2)

cv2.imshow('main_img', ervon)
cv2.imshow('test_img', ervon_test)
cv2.waitKey(0)
cv2.destroyAllWindows()

