import os
import cv2
import EasyPySpin
import PySpin
import uuid    
import sys
import numpy as np
import skvideo
skvideo.setFFmpegPath('C:/Program Files/ffmpeg/ffmpeg-2023-09-07-git-9c9f48e7f2-essentials_build/bin') #set path to ffmpeg installation before importing io
import skvideo.io
from pylsl import StreamInfo, StreamOutlet
from multiprocessing import Process
from threading import Thread
import time
import datetime
import queue
import keyboard
class VideoAcq(object):
    def __init__(self, camNum, start_time):
        self.cam = camNum
        self.buflen = 500
        self.buffer = queue.Queue(maxsize=self.buflen)

        # Set settings
        self.settings = {'fps': 100, 'width': 1280, 'height': 800, 'brightness': 0.0, 'contrast': 0.5,
                'saturation': 0.80, 'hue': 0.5, 'gain': 0, 'exposure': 9791, "saturation": 1.15, "balance_ratio": 1.05,
                'dataFolder': 'C:/Users/vizlab_stud/Desktop/Emanuel/data/video'}
        dataFolder = self.settings['dataFolder']
        
        # Wait for set time point to start parallel
        while time.time() < start_time: pass

        # Open webcam stream
        self.cap = []
        self.cap = EasyPySpin.VideoCapture(self.cam)
        if not self.cap.isOpened():
            print('Camera' + str(self.cam) + ' is not connected!')
            return

        # Set parameters of cameras
        setDevParametersTTL(self.cap, self.settings)

        # Set parameters for video writer
        filename = os.path.join(dataFolder, 'Camera' + str(self.cam) + '_' + str(hash(start_time)) + '.mp4')
        self.writer = skvideo.io.FFmpegWriter(filename, inputdict={'-framerate':str(self.settings['fps'])}, outputdict={'-vcodec': 'h264_nvenc'})
        
        # Set LSL outlet
        self.outlet = createOutlet(self.cam, filename)

        # Start camera stream
        if not self.cap.cam.IsStreaming():
            self.cap.cam.BeginAcquisition()
        else: 
            print('Capturing of Camera' + str(self.cam) + ' can not be started!')

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
                    if self.buffer.empty:
                        #print("BUFFER: Empty!")
                        pass
                    if self.buffer.full(): #Might need a counter
                        print("BUFFER: Full!")
                        break
                    VideoAcq.save_Frame(self)
                except AttributeError:
                    pass
            VideoAcq.end_capture(self)

        self.capture_thread = Thread(target = start_Capture_thread, args = ())
        self.capture_thread.daemon = True
        self.capture_thread.start()   
    
    # Save frame
    def save_Frame(self):
        #image = self.buffer.pop().Convert(PySpin.PixelFormat_YUV444Packed)
        #image = self.buffer.pop().Convert(PySpin.PixelFormat_RGB8)
        image = self.buffer.get()
        image = np.array(image.GetData(), dtype="uint8").reshape((self.settings['height'], self.settings['width'],3))
        self.writer.writeFrame(image)
   
            
    # Capture frame
    def capture_Frame(self):
        frameCounter = 1 
        previous_time = datetime.datetime.now()
        while True:
            if keyboard.is_pressed("Esc"):
                print("Closed")
                self.end_capture()


            if frameCounter == 1: #Try to get first frame without timeout, but no use it further
                try:
                    frame = self.cap.cam.GetNextImage()
                    if not frame.IsIncomplete():
                        self.outlet.push_sample([frameCounter])
                        self.buffer.put(frame)
                        frameCounter += 1  
                except:
                    continue  
            if frameCounter > 1: 
                try:
                    frame = self.cap.cam.GetNextImage(1000) 
                    if not frame.IsIncomplete():
                        current_time = datetime.datetime.now()
                        elapsed = current_time - previous_time
                        previous_time = current_time
                        print(int(elapsed.total_seconds()*1000))
                        self.outlet.push_sample([frameCounter])
                        self.buffer.put(frame)
                        frameCounter += 1   
                except:
                    print("ERROR: Frame capture timeout")
                    break

    # End capture - not used - but should
    def end_capture(self):          
        self.cap.release()
        self.writer.close()
        sys.exit(1)

def setDevParametersTTL(cap, settings):
    # Intial non trigger settings -> needed to get right parameters for video writer -> strange...
    cap.set(cv2.CAP_PROP_FPS,           settings['fps'])
    cap.set(cv2.CAP_PROP_FRAME_WIDTH,   settings['width'])
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT,  settings['height'])
    cap.set(cv2.CAP_PROP_BRIGHTNESS,    settings['brightness'])
    cap.set(cv2.CAP_PROP_CONTRAST,      settings['contrast'])
    cap.set(cv2.CAP_PROP_SATURATION,    settings['saturation'])
    cap.set(cv2.CAP_PROP_HUE,           settings['hue'])
    cap.set(cv2.CAP_PROP_GAIN,          settings['gain'])
    cap.set(cv2.CAP_PROP_EXPOSURE,      settings['exposure'])

    #Set camera buffer
    camTransferLayerStream = cap.cam.GetTLStreamNodeMap()
    handling_mode = PySpin.CEnumerationPtr(camTransferLayerStream.GetNode('StreamBufferHandlingMode'))
    handling_mode_entry = handling_mode.GetEntryByName('NewestOnly')
    handling_mode.SetIntValue(handling_mode_entry.GetValue())

    #cap.cam.UserSetSelector.SetValue(PySpin.UserSetSelector_Default)
    #cap.cam.UserSetLoad()
    #Set frame rate to auto
    cap.cam.AcquisitionFrameRateEnable.SetValue(False)



    #cap.cam.AcquisitionFrameRate.SetValue(settings['fps'])

    # Set trigger mode to off to be able to set trigger settings
    if cap.cam.TriggerMode.GetAccessMode() != PySpin.RW:
        print('Unable to disable trigger mode (node retrieval). Aborting...')
        return False
    cap.cam.TriggerMode.SetValue(PySpin.TriggerMode_Off)

    # Set trigger selector to Frame Start
    if cap.cam.TriggerSelector.GetAccessMode() != PySpin.RW:
        print('Unable to get trigger selector (node retrieval). Aborting...')
        return False
    cap.cam.TriggerSource.SetValue(PySpin.TriggerSelector_FrameStart)

    # Set trigger source to Line 3
    if cap.cam.TriggerSource.GetAccessMode() != PySpin.RW:
        print('Unable to get trigger source (node retrieval). Aborting...')
        return False
    cap.cam.TriggerSource.SetValue(PySpin.TriggerSource_Line3)

    # Set trigger overlap to Read Out 
    cap.cam.TriggerOverlap.SetValue(PySpin.TriggerOverlap_ReadOut)

    # Set trigger activation to Rising Edge
    try:
        cap.cam.TriggerActiviation.SetValue(PySpin.TriggerActivation_RisingEdge)
    except:
        pass    
    
    # Switch trigger mode back on
    cap.cam.TriggerMode.SetValue(PySpin.TriggerMode_On)

    # Set acquisition mode to continous
    cap.cam.AcquisitionMode.SetValue(PySpin.ExposureMode_Timed)

    #Set automatic exposure on
    if cap.cam.ExposureAuto.GetAccessMode() != PySpin.RW:
        print('Unable to disable automatic exposure. Aborting...')
        return False
    cap.cam.ExposureAuto.SetValue(PySpin.ExposureAuto_Off)
    cap.cam.ExposureTime.SetValue(settings['exposure'])
    cap.cam.BalanceWhiteAuto.SetValue(PySpin.BalanceWhiteAuto_Off)
    cap.cam.BalanceRatio.SetValue(settings['balance_ratio'])
    try:
        cap.cam.IspEnable.SetValue(True)
    except:
        pass
    cap.cam.SaturationEnable.SetValue(True)
    cap.cam.RgbTransformLightSource.SetValue(PySpin.RgbTransformLightSource_CoolFluorescent4000K)
    cap.cam.Saturation.SetValue(settings['saturation'])


    # Set bandwidth 
    cap.cam.DeviceLinkThroughputLimit.SetValue(500000000)

    # Set Pixel format
    try:
        cap.cam.PixelFormat.SetValue(PySpin.PixelFormat_RGB8Packed)
    except:
        pass

def createOutlet(cam, filename):
    streamName = 'FrameMarker'+str(cam)
    info = StreamInfo(name=streamName,
                    type='videostream',
                    channel_format='float32',
                    channel_count=1,
                    source_id=str(uuid.uuid4()))
    info.desc().append_child_value("videoFile", filename)
    return StreamOutlet(info)

def stayin_alive(cam, start_time):
    VideoAcq(cam, start_time)
    while True:
        time.sleep(3)

if __name__ == "__main__":
   start_time = time.time() + 3
   cam1 = Process(target=stayin_alive, args=(0, start_time)).start() 
   cam2 = Process(target=stayin_alive, args=(1, start_time)).start()
   #cam3 = Process(target=stayin_alive, args=(2, start_time)).start()
   #cam4 = Process(target=stayin_alive, args=(3, start_time)).start()


