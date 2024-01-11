import struct
import sys

# Your data and format string
command = 1
track_time = 2
track_number = 3
pos_current = [4, 5, 6]
theta_current = 7.0

frame_data = struct.pack('<qqqqddddddddddddqqqdddddddddddd',
                         int(command), int(track_time), int(track_number), 0,
                         pos_current[0], pos_current[1], pos_current[2],
                         0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                         0.0, 0, 0, 0, 0.0, theta_current, 0.0,
                         0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)

# Get the length in bytes
length_in_bytes = len(frame_data)
frame_length = sys.getsizeof(frame_data)
print("Number of bytes:", length_in_bytes)
print("Number of bytes:", frame_length)