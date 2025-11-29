"""
Example of how to send GPS_INPUT messages to autopilot
"""

import time
import math
# Import mavutil
from pymavlink import mavutil


# GPS_TYPE need to be MAV
def test_gps_input(ardusub_container):

    print("getting mavlink connection")
    # Create the connection
    master = mavutil.mavlink_connection('udp:0.0.0.0:14550')
    # Wait a heartbeat before sending commands
    print("waiting for heartbeat")
    master.wait_heartbeat()
    #master.mav.gps_input_send(
    #    0,  # Timestamp (micros since boot or Unix epoch)
    #    0,  # ID of the GPS for multiple GPS inputs
        # Flags indicating which fields to ignore (see GPS_INPUT_IGNORE_FLAGS enum).
        # All other fields must be provided.
    #    (mavutil.mavlink.GPS_INPUT_IGNORE_FLAG_VEL_HORIZ |
    #     mavutil.mavlink.GPS_INPUT_IGNORE_FLAG_VEL_VERT |
    #     mavutil.mavlink.GPS_INPUT_IGNORE_FLAG_SPEED_ACCURACY),
    #    0,  # GPS time (milliseconds from start of GPS week)
    #    0,  # GPS week number
    #    3,  # 0-1: no fix, 2: 2D fix, 3: 3D fix. 4: 3D with DGPS. 5: 3D with RTK
    #    0,  # Latitude (WGS84), in degrees * 1E7
    #    0,  # Longitude (WGS84), in degrees * 1E7
    #    0,  # Altitude (AMSL, not WGS84), in m (positive for up)
    #    1,  # GPS HDOP horizontal dilution of position in m
    #    1,  # GPS VDOP vertical dilution of position in m
    #    0,  # GPS velocity in m/s in NORTH direction in earth-fixed NED frame
    #    0,  # GPS velocity in m/s in EAST direction in earth-fixed NED frame
    #    0,  # GPS velocity in m/s in DOWN direction in earth-fixed NED frame
    #    0,  # GPS speed accuracy in m/s
    #    0,  # GPS horizontal accuracy in m
    #    0,  # GPS vertical accuracy in m
    #    7   # Number of satellites visible.
    #)

    # Current time in microseconds
    usec = int(time.time() * 1_000_000)

    # Example position (x, y, z) in meters
    x = 56.067113
    y = 9.981787
    z = -100.0  # NED frame: negative z is up

    # Example orientation (roll, pitch, yaw) in radians
    roll = math.radians(5)   # 5 degrees
    pitch = math.radians(2)  # 2 degrees
    yaw = math.radians(45)   # 45 degrees

    try:
        
        print("sending GPS_INPUT message")

        master.mav.gps_input_send(
            usec,  # Timestamp since epoch in microseonds
            0,  # GPS ID
                        # Flags indicating which fields to ignore
            (mavutil.mavlink.GPS_INPUT_IGNORE_FLAG_HDOP |
            mavutil.mavlink.GPS_INPUT_IGNORE_FLAG_VDOP  |
            mavutil.mavlink.GPS_INPUT_IGNORE_FLAG_VEL_HORIZ |
            mavutil.mavlink.GPS_INPUT_IGNORE_FLAG_VEL_VERT |
            mavutil.mavlink.GPS_INPUT_IGNORE_FLAG_SPEED_ACCURACY |
            mavutil.mavlink.GPS_INPUT_IGNORE_FLAG_HORIZONTAL_ACCURACY |
            mavutil.mavlink.GPS_INPUT_IGNORE_FLAG_VERTICAL_ACCURACY),
            0,  # GPS time (milliseconds from start of GPS week)
            0,  # GPS week number
            4,  # 3-D Fix
            int(x * 1E7),  # Latitude, in degrees * 1E7
            int(y * 1E7),  # Longitude, in degrees * 1E7
            int(z),  # Altitude above sea level (N/A)
            0,  # GPS HDOP horizontal dilution of position in m. Unknown so set to uint16 max
            0,  # GPS VDOP vertical dilution of position in m. Unknown so set to uint16 max
            0,  # GPS velocity in m/s in NORTH direction in earth-fixed NED frame. Ignored
            0,  # GPS velocity in m/s in EAST direction in earth-fixed NED frame. Ignored
            0,  # GPS velocity in m/s in DOWN direction in earth-fixed NED frame. Ignored
            0,  # GPS speed accuracy in m/s. Need to convert from mm/s. Ignored
            0,  # GPS horizontal accuracy in m. Ignored
            0.1,  # GPS vertical accuracy in m
            12,   # Number of satellites visible
            int(yaw) # Yaw, in degrees * 1E2
        )
    except Exception as e:
        print(f"Cannot send GPS Input message to ROV : ${e}")
