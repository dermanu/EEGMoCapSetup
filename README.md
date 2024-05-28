# EEGMoCapSetup
## Overview
This repro includes all required software to run the experiment for the EEGMoCap study. 

## Camera
This folder includes the script to record video from two FLIR cameras synchronised to a TTL input. It further sends out the currently recorded frame number via LSL to the local network.

## EEG/LiveAmpLSLStreamDelay
This folder includes a modified version of the BrainProducts LiveAmpLSLStream client. We added a certain delay to wait a couple of seconds so the the other streams and the LabRecorded can be started after the LiveAmp outputs the sync TTL signal. It further includes the electrode configuration file.

## Qualisys
This includes a slightly modified version of the Qulisys LSL client. This allows the client to wait for the first packaged beeing send by Qualisys QTM.

## Recorder 
This includes the standard LSLRecorded and they used config file.
