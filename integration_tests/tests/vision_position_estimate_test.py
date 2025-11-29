#!/usr/bin/env python3
"""
Example: Send VISION_POSITION_ESTIMATE to a MAVLink-enabled autopilot
Requires: pip install pymavlink
"""

from pymavlink import mavutil
import time
import math

def test_vision_position_estimate(ardusub_container):
    try:
        # Connect to the vehicle (UDP example; adjust for your setup)
        # For serial: mavutil.mavlink_connection('/dev/ttyUSB0', baud=57600)
        master = mavutil.mavlink_connection('udp:0.0.0.0:14550')

        # Wait for a heartbeat to confirm connection
        print("Waiting for heartbeat...")
        master.wait_heartbeat()
        print(f"Heartbeat from system {master.target_system} component {master.target_component}")

        #lat = 12345
        #lon = 12345
        #alt = 50

        #master.mav.set_gps_global_origin_send(1, lat, lon, alt)
        #master.mav.set_home_position_send(1, lat, lon, alt, 0, 0, 0, [1, 0, 0, 0], 0, 0, 1)

        for i in range(10):
            # Current time in microseconds
            usec = int(time.time() * 1_000_000)

            # Example position (x, y, z) in meters
            x = 1.0
            y = 0.5
            z = -10.0  # NED frame: negative z is up

            # Example orientation (roll, pitch, yaw) in radians
            roll = math.radians(5)   # 5 degrees
            pitch = math.radians(2)  # 2 degrees
            yaw = math.radians(45)   # 45 degrees

            # Send the VISION_POSITION_ESTIMATE message
            master.mav.vision_position_estimate_send(
                usec,   # Timestamp (microseconds, synced to system clock)
                x, y, z,
                roll, pitch, yaw
            )

            print(f"Sent VISION_POSITION_ESTIMATE: pos=({x:.2f},{y:.2f},{z:.2f}) "
                  f"att=({roll:.2f},{pitch:.2f},{yaw:.2f})")

            time.sleep(0.1)  # Send at 10 Hz

    except KeyboardInterrupt:
        print("\nStopped by user.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()


