This folder includes information on how the marker-based system Qualisys works, a Qualisys config file, and the Labstreaming Layer Client for Qualisys.
In general:
1. You must start Qualisys and check if all cameras are recognized and the setup is correct. If not, find the QDS (Qualisys DHCP Server) in the taskbar. Reboot the cameras and/or check the Network configurations.
2. Open the Qualisys Track Manager (QTM) and load the respective Qualysis project file (I think we make a new one). 
3. Check in the "Tools" -> "Project option" if the "Connection" is correct, "Linearization" was done, the "Calibration" option is set correctly, and "Timing" and "Camera setting" are set in a way that they take an external trigger (TTL).
4. Then, create an AIM model for the markers (talk with me).
5. The software automatically sends the marker positions to the Qualisys LSL client if everything is set correctly upon opening.