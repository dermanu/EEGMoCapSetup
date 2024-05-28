import os
import cv2
import EasyPySpin
import PySpin
import uuid    
import sys
from pylsl import StreamInfo, StreamOutlet
from multiprocessing import Process, Queue
from threading import Thread
import time
import datetime
import collections

class VideoAcq(object):
    def __init__(self, camNum, start_time):
        self.cam = camNum
        self.buflen = 1000  #4800 for a min recoding?
        self.buffer = collections.deque(maxlen=self.buflen)

        # Set settings
        settings = {'fps': 100, 'width': 1280, 'height': 1024, 'brightness': 0.5, 'contrast': 0.5,
                'saturation': 0.64, 'hue': 0.5, 'gain': -1, 'exposure': 7990,
                'dataFolder': 'C:\Projects\Test_Data'}
        dataFolder = settings['dataFolder']
        
        # Wait for set time point to start parallel
        while time.time() < start_time: pass

        # Open webcam stream
        self.cap = []
        self.cap = EasyPySpin.VideoCapture(self.cam)
        if not self.cap.isOpened():
            print('Camera' + str(self.cam) + ' is not connected!')
            return

        # Set parameters of cameras
        setDevParameters(self.cap, settings)  # => Change to setDevParametersTTL for trigger

        # Set parameters for avi writer
        self.avi_recorder = PySpin.SpinVideo()
        filename = os.path.join(dataFolder, 'Camera' + str(self.cam) + '.avi')
        option = PySpin.AVIOption()
        option.frameRate = self.cap.get(cv2.CAP_PROP_FPS)
        self.avi_recorder.Open(filename, option)

        # Set LSL outlet
        self.outlet = createOutlet(self.cam, filename)

        # Create seperate stream for Video capture
        self.thread = Thread(target=VideoAcq.capture_Frame, args=(self, ))
        self.thread.daemon = True
        self.thread.start()

        print('Capturing of Camera' + str(self.cam) + ' is started!')

        # Start main routine
        VideoAcq.start_Capture(self)

    # Coordinating everything in another thread
    def start_Capture(self):
        def start_Capture_thread(): 
            while True:
                try:
                    if not self.buffer:
                        print("BUFFER: Empty!")
                        break
                    if self.buflen <= len(self.buffer): #Might need a counter
                        print("BUFFER: Full!")
                        break
                    time1 = time.time()
                    VideoAcq.save_Frame(self)
                    self.t_diff = time.time()-time1
                except AttributeError:
                    pass  
            VideoAcq.end_capture(self)    

        self.capture_thread = Thread(target = start_Capture_thread, args = ())
        self.capture_thread.daemon = True
        self.capture_thread.start()   
    
    # Save frame
    def save_Frame(self):
        if self.buffer:
            self.avi_recorder.Append(self.buffer.pop())
            
    # Capture frame
    def capture_Frame(self):
        self.frameCounter = 1                       #START EARLYER THEN FILE SAVER -> UNDOCUMENTED BUFFEROVERFLOW?
        self.t_diff = 0
        while True:
            ret, frame = self.cap.read()
            if ret:
                self.outlet.push_sample([self.frameCounter, self.t_diff])
                frame = cv2.cvtColor(frame, cv2.COLOR_BayerBG2BGR)
                self.buffer.append(frame)
                self.frameCounter += 1

    # End capture - not used - but should
    def end_capture(self):          
        self.cap.release()
        self.avi_recorder.Close()
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
    VideoAcq(cam, start_time).end_capture()     

if __name__ == "__main__":
   start_time = time.time() + 3
   Process(target=stayin_alive, args=(0, start_time)).start() 
   Process(target=stayin_alive, args=(1, start_time)).start()
   Process(target=stayin_alive, args=(2, start_time)).start()


## If not working https://github.com/nrsyed/computer-vision