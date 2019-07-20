import cv2,os
import numpy as np
from PIL import Image

recognizer = cv2.face.LBPHFaceRecognizer_create(radius=1, neighbors=8, grid_x=8, grid_y=8)
detector= cv2.CascadeClassifier("haarcascade_frontalface_default.xml");

def getImagesAndLabels(path):
    folders = os.listdir(path)
    faceSamples=[]
    Ids=[]
    for folder in folders:
        label = int(folder)
        training_images_path = path + '/' + folder
        for image in os.listdir(training_images_path):
            image_path = training_images_path + '/' + image

            pilImage=Image.open(image_path).convert('L')

            imageNp=np.array(pilImage,'uint8')
            faces=detector.detectMultiScale(imageNp,1.1,4)
            for (x,y,w,h) in faces:
                faceSamples.append(imageNp[y:y+h,x:x+w])
                Ids.append(label)
    return faceSamples,Ids


faces,Ids = getImagesAndLabels('training')
print(len(faces))
print(len(Ids))

recognizer.train(faces, np.array(Ids))
if os.path.isfile("trainner.yml")==True:
	os.remove('trainner.yml')
	# menyimpan model pada file bernama trainner.yml
	recognizer.write('trainner.yml')
else:
    #save
	recognizer.write('trainner.yml')
