import time
import pylsl

# Create an LSL outlet
info = pylsl.StreamInfo("MyStream", "Numbers", 1, 1, pylsl.cf_float32, "my_unique_identifier")
outlet = pylsl.StreamOutlet(info)

try:
    while True:
        # Send the number 1 as a sample
        outlet.push_sample([1.0])

        # Sleep for 50 milliseconds
        time.sleep(0.05)
except KeyboardInterrupt:
    pass
