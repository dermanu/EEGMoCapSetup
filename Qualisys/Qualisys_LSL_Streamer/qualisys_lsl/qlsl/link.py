"""
    Stream 3D and 6DOF data from QTM and pass it through an LSL outlet.
"""

import asyncio
from enum import Enum
import logging
import time

from pylsl import StreamInfo, StreamOutlet
import qtm
from qtm import QRTEvent

from qlsl.config import (
    Config,
    new_lsl_stream_info,
    parse_qtm_parameters,
    qtm_packet_to_lsl_sample,
)

LOG = logging.getLogger("qlsl")
QTM_DEFAULT_PORT = 22223
QTM_DEFAULT_VERSION = "1.19"

# The provided data
data = [
    ('general', {'frequency': 100.0, 'cameras': [
        {'id': '1', 'model': 'Oqus 500 Plus', 'serial': '20143', 'mode': 'Marker', 'video_frequency': '10', 'position':
            {'x': 103.696578, 'y': -2051.682288, 'z': 2150.600161}},
        {'id': '2', 'model': 'Oqus 500 Plus', 'serial': '20144', 'mode': 'Marker', 'video_frequency': '10', 'position':
            {'x': -2432.191941, 'y': -1917.871065, 'z': 2171.698165}},
        {'id': '3', 'model': 'Oqus 500 Plus', 'serial': '20206', 'mode': 'Marker', 'video_frequency': '10', 'position':
            {'x': -2415.537383, 'y': 552.566729, 'z': 2138.846453}},
        {'id': '4', 'model': 'Oqus 300', 'serial': '10230', 'mode': 'Marker', 'video_frequency': '10', 'position':
            {'x': 2626.424314, 'y': 2759.402127, 'z': 2111.338128}},
        {'id': '5', 'model': 'Oqus 300', 'serial': '10236', 'mode': 'Marker', 'video_frequency': '10', 'position':
            {'x': 2655.502945, 'y': 259.301673, 'z': 616.446892}},
        {'id': '6', 'model': 'Oqus 500 Plus', 'serial': '20207', 'mode': 'Marker', 'video_frequency': '10', 'position':
            {'x': 658.339528, 'y': 2784.126949, 'z': 2118.82703}},
        {'id': '7', 'model': 'Oqus 500 Plus', 'serial': '20145', 'mode': 'Marker', 'video_frequency': '10', 'position':
            {'x': -2365.869915, 'y': 2846.646847, 'z': 2112.201511}},
        {'id': '8', 'model': 'Oqus 300', 'serial': '10229', 'mode': 'Marker', 'video_frequency': '10', 'position':
            {'x': 2596.850831, 'y': -1980.217602, 'z': 2174.377738}}]}),
    ('the_3d', {
        'markers': ['RFIN', 'LFIN', 'LWRA', 'LWRB', 'LELB', 'LELA', 'LSHO', 'RSHO', 'RELB', 'RELA', 'RWRB', 'RWRA']}),
    ('the_6d', {'bodies': [], 'euler': {'first': 'Roll', 'second': 'Pitch', 'third': 'Yaw'}})
]

class State(Enum):
    INITIAL = 1
    WAITING = 2
    STREAMING = 3
    STOPPED = 4

class Link:
    def __init__(self, host, port, on_state_changed, on_error):
        self.host = host
        self.port = port
        self._on_state_changed = on_state_changed
        self._on_error = on_error

        self.state = State.INITIAL
        self.conn = None
        self.packet_count = 0
        self.start_time = 0
        self.stop_time = 0
        self.reset_stream_context()
        self.opened = False
    
    def reset_stream_context(self):
        self.config = Config()
        self.receiver_queue = None
        self.receiver_task = None
        self.lsl_info = None
        self.opened = False
        self.lsl_outlet = None
    
    def set_state(self, state):
        prev_state = self.state
        self.state = state
        self.on_state_changed(self.state)
        return prev_state
    
    def is_streaming(self):
        return self.state == State.STREAMING
    
    def is_waiting(self):
        return self.state == State.WAITING

    def is_stopped(self):
        return self.state in [State.INITIAL, State.STOPPED]
    
    def elapsed_time(self):
        if self.start_time > 0:
            return time.time() - self.start_time
        return 0
    
    def final_time(self):
        if self.stop_time > self.start_time:
            return self.stop_time - self.start_time
        return 0
    
    def on_state_changed(self, new_state):
        if self._on_state_changed:
            self._on_state_changed(new_state)
    
    def on_error(self, msg):
        if self._on_error:
            self._on_error(msg)
    
    def on_event(self, event):
        start_events = [
            QRTEvent.EventRTfromFileStarted,
            QRTEvent.EventCalibrationStarted,
            QRTEvent.EventCaptureStarted,
            QRTEvent.EventConnected,
        ]
        stop_events = [
            QRTEvent.EventRTfromFileStopped,
            QRTEvent.EventCalibrationStopped,
            QRTEvent.EventCaptureStopped,
            QRTEvent.EventConnectionClosed,
        ]
        if self.state == State.WAITING:
            if event in start_events:
                if not self.opened:
                    self.open_lsl_stream_outlet()

                asyncio.ensure_future(self.start_stream())
            else:
                self.open_lsl_stream_outlet()
        elif self.state == State.STREAMING:
            if event in stop_events:
                asyncio.ensure_future(self.stop_stream())
        
    def on_disconnect(self, exc):
        if self.is_stopped(): return
        if self.conn:
            msg = "Disconnected from QTM"
            LOG.error(msg)
            self.err_disconnect(msg)
        if exc:
            LOG.debug("link: on_disconnect: {}".format(exc))

    def convert_to_config(self, data):
        config = Config()

        for section, section_data in data:
            if section == 'general':
                config.general = {
                    'frequency': section_data['frequency'],
                    'cameras': section_data['cameras']
                }
            elif section == 'the_3d':
                config.the_3d = {
                    'markers': section_data['markers']
                }
            elif section == 'the_6d':
                config.the_6d = {
                    'bodies': section_data['bodies'],
                    'euler': section_data['euler']
                }

        return config

    def open_lsl_stream_outlet(self):
        #packet = await self.conn.get_parameters(
        #    parameters=["general", "3d", "6d"],
        #)
        #config = parse_qtm_parameters(packet.decode("utf-8"))
        self.config = self.convert_to_config(data)
        LOG.info(f"Open stream: {vars(self.config)}")
        self.lsl_info = new_lsl_stream_info(self.config, self.host, self.port)
        self.lsl_outlet = StreamOutlet(info=self.lsl_info, max_buffered=180)
        self.opened = True
    
    def err_disconnect(self, err_msg):
        asyncio.ensure_future(self.shutdown(err_msg))

    async def shutdown(self, err_msg=None):
        try:
            LOG.debug("link: shutdown enter")
            if self.state == State.STREAMING:
                await self.stop_stream()
            if self.conn and self.conn.has_transport():
                self.conn.disconnect()
            self.conn = None
        finally:
            self.set_state(State.STOPPED)
            if err_msg:
                self.on_error(err_msg)
            LOG.debug("link: shutdown exit")

    async def stop_stream(self):
        if self.conn and self.conn.has_transport():
            try:
                await self.conn.stream_frames_stop()
            except qtm.QRTCommandException as ex:
                LOG.error("QTM: stream_frames_stop exception: " + str(ex))
        if self.receiver_queue:
            self.receiver_queue.put_nowait(None)
            await self.receiver_task
        self.reset_stream_context()
        if self.state == State.STREAMING:
            LOG.info("Stream stopped")
            self.stop_time = time.time()
            self.set_state(State.WAITING)


    
    async def start_stream(self):
        try:
            packet = await self.conn.get_parameters(
                parameters=["general", "3d", "6d"],
            )
            config = parse_qtm_parameters(packet.decode("utf-8"))
            if config.channel_count() == 0:
                msg = "Missing QTM data: markers {} rigid bodies {}" \
                    .format(config.marker_count(), config.body_count())
                LOG.info(msg)
                self.err_disconnect("No 3D or 6DOF data available from QTM")
                return
            attrs = vars(config)
            LOG.info(config)
            LOG.info(vars(config))
            for item in attrs.items():
                LOG.info(item)

            #self.config = self.convert_to_config(data)
            #self.config = config
            self.receiver_queue = asyncio.Queue()
            self.receiver_task = asyncio.ensure_future(self.stream_receiver())
            #self.open_lsl_stream_outlet()
            await self.conn.stream_frames(
                components=["3d", "6deuler"],
                on_packet=self.receiver_queue.put_nowait,
            )
            LOG.info("Stream started with {} marker(s) and {} rigid bod(y/ies)".format(
                self.config.marker_count(), self.config.body_count()
            ))
            self.packet_count = 0
            self.start_time = time.time()
            self.set_state(State.STREAMING)
        except asyncio.CancelledError:
            raise
        except qtm.QRTCommandException as ex:
            LOG.error("QTM: stream_frames exception: " + str(ex))
            self.err_disconnect("QTM error: {}".format(ex))
        except Exception as ex:
            LOG.error("link: start_stream exception: " + repr(ex))
            self.err_disconnect("An internal error occurred. See log messages for details.")
            raise ex

    async def stream_receiver(self):
        try:
            LOG.debug("link: stream_receiver enter")
            while True:
                packet = await self.receiver_queue.get()
                if packet is None:
                    break
                sample = qtm_packet_to_lsl_sample(packet)
                if len(sample) != self.config.channel_count():
                    msg = ("Stream canceled: "
                        "sample length {} != channel count {}") \
                        .format(len(sample), self.config.channel_count())
                    LOG.error(msg)
                    self.err_disconnect(("Stream canceled: "
                        "QTM stream data inconsistent with LSL metadata"))
                else:
                    self.packet_count += 1
                    self.lsl_outlet.push_sample(sample)
        except asyncio.CancelledError:
            raise
        except Exception as ex:
            LOG.error("link: stream_receiver exception: " + repr(ex))
            self.err_disconnect("An internal error occurred. See log messages for details.")
            raise
        finally:
            LOG.debug("link: stream_receiver exit")

class LinkError(Exception):
    pass

async def init(
    qtm_host,
    qtm_port=QTM_DEFAULT_PORT,
    qtm_version=QTM_DEFAULT_VERSION,
    on_state_changed=None,
    on_error=None
):
    LOG.debug("link: init enter")
    link = Link(qtm_host, qtm_port, on_state_changed, on_error)
    try:
        link.conn = await qtm.connect(
            host=qtm_host,
            port=qtm_port,
            version=qtm_version,
            on_event=link.on_event,
            on_disconnect=link.on_disconnect,
        )
        if link.conn is None:
            msg = ("Failed to connect to QTM "
                "on '{}:{}' with protocol version '{}'") \
                .format(qtm_host, qtm_port, qtm_version)
            LOG.error(msg)
            raise LinkError(msg)
        try:
            link.set_state(State.WAITING)
            await link.conn.get_state()
        except qtm.QRTCommandException as ex:
            LOG.error("QTM: get_state exception: " + str(ex))
            raise LinkError("QTM error: {}".format(ex))
    except:
        await link.shutdown()
        raise
    finally:
        LOG.debug("link: init exit")
    return link
