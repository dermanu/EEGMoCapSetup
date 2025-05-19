# Qualisys Marker System Integration

This folder contains all files and instructions required to set up the **Qualisys marker-based motion capture system** for integration with LabStreamingLayer (LSL).

---

## Folder Contents

- `Qualisys_Calibration_AIM_Models/`  
  Contains:
  - `.qdr` configuration files  
  - AIM models  
  - Calibration files

- `Qualisys_LSL_Streamer/`  
  Contains:
  - **Modified Qualisys LSL client**: Streams marker positions via LSL.
  - `Qualisys.bat`: Batch file to launch the modified client.

> 🔧 The modified LSL client **waits until QTM starts streaming** marker positions before initializing the LSL stream.

---

## Setup Instructions

### 1. Start Qualisys

- Launch **Qualisys Track Manager (QTM)**.
- Confirm all cameras are detected.
  - If not, check the **Qualisys DHCP Server (QDS)** in the taskbar.
  - Reboot the cameras and/or inspect **network configuration**.

### 2. Load or Create Project

- Open the appropriate `.qpr` project file.
- Or create a new project in QTM and save it.

### 3. Configure Project Settings

Go to **Tools > Project Options** and verify the following:

- **Connection**: Correct device connections.
- **Linearization**: Performed and complete.
- **Calibration**: Properly executed.
- **Timing**: Set to use **external TTL trigger**.
- **Camera Settings**: Configured for external triggering.

### 4. Define AIM Model

- Use QTM to create an **AIM model** corresponding to your reflective marker setup.

### 5. Start LSL Streaming

- Run the `Qualisys.bat` file from the `Qualisys_LSL_Streamer` directory.
- The LSL client will wait for QTM to begin sending data before starting the stream.

---

## Notes

- This setup enables **synchronized marker and EEG/video data** via external TTL triggering.
- The Qualisys LSL stream will automatically start once QTM is live and streaming marker data.

---

**Maintainer**: Emanuel Lorenz  
**Lab**: NTNU Vizlab / EEG-MoCap  
"""

