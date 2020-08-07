### Problem Statement
To monitor the presence of face masks and detect coughs in real time and classify individuals into varying risk categories. 

#### Built With
* Flask
* Flask-SocketIO
* Librosa
* Keras
* Tensorflow
* OpenCV
* Media Recorder API
* Bootstrap 4

##### The Web Application is deployed on Microsoft Azure, and can be accessed via 
<a href="https://pnuemosenseai.azurewebsites.net/" target="_blank">https://pnuemosenseai.azurewebsites.net/</a>

#### Troubleshooting
* In case the trigger doesn't appear at all, it is advised to open the link in the incognito mode.
* Latency: latency depends on the GPU of the system on which  you are running the web application. For best results, A high performing GPU is required.

#### How do I deploy the app?

##### Getting Started
The following package versions must be installed to successfully deploy the model.
* matplotlib 3.1.3
* ffmpeg 3.2
* numpy 1.18.5
* Flask 1.1.2
* gevent 1.4.0
* Keras 2.3.0
* librosa 0.6.3
* numba 0.49.1
* tensorflow 2.1.0
* python 3.7.1
* flask-socketio 4.3.1
* imutils 0.5.3
* opencv-python 4.3.0.36
* six 1.12.0
* scipy 1.4.1
* setuptools 41.0.0

To run the model on your <b>local machine</b>, you can download this repository as a zip file, clone or pull it by using the command
```
$ git pull https://github.com/mitali3112/Cough-Detector.git
```
or
```
$ git clone https://github.com/mitali3112/Cough-Detector.git
```
Requirements can be installed using the command (from the command-line)
```
$ pip install -r requirements.txt
```

Then, navigate to the project folder and execute the command
```
$ python app.py
```

to deploy the app locally. 

On your web browser go to <a href="http://localhost:8000/" target="_blank">http://localhost:8000/</a>

#### Contributers
* Aparna Ranjith
* Gunveen Batra
* Mansi Parashar
* Mitali Sheth 
* Sruti Dammalapati

#### Acknowledgements 
We thank B-Aegis Life Sciences for the opportunity.
