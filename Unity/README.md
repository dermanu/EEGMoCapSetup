# Unity Experiment Control and VR Environment (Hand Tracking)

This folder contains Unity projects and scripts used for **experiment control** and **VR-based reaching tasks** with **hand tracking** support.

---

## Overview

The Unity environment is designed to:

- Present interactive reaching tasks in VR
- Control and log experimental trials
- Interface with LabStreamingLayer (LSL) for time-synchronized event streaming

---

## Features

- Modular VR scene for customizable task design
- Hand tracking support (e.g., Oculus, OpenXR, Leap Motion)
- Trigger-based event handling (start, end, feedback)
- LSL integration for synchronization with external data sources (e.g., EEG, MoCap)

---

## Setup Requirements

- **Unity Version**: 2021.3 LTS or newer
- **Hardware**: VR headset with hand tracking (e.g., Oculus Quest 2)
- **Unity Packages**:
  - XR Interaction Toolkit
  - OpenXR or Oculus Integration
  - LabStreamingLayer Unity plugin

---

## Usage Instructions

1. Open the Unity project in the correct Unity version.
2. Load the main scene.
3. Connect and activate your VR headset with hand tracking.
4. Configure LSL outlets in Unity Inspector (if applicable).
5. Enter Play mode to run the VR experiment.

---

## Notes

- Hand tracking fidelity depends on the hardware and lighting conditions.
- Use [LabRecorder](https://github.com/sccn/labstreaminglayer) to record `.xdf` files from LSL streams.
- Ensure trial timing and event triggers are synchronized for reproducibility.

---

**Maintainer**: Emanuel Lorenz  
**Lab**: NTNU Vizlab / EEG-MoCap

