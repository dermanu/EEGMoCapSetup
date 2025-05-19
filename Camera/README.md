# ParaSpinVideoAcq

Python-based parallel video acquisition tool for FLIR (Point Grey) cameras using the Spinnaker SDK. This script supports synchronized multi-camera recording, with LSL event streaming and hardware trigger configuration.

## Features

- Parallel video recording using `multiprocessing`
- FLIR/Spinnaker camera control via `EasyPySpin`
- Hardware trigger configuration (master/slave or external, e.g., Qualisys)
- Real-time frame timestamp streaming via LSL
- Configurable camera parameters
- GPU-accelerated H.264 encoding using FFmpeg (`h264_nvenc`)
- Currently set up for 6 cameras; modify as needed for 2

## Requirements

- **OS**: Windows 10 (tested)
- **Python**: 3.8+
- **Hardware**: FLIR cameras (USB3/Blackfly recommended), trigger sync source (optional)

## Dependencies

Install required Python packages:
```bash
pip install numpy opencv-python EasyPySpin imageio sk-video pylsl keyboard
```

Also:
- [Install FLIR Spinnaker SDK](https://www.flir.com/products/spinnaker-sdk/) (required)
- Set FFmpeg path in code (currently hardcoded in `skvideo.setFFmpegPath(...)`)

## Setup

1. **Download and install** the Spinnaker SDK from FLIR.
2. **Connect cameras** and verify detection in FLIR SpinView GUI.
3. **Configure camera triggering**:
   - One camera as master, one as slave
   - Optionally use Qualisys as external trigger for both (via GPIO Line 3)
4. **Adjust settings** in `self.settings` if needed.

## Running the Code

The script records synchronized streams from two FLIR cameras. Adjust the number of active `camX` processes in the `__main__` block.

```bash
python ParaVideoAcqBufferEasy_final.py
```

Captured videos are stored in the directory specified under `self.settings['dataFolder']`.

## Output

- `.mp4` video files per camera with encoded timestamps in filenames
- LSL stream per camera (`FrameMarkerN`) containing frame counters

## Notes

- Ensure correct hardware trigger wiring when using external synchronization.
- Adjust exposure, gain, and white balance manually in code if needed.
- Press `Esc` to stop recording.
- Default FPS is 100 Hz; make sure this is supported by your FLIR cameras and the bandwith limitations of your system.
- NVIDIA GeForce grafic cards natively only support encoding of up to 2 cameras streams. 

## To Do

- Modularize configuration
- Implement graceful shutdown (keyboard interrupts)
- Add config file support

---

**Author**: Emanuel Lorenz  
**Lab**: NTNU Vizlab / EEG-MoCap  
