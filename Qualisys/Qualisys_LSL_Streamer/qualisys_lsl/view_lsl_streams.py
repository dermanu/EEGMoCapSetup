import pylsl

streams = pylsl.resolve_streams()

for stream in streams:
    print(f"Stream name: {stream.name()}")
    print(f"Channel count: {stream.channel_count()}")
    print(f"Type: {stream.type()}")
    print()

inlet = pylsl.StreamInlet(streams[0])
while True:
    sample, _ = inlet.pull_sample()
    print(sample)
    print(_)