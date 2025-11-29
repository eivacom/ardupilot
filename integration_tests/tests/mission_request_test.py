#!/usr/bin/env python3
"""
Upload a mission to an ArduPilot vehicle using pymavlink.
Tested with ArduPilot SITL and real hardware.
"""

from pymavlink import mavutil
import time
import sys

def test_mission_request(ardusub_container):

    # -------------------------------
    # Mission definition (example)
    # -------------------------------
    # Each mission item is a tuple:
    # (seq, frame, command, current, autocontinue, param1..param7)
    # param7 is usually latitude, longitude, altitude for NAV_WAYPOINT
    mission_items = [
        # Takeoff to 10m
        (0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT,
        mavutil.mavlink.MAV_CMD_NAV_TAKEOFF, 0, 1,
        0, 0, 0, 0, 33, -118, -10),

        # Waypoint 1
        (1, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT,
        mavutil.mavlink.MAV_CMD_NAV_WAYPOINT, 0, 1,
        0, 0, 0, 0, 50, -150, -10),

        # Waypoint 2
        (2, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT,
        mavutil.mavlink.MAV_CMD_NAV_WAYPOINT, 0, 1,
        0, 0, 0, 0, 60, -160, -10),

        # Return to launch
        (3, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT,
        mavutil.mavlink.MAV_CMD_NAV_RETURN_TO_LAUNCH, 0, 1,
        0, 0, 0, 0, 0, 0, 0)
    ]

    # -------------------------------
    # Connect to the vehicle
    # -------------------------------
    # Example: SITL: 'udp:127.0.0.1:14550'
    #          Serial: '/dev/ttyUSB0', baud=57600
    connection_str = 'udp:127.0.0.1:14550'
    master = mavutil.mavlink_connection(connection_str)

    # Wait for heartbeat to confirm connection
    print("Waiting for heartbeat...")
    master.wait_heartbeat()
    print(f"Heartbeat from system {master.target_system} component {master.target_component}")

    # -------------------------------
    # Clear existing mission
    # -------------------------------
    print("Clearing existing mission...")
    master.mav.mission_clear_all_send(master.target_system, master.target_component)

    # Wait a moment to ensure clear is processed
    time.sleep(1)

    # -------------------------------
    # Send mission count
    # -------------------------------
    mission_count = len(mission_items)
    print(f"Sending mission count: {mission_count}")
    master.mav.mission_count_send(master.target_system, master.target_component, mission_count)

    # -------------------------------
    # Send mission items
    # -------------------------------
    for item in mission_items:
        seq, frame, command, current, autocontinue, p1, p2, p3, p4, lat, lon, alt = item

        # Wait for MISSION_REQUEST for this seq
        msg = master.recv_match(type=['MISSION_REQUEST', 'MISSION_REQUEST_INT'], blocking=True, timeout=10)
        if not msg:
            print(f"Timeout waiting for MISSION_REQUEST for seq {seq}")
            sys.exit(1)

        print(f"Sending mission item {seq}")
        master.mav.mission_item_send(
            master.target_system,
            master.target_component,
            seq,
            frame,
            command,
            current,
            autocontinue,
            p1, p2, p3, p4,
            lat, lon, alt
        )

    # -------------------------------
    # Wait for mission ack
    # -------------------------------
    msg = master.recv_match(type='MISSION_ACK', blocking=True, timeout=10)
    if msg:
        print(f"Mission upload ACK: {msg.type}")
    else:
        print("No MISSION_ACK received!")

    print("Mission upload complete.")

    # --- Parameters for NAV_MISSION_START ---
    first_item = 0   # First mission item index to execute
    last_item = 0    # Last mission item index (0 means execute until end)

    try:
        # Send the NAV_MISSION_START command
        master.mav.mission_set_current_send(
            master.target_system,
            master.target_component,
            first_item
        )

        master.mav.command_long_send(
            master.target_system,            # target_system
            master.target_component,         # target_component
            mavutil.mavlink.MAV_CMD_MISSION_START,  # command
            0,                               # confirmation
            first_item,                      # param1: first item index
            last_item,                       # param2: last item index
            0, 0, 0, 0, 0                     # unused params
        )

        print(f"Sent NAV_MISSION_START from item {first_item} to {last_item or 'end'}.")

    except Exception as e:
        print(f"Failed to send NAV_MISSION_START: {e}")
        sys.exit(1)
