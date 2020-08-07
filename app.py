import matplotlib
matplotlib.use('Agg')
# Importing major libraries
from flask import Flask, render_template, url_for,request, jsonify
from flask_socketio  import SocketIO
import base64
import os
# Importing from external python file
from audio_model import init_cough_mask,extract_features
from check_mask import Check_Mask
from capture import Capture
from check_mask import mask_count,re_init
#Remove logging
import logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

#Hide warnings
import warnings
warnings.filterwarnings("ignore")
import shutil

#Function to handle unrequired pages
def page_not_found(e):
    print('Not found')
    return render_template('404.html'), 404

# Creating flask app and initialize the socket
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
app.register_error_handler(404, page_not_found)

# Socket
socketio = SocketIO(app, cors_allowed_origins="*",ping_interval=60000, ping_timeout=120000, async_mode = "threading")

#Global Variables
sockets = {}

#Load the models
cough_model = init_cough_mask()

class Socket:
    def __init__(self, sid):
        self.sid = sid
        self.connected = True
        self.count = "0"
        self.icount = "0"
        self.lname = "breathing"
        self.lprob = 0
        self.dirpath =""
        self.Hrisk = 0
        self.Mrisk = 0
        self.Lrisk = 0
        self.capture = None

    # Emits data to a socket's unique room
    def emit(self, event, data):
        socketio.emit(event, data, room=self.sid)

#Reinitialise the count when refreshed or on a new connection
def re_initialise():
    global Hrisk,Mrisk,Lrisk
    Hrisk = 0
    Mrisk = 0
    Lrisk = 0
    capture = None

# Load the html page as homepage
@app.route('/', methods=['GET'])
def index():
    # Main page
    return render_template('index.html')

# Return message on successful connection
@socketio.on('connect')
def connection():
    currentSocketId = request.sid
    sockets[request.sid] = Socket(request.sid)
    sockets[request.sid].emit('message', 'connected established')

#When the user clicks on start
@socketio.on('started')
def started_feed(message):
    print(message)
    re_initialise()
    sockets[request.sid].capture = Capture(Check_Mask())

    currentSocketId = request.sid
    folder = os.path.join(os.getcwd(),"static")
    sockets[request.sid].dirpath = os.path.join(folder,currentSocketId)

    if not os.path.isdir(sockets[request.sid].dirpath):
        os.mkdir(sockets[request.sid].dirpath)


#Receive the blob and process it
@socketio.on('blob_event')
def handle_blob(message):
    currentSocketId = request.sid

    #Declaring filename and videoname)
    filename = "video" + sockets[request.sid].count + ".webm"

    filepath = os.path.join(sockets[request.sid].dirpath,filename)

    data = base64.b64decode(message)

    #write the videofile to disk
    try:
        f = open(filepath, 'wb')
        f.write(data)
        f.close()
    except:
        # print("Stoppped feed")
        return

    #Updating information
    sockets[request.sid].count = str(int(sockets[request.sid].count)+1)
    print ("Processing now: ", filepath)

    #Path to save the melspectrogram image
    img_name = sockets[request.sid].count + ".png"
    img_savepath = (os.sep).join(filepath.split(os.sep)[:-1])
    img_savepath = os.path.join(img_savepath,img_name)
    

    #function for audio processing
    sockets[request.sid].lname,sockets[request.sid].lprob = extract_features(cough_model,filepath,img_savepath)
    print("Predicted class:",sockets[request.sid].lname)
    sockets[request.sid].emit('label_event',{"label":sockets[request.sid].lname,"prob":str(sockets[request.sid].lprob)})


#Process the frames from the video feed
@socketio.on('input_image')
def test_message(image):
    #Creating image path
    image = image.split(",")[1]
    iname = sockets[request.sid].icount + ".jpg"
    currentSocketId = request.sid

    if not os.path.isdir(sockets[request.sid].dirpath):
        os.mkdir(sockets[request.sid].dirpath)
    # Creating folder to save images
    ipath = os.path.join(sockets[request.sid].dirpath,"images")

    if not os.path.isdir(ipath):
        os.mkdir(ipath)
    ipath = os.path.join(ipath,iname)

    # Saving image
    with open(ipath, "wb") as f:
        f.write(base64.b64decode(image))

    # Send image for processing
    sockets[request.sid].capture.enqueue_input(ipath,sockets[request.sid].lname,sockets[request.sid].lprob)
    sockets[request.sid].icount = str(int(sockets[request.sid].icount)+1)

    imagepath = os.path.join(currentSocketId,"images")
    imagepath = os.path.join(imagepath,iname)

    frame = sockets[request.sid].capture.get_frame()

    #To solve Windows path error issues
    if os.sep == '\\':
        imagepath = imagepath.replace('\\','/')

    #Sending the processed frame to frontend
    sockets[request.sid].emit("response_back",url_for("static",filename = imagepath))

    #Send analytics every five seconds
    if int(sockets[request.sid].icount) % 5 ==0:
        hrisk,mrisk,lrisk = mask_count()
        re_init()
        sockets[request.sid].Hrisk += hrisk
        sockets[request.sid].Lrisk += lrisk
        sockets[request.sid].Mrisk += mrisk
        print("High Risk: ",sockets[request.sid].Hrisk,"Moderate Risk: ",sockets[request.sid].Mrisk,"Low Risk: ",sockets[request.sid].Lrisk)
        sockets[request.sid].emit('stopped',{"High Risk": sockets[request.sid].Hrisk,"Moderate Risk":sockets[request.sid].Mrisk,"Low Risk":sockets[request.sid].Lrisk})

@socketio.on('stopped')
def stopped_function(message):
    print(message)

    shutil.rmtree(sockets[request.sid].dirpath, ignore_errors = True)

    socketio.sleep(1)

@socketio.on('disconnect')
def disconnect_function():
    try:
        shutil.rmtree(sockets[request.sid].dirpath)
    except:
        pass
    print("Disconnected the socket: ")
    sockets[request.sid].emit("Manual Disconnect")

@socketio.on('uncaughtException')
def exception_func():
    # handle or ignore error
    console.log(exception);


if __name__ == '__main__':
    print ("socket listening on 8000")
    socketio.run(app, port = 8000, host='0.0.0.0')
