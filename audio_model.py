from tensorflow.keras.models import load_model
import numpy as np
import imutils
import os
import librosa
from keras.applications.vgg16 import VGG16
from keras.preprocessing import image
from keras.models import Sequential, Model
from keras.layers import Dense, Dropout, Flatten, Input
import librosa.display
import warnings
from sklearn.preprocessing import scale
import matplotlib.pyplot as plt
warnings.filterwarnings("ignore")


##--------------------------------------------------------------------------------------------------------
## Cough Detection functions
##--------------------------------------------------------------------------------------------------------

def init_cough_mask():

	batch_size = 40
	epochs = 200

	# dimensions of our images.
	img_width, img_height = 224, 224

	input_tensor = Input(shape=(224,224,3))

	nb_training_samples = 723
	nb_validation_samples = 181 # Set parameter values

	base_model = VGG16(weights='imagenet', include_top=False, input_tensor=input_tensor)
	print('VGG Model loaded.')
	# base_model.summary()

	# build a classifier model to put on top of the convolutional model
	top_model = Sequential()
	top_model.add(Flatten(input_shape=base_model.output_shape[1:]))
	top_model.add(Dense(256, activation='relu'))
	top_model.add(Dropout(0.5))
	top_model.add(Dense(20, activation='softmax'))
	# top_model.summary()

	model = Model(inputs=base_model.input, outputs=top_model(base_model.output))
	# model.summary()

	num_layers_to_freeze = 15
	from keras import metrics, optimizers

	def top_5_accuracy(y_true, y_pred):
	    return metrics.top_k_categorical_accuracy(y_true, y_pred, k=5)

	for layer in model.layers[:num_layers_to_freeze]:
	    layer.trainable = False


	#load cough detector model
	modelfolder = os.path.join(os.getcwd(),"model2_1")
	model.load_weights(os.path.join(modelfolder,"model2_1.h5"))
	print("Loaded cough model from disk")


    # model = tensorflow.keras.experimental.load_from_saved_model('', custom_objects={'Functional':hub.Functional})
    # model = tf.keras.models.load_model('/home/mitali/Cough-Detector/model2_1/model2_1.h5',custom_objects={'Functional':hub.Functional})
	return model

def get_top_k_predictions(preds, label_map, k=5, print_flag=True):
    sorted_array = np.argsort(preds)[::-1]
    top_k = sorted_array[:k]
    label_map_flip = dict((v,k) for k,v in label_map.items())

    y_pred = []
    for label_index in top_k:
        if print_flag:
            print(f"{label_map_flip[label_index]} ({preds[label_index]})")
        y_pred.append(label_map_flip[label_index])
        lname = label_map_flip[label_index]
        lprob = preds[label_index]
    return lname,lprob

def extract_features(loaded_model,filename,img_savepath):

    data, sr = librosa.load(filename, sr=44100, mono=True)
    data = scale(data)

    melspec = librosa.feature.melspectrogram(y=data, sr=sr, n_mels=128)
    log_melspec = librosa.power_to_db(melspec, ref=np.max)
    librosa.display.specshow(log_melspec, sr=sr)
    # print("Log_Melspec Shape: ",log_melspec.shape)

    plt.savefig(img_savepath)
    img = image.load_img(img_savepath, target_size=(224, 224))
    x = image.img_to_array(img)
    # x = image.img_to_array(log_melspec)
    x = np.expand_dims(x, axis=0)* 1./255

    preds = loaded_model.predict(x)[0]

    label_map = {'airplane': 0,
                 'breathing': 1,
                 'car_horn': 2,
                 'chainsaw': 3,
                 'church_bells': 4,
                 'clapping': 5,
                 'crying_baby': 6,
                 'door_wood_knock': 7,
                 'dry cough': 8,
                 'engine': 9,
                 'fireworks': 10,
                 'helicopter': 11,
                 'laughing': 12,
                 'rain': 13,
                 'silence': 14,
                 'speech': 15,
                 'thunderstorm': 16,
                 'train': 17,
                 'wet cough': 18,
                 'wind': 19}

    result = get_top_k_predictions(preds, label_map, k=1)
    print(result)
    # print(type(result))
    return result
