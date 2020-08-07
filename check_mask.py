import cv2
import imutils
import os
import time
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
from tensorflow.keras.preprocessing.image import img_to_array
from tensorflow.keras.models import load_model, model_from_json
import numpy as np

def re_init():
    global Hrisk,Mrisk,Lrisk
    Hrisk = 0
    Mrisk = 0
    Lrisk = 0

def mask_count():
    global Hrisk,Mrisk,Lrisk
    return Hrisk,Mrisk,Lrisk
##--------------------------------------------------------------------------------------------------------
## Mask Detection functions
##--------------------------------------------------------------------------------------------------------
def detect_and_predict_mask(frame, faceNet, maskNet):
	# grab the dimensions of the frame and then construct a blob from it
	(h, w) = frame.shape[:2]
	blob = cv2.dnn.blobFromImage(frame, 1.0, (300, 300), (104.0, 177.0, 123.0))

	# pass the blob through the network and obtain the face detections
	faceNet.setInput(blob)
	detections = faceNet.forward()

	# initialize our list of faces, their corresponding locations, and the list of predictions
	faces = []
	locs = []
	preds = []

	# loop over the detections
	for i in range(0, detections.shape[2]):

		# extract the confidence (i.e., probability) associated with the detection
		confidence = detections[0, 0, i, 2]
		# filter out weak detections
		if confidence > 0.70:
			# compute the (x, y)-coordinates of the bounding box for the object
			box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
			(startX, startY, endX, endY) = box.astype("int")
			# print("box:",(startX, startY, endX, endY))

			# ensure the bounding boxes fall within the dimensions of the frame
			(startX, startY) = (max(0, startX), max(0, startY))
			(endX, endY) = (min(w - 1, endX), min(h - 1, endY))

			# extract the face ROI, convert it from BGR to RGB channel ordering,
			# resize it to 224x224, and preprocess it
			face = frame[startY:endY, startX:endX]
			# print("face:",(startX, startY, endX, endY))


			try:
				face = cv2.cvtColor(face, cv2.COLOR_BGR2RGB)
				face = cv2.resize(face, (224, 224))
				face = img_to_array(face)
				face = preprocess_input(face)
				# add the face and bounding boxes to their respective lists
				faces.append(face)
				locs.append((startX, startY, endX, endY))

			except:
				return (-1,-1,-1)

	# only make a predictions if at least one face was detected
	if len(faces) > 0:
		faces = np.array(faces, dtype="float32")
		preds = maskNet.predict(faces, batch_size=32)

	# return a 2-tuple of the face locations and their corresponding locations
	return (locs, preds, len(faces))



def init_face_mask():


    # load our serialized face detector model from disk
    mypath = os.getcwd()
    facenet_dir = os.path.join(mypath,"face_detector")
    prototxtPath = os.path.join(facenet_dir,"deploy.prototxt")
    weightsPath = os.path.join(facenet_dir,"res10_300x300_ssd_iter_140000.caffemodel")
    faceNet = cv2.dnn.readNet(prototxtPath, weightsPath)
    print("Loaded faceNet model")

    # load the face mask detector model from disk
    mask_dir = os.path.join(mypath,"mask_model")
    json_file = open(os.path.join(mask_dir,"detection_model.json"),"r")
    loaded_model_json = json_file.read()
    json_file.close()
    maskNet = model_from_json(loaded_model_json)
    # load weights into new model
    maskNet.load_weights(os.path.join(mask_dir,"detection_model.h5"))
    print("Loaded maskNet model")
    return faceNet,maskNet

faceNet,maskNet = init_face_mask()
Hrisk = 0
Mrisk = 0
Lrisk = 0

class Check_Mask(object):
    def __init__(self):
        pass

    def check_mask(self, label,lprob, imgpath):
        global Hrisk,Mrisk,Lrisk
        hrisk = 0
        mrisk = 0
        lrisk = 0

        # print("Makeup: ",label)
        iname = int((imgpath.split(os.sep)[-1]).split('.')[0])


        if (label == "dry cough" or label == "wet cough")  and lprob >= 0.50:
            is_cough = True
        else:
            is_cough = False

        # print("is_cough:",label,lprob,is_cough)

        frame = cv2.imread(imgpath)
        try:
            frame = imutils.resize(frame, width=400)
        # print("resized frame shape:",frame.shape)
            (locs, preds, faces) = detect_and_predict_mask(frame, faceNet, maskNet)
            if (locs == -1) and (preds == -1):
                return False

            for (box, pred) in zip(locs, preds):

                (startX, startY, endX, endY) = box
                (mask, withoutMask) = pred
                mask_label = "Mask" if mask > withoutMask else "No Mask"

                if mask>0.70 or withoutMask>0.70:
                	#sort into risk categories
                    if is_cough:
                        if mask_label == 'Mask':
                            label = "Moderate Risk"
                            color = (255, 0, 0) #Blue
                            mrisk += 1

                        else:
                            label = "High Risk"
                            color = (0, 0, 225) #Red
                            hrisk += 1

                    else:
                        if mask_label == 'Mask':
                            label = "Low Risk"
                            color = (0, 225, 0) #Green
                            lrisk += 1

                        else:
                            label = "Moderate Risk"
                            color = (255, 0, 0) #Blue
                            mrisk += 1



                	# include the probability in the label
                	# label = "{} ({:.1f}%)".format(label, max(mask, withoutMask) * 100)
                	# display the label and bounding box rectangle on the output frame
                    cv2.putText(frame, label, (startX, startY - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.45, color, 2)
                    cv2.rectangle(frame, (startX, startY), (endX, endY), color, 2)

                    if hrisk > Hrisk:
                        Hrisk = hrisk
                    if mrisk > Mrisk:
                        Mrisk = mrisk
                    if lrisk > Lrisk:
                        Lrisk = lrisk



                else:
                    continue

            if faces < 5:
                # show the output frame
                # cv2.imshow("Frame", frame)
                # key = cv2.waitKey(1) & 0xFF
                cv2.imwrite(imgpath,frame)
                # cv2.imshow('myframe',frame)
                # return img.transpose(Image.FLIP_LEFT_RIGHT)
            return imgpath
        except:
            time.sleep(1)
            return ""
