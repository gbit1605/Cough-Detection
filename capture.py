import threading
import base64
from time import sleep
import io
import cv2

class Capture(object):
    def __init__(self, check_mask):
        self.to_process = []
        self.to_output = []
        self.check_mask = check_mask
        self.labelname = ""
        self.labelprob = 0
        thread = threading.Thread(target=self.keep_processing, args=())
        thread.daemon = True
        thread.start()


    def process_one(self):
        if not self.to_process:
            return

        # input is an ascii string.
        input_str = self.to_process.pop(0)
        label = self.labelname
        lprob = self.labelprob

        ################## where the hard work is done ############
        # output_img is an imagepath
        output_img = self.check_mask.check_mask(label,lprob,input_str)
        if output_img == "":
            thread= threading.currentThread()
            thread.to_run = False


        self.to_output.append(output_img)

    def keep_processing(self):
        while True:
            self.process_one()
            sleep(0.01)

    def enqueue_input(self, input,label,lprob):
        self.to_process.append(input)
        self.labelname = label
        self.labelprob = lprob


    def get_frame(self):
        while not self.to_output:
            sleep(0.05)
        return self.to_output.pop(0)
