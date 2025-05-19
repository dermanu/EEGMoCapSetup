# EEGMoCapSetup

This repository contains all required software and configuration files to run the EEGMoCap study, integrating EEG, video, motion capture, and VR streams via LabStreamingLayer (LSL).

---

## Folder Structure

- **Camera/**  
  Python scripts for parallel video acquisition from two FLIR cameras.  
  - TTL‐triggered frame capture at 100 Hz  
  - Frame counters streamed via LSL

- **EEG/LiveAmpLSLStreamDelay/**  
  Modified Brain Products LiveAmp LSL client with startup delay.  
  - Waits for LiveAmp TTL sync before initializing LSL stream  
  - Includes electrode configuration file

- **Qualisys/**  
  Custom Qualisys LSL client that waits for QTM to begin streaming.  
  - Contains `.qpr` project file and AIM models in `Qualisys_Calibration_AIM_Models/`  
  - Batch launcher `Qualisys.bat` in `Qualisys_LSL_Streamer/`

- **Recorder/**  
  Standard LabRecorder application with example XML configuration.  
  - Records all required LSL streams into `.xdf` files

---

## Setup and Execution

1. **Qualisys Motion Capture**  
   - Launch QTM, ensure cameras are online (check QDS and network settings).  
   - Load or create your Qualisys project (`.qpr`).  
   - Verify external TTL trigger under **Tools > Project Options**.  
   - Run `Qualisys.bat` to start the LSL streamer.

2. **FLIR Camera Acquisition**  
   - Install FLIR Spinnaker SDK and Python dependencies.  
   - Configure TTL trigger wiring to camera GPIO.  
   - Run the video acquisition script in **Camera/**.

3. **LiveAmp EEG Stream**  
   - Install LiveAmp drivers and LSL client.  
   - Use the delayed client in **EEG/LiveAmpLSLStreamDelay/** to align with camera and Qualisys streams.

4. **Recording with LabRecorder**  
   - Edit the XML config in **Recorder/** to specify required streams and output path.  
   - Launch LabRecorder to capture all streams into an `.xdf` file.

5. **VR Synchronization (Optional)**  
   - Launch VR task to send event markers to LSL.

---

## Notes

- All streams must be active before starting LabRecorder.
- Use the provided example configs as templates.
- Consult README files in each subfolder for detailed instructions.

---

**Maintainer**: Emanuel Lorenz  
**Lab**: NTNU Vizlab / EEG-MoCap  
"""
