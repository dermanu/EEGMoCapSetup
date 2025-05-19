# LabStreamingLayer LabRecorder

This folder contains the **LabRecorder** application for LabStreamingLayer (LSL). It is likely based on an older version but remains functional.

---

## Overview

LabRecorder listens for active LSL streams on the network and records them into a single `.xdf` file. It is typically used for synchronized acquisition of data streams such as EEG, motion capture, video, and triggers.

---

## Key Features

- Scans the network for all available LSL streams
- Records synchronized data to `.xdf` format
- Supports configuration via XML to reduce operator errors

---

## Configuration

A configuration file (`.xml`) should be created to:

- Specify required streams
- Define the output path for the `.xdf` file
- Enable optional features like remote control or auto-start

> ⚠️ The official documentation is sparse. However, the tool is straightforward and mostly self-explanatory.

---

## Notes

- Ensure all required LSL streams are active **before** launching the recorder.
- Using an XML configuration is **highly recommended** to prevent errors during data collection.
- Although outdated, this version remains sufficient for typical EEG and MoCap experiments.

---

**Maintainer**: Emanuel Lorenz  
**Lab**: NTNU Vizlab / EEG-MoCap  

