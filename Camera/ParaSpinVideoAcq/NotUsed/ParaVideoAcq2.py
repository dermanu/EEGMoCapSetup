import os
import cv2
import EasyPySpin
#import PySpin
import uuid    
import sys
from pylsl import StreamInfo, StreamOutlet
from multiprocessing import Process, Queue
from threading import Thread
import time
import datetime

class VideoAcq(object):
    def __init__(self, camNum, start_time):
        self.cam = camNum
        settings = {'fps': 100, 'width': 1280, 'height': 1024, 'brightness': 0.5, 'contrast': 0.5,
                'saturation': 0.64, 'hue': 0.5, 'gain': -1, 'exposure': 7990, 'buffer': 100,
                'dataFolder': 'C:\Projects\Test_Data'}
        dataFolder = settings['dataFolder']

        while time.time() < start_time: pass

        self.cap = []
        self.cap = EasyPySpin.VideoCapture(self.cam)
        if not self.cap.isOpened():
            print('Camera' + str(self.cam) + ' is not connected!')
            return

        setDevParameters(self.cap, settings)

        fps = self.cap.get(cv2.CAP_PROP_FPS)
        width = self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        height = self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        filename = os.path.join(dataFolder, 'Camera' + str(self.cam) + '.avi')
        fourcc = cv2.VideoWriter_fourcc(*'MPEG')
        #fourcc = cv2.VideoWriter_fourcc(*'X264') -> might be faster?!
        self.writer = cv2.VideoWriter(filename, fourcc, fps, (int(width), int(height)))
        self.outlet = createOutlet(self.cam, filename)

        self.thread = Thread(target=VideoAcq.capture_Frame, args=(self, ))
        self.thread.daemon = True
        self.thread.start()

        print('Capturing of Camera' + str(self.cam) + ' is started!')

        VideoAcq.start_Capture(self)

    def start_Capture(self):
        def start_Capture_thread(): 
            self.frameCounter = 1 
            while True:
                try:
                    time1 = time.time()
                    VideoAcq.save_Frame(self)
                    self.t_diff = time.time()-time1
                    self.frameCounter += 1
                except AttributeError:
                    pass  

        self.capture_thread = Thread(target = start_Capture_thread, args = ())
        self.capture_thread.daemon = True
        self.capture_thread.start()   

    def save_Frame(self):
        self.writer.write(self.frame)

    def capture_Frame(self):
        self.t_diff = 0
        self.frameCounter = 0
        while True:
            self.ret, self.frame = self.cap.read()
            self.outlet.push_sample([self.frameCounter, self.t_diff])
            self.frame = cv2.cvtColor(self.frame, cv2.COLOR_BayerBG2BGR)

    def end_capture(self):          
        self.cap.release()
        self.writer.release()
        cv2.destroyAllWindows()
        exit(1)


def setDevParameters(cap, settings):
    cap.set(cv2.CAP_PROP_FPS,           settings['fps'])
    cap.set(cv2.CAP_PROP_FRAME_WIDTH,   settings['width'])
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT,  settings['height'])
    #cap.set(cv2.CAP_PROP_BRIGHTNESS,    settings['brightness'])
    #cap.set(cv2.CAP_PROP_CONTRAST,      settings['contrast'])
    #cap.set(cv2.CAP_PROP_SATURATION,    settings['saturation'])
    #cap.set(cv2.CAP_PROP_HUE,           settings['hue'])
    #cap.set(cv2.CAP_PROP_GAIN,          settings['gain'])
    cap.set(cv2.CAP_PROP_EXPOSURE,      settings['exposure'])
    cap.set(cv2.CV_CAP_PROP_BUFFERSIZE, settings['buffer']) # -> change buffer size

def createOutlet(cam, filename):
    streamName = 'FrameMarker'+str(cam)
    info = StreamInfo(name=streamName,
                    type='videostream',
                    channel_format='float32',
                    channel_count=2,
                    source_id=str(uuid.uuid4()))
    info.desc().append_child_value("videoFile", filename)
    return StreamOutlet(info)

def stayin_alive(cam, start_time):    
    VideoAcq(cam, start_time)
    while True:
         time.sleep(5)

if __name__ == "__main__":
   start_time = time.time() + 3
   Process(target=stayin_alive, args=(0, start_time)).start() 
   Process(target=stayin_alive, args=(1, start_time)).start()
   Process(target=stayin_alive, args=(2, start_time)).start()


## If not working https://github.com/nrsyed/computer-vision