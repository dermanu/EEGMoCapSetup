import os
import cv2
import EasyPySpin
import uuid    
from pylsl import StreamInfo, StreamOutlet
from multiprocessing import Process, Lock

def capture(camNum):
    settings = {'fps': 60, 'width': 1280, 'height': 1024, 'brightness': 0.5, 'contrast': 0.5,
            'saturation': 0.64, 'hue': 0.5, 'gain': -1, 'exposure': -1,
            'dataFolder': 'C:\Projects\Test_Data'}
    dataFolder = settings['dataFolder']
    record = True
    cap = []
    frameCounter = 1
    cap = EasyPySpin.VideoCapture(camNum)
    if not cap.isOpened():
        print('Camera' + str(camNum) + ' is not connected!')
        return
    setDevParameters(cap, settings['Camera' + str(camNum)])
    winName = 'Camera ' + str(camNum)
    cv2.namedWindow(winName)
    print('Recording of Camera' + str(camNum) + ' is started!')
    if record:
        fps = cap.get(cv2.CAP_PROP_FPS)
        width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        filename = os.path.join(dataFolder, 'Camera' + str(camNum) + '.avi')
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        writer = cv2.VideoWriter(filename, fourcc, fps, (int(width), int(height)))
        outlet = createOutlet(camNum, filename)
    try:
        ret = True
        while (cv2.waitKey(1) & 0xFF) != ord('q') and ret:                  ## Maybe only parallelly execute while loop
            if cv2.getWindowProperty(winName, cv2.WND_PROP_VISIBLE):
                ret, frame = cap.read()
                frame = cv2.cvtColor(frame, cv2.COLOR_BayerBG2BGR)
                cv2.imshow(winName, frame)
                if record:
                    outlet.push_sample([frameCounter])
                    writer.write(frame)
            else:
                ret = False
            frameCounter += 1
            cv2.waitKey(1)
    finally:
        cap.release()
        cv2.destroyAllWindows()
        print('Recording of Camera' + str(camNum) + ' ended!')
     

def setDevParameters(cap, parameters):
    cap.set(cv2.CAP_PROP_FPS,           parameters['fps'])
    cap.set(cv2.CAP_PROP_FRAME_WIDTH,   parameters['width'])
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT,  parameters['height'])
    cap.set(cv2.CAP_PROP_BRIGHTNESS,    parameters['brightness'])
    cap.set(cv2.CAP_PROP_CONTRAST,      parameters['contrast'])
    cap.set(cv2.CAP_PROP_SATURATION,    parameters['saturation'])
    cap.set(cv2.CAP_PROP_HUE,           parameters['hue'])
    cap.set(cv2.CAP_PROP_GAIN,          parameters['gain'])
    cap.set(cv2.CAP_PROP_EXPOSURE,      parameters['exposure'])


def createOutlet(index, filename):
    streamName = 'FrameMarker'+str(index+1)
    info = StreamInfo(name=streamName,
                    type='videostream',
                    channel_format='float32',
                    channel_count=1,
                    source_id=str(uuid.uuid4()))
    info.desc().append_child_value("videoFile", filename)
    return StreamOutlet(info)


if __name__ == "__main__":
    capture(3)