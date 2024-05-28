import os
import cv2
import EasyPySpin
import PySpin
import uuid    
from pylsl import StreamInfo, StreamOutlet
from multiprocessing import Process, Lock

def capture(camNum):
        dataFolder = 'C:\Projects\Test_Data'
        record = True
        cap = []
        frameCounter = 1
        cap = EasyPySpin.VideoCapture(camNum)
        if not cap.isOpened():
            print('Camera' + str(camNum) + ' is not connected!')
            return
        setDevParameters(cap)
        winName = 'Camera ' + str(camNum)
        cv2.namedWindow(winName)
        if record:
            fps = cap.get(cv2.CAP_PROP_FPS)
            width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
            height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
            filename = os.path.join(dataFolder, 'Camera' + str(camNum) + '.avi')
            fourcc = cv2.VideoWriter_fourcc(*'MJPG')
            writer = cv2.VideoWriter(filename, fourcc, fps, (int(width), int(height)))
            outlet = createOutlet(camNum, filename)
        try:
            print('Recording of Camera' + str(camNum) + ' is started!')
            ret = True
            while ret:                  ## Maybe only parallelly execute while loop
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

def setDevParameters(cap):
    print('Setting parameters')
    if cap.cam.TriggerMode.GetAccessMode() != PySpin.RW:
        print('Unable to disable trigger mode (node retrieval). Aborting...')
        return False
    cap.cam.TriggerMode.SetValue(PySpin.TriggerMode_Off)

    if cap.cam.TriggerSelector.GetAccessMode() != PySpin.RW:
        print('Unable to get trigger selector (node retrieval). Aborting...')
        return False
        cap.cam.TriggerSource.SetValue(PySpin.TriggerSelector_FrameStart)

    if cap.cam.TriggerSource.GetAccessMode() != PySpin.RW:
        print('Unable to get trigger source (node retrieval). Aborting...')
        return False
    cap.cam.TriggerSource.SetValue(PySpin.TriggerSource_Line3)

    cap.cam.TriggerOverlap.SetValue(PySpin.TriggerOverlap_ReadOut)

    ##cap.cam.TriggerActiviation.SetValue(PySpin.TriggerActivation_RisingEdge)

    cap.cam.TriggerMode.SetValue(PySpin.TriggerMode_On)

    cap.cam.AcquisitionMode.SetValue(PySpin.AcquisitionMode_Continuous)

    cap.set(cv2.CAP_PROP_EXPOSURE, 8000)

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1240)

    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1024)

    if cap.cam.ExposureAuto.GetAccessMode() != PySpin.RW:
        print('Unable to disable automatic exposure. Aborting...')
        return False
    cap.cam.ExposureAuto.SetValue(PySpin.ExposureAuto_Off)
    
    if cap.cam.ExposureTime.GetAccessMode() != PySpin.RW:
        print('Unable to set exposure time. Aborting...')
        return False
    exposure_time_to_set = min(cap.cam.ExposureTime.GetMax(), 8001.0)
    cap.cam.ExposureTime.SetValue(exposure_time_to_set)




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
    CamTotal = 4
    for num in range(CamTotal):
        Process(target=capture, args=(num,)).start()