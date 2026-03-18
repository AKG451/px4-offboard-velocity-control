import time
import math
from pymavlink import mavutil

DRONE_CONNECTION = 'udpin:localhost:14540'
TAKEOFF_HEIGHT = 4.5                      
FLIGHT_SPEED = 3.0                          
ARRIVAL_DISTANCE = 1.0                  
FLIGHT_PATH = [
    [0, 35, -3.5],
    [0, 25, -3.5],
    [0, 10, -3.5],
    [0, 5, -1.5],
    [0, 0, 0]
]
class DronePilot:
    def __init__(self):
        print("Waking up the drone...")
        self.drone = mavutil.mavlink_connection(DRONE_CONNECTION)
        self.drone.wait_heartbeat()
        print("Connection established! Ready for instructions.")
        self.current_location = [0, 0, 0]
    def update_location(self):
        message = self.drone.recv_match(type='LOCAL_POSITION_NED', blocking=False)
        if message:
            self.current_location = [message.x, message.y, message.z]
        return self.current_location
    def set_speed(self, speed_x, speed_y, speed_z):
        ignore_everything_but_velocity = 3527
        self.drone.mav.set_position_target_local_ned_send(
            0,                          
            self.drone.target_system,  
            self.drone.target_component, 
            mavutil.mavlink.MAV_FRAME_LOCAL_NED, 
            ignore_everything_but_velocity,                  
            0, 0, 0,                    
            speed_x, speed_y, speed_z,                 
            0, 0, 0,                    
            0, 0                        
        )
    def wake_up_motors(self):
        print("Spinning up the propellers...")
        self.drone.mav.command_long_send(
            self.drone.target_system,
            self.drone.target_component,
            mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
            0, 1, 0, 0, 0, 0, 0, 0 
        )
        self.drone.motors_armed_wait()
        print("Propellers are spinning!")
    def take_control(self):
        print("Taking computer control...")
        for _ in range(10):
            self.set_speed(0, 0, 0)
            time.sleep(0.1)
        self.drone.mav.command_long_send(
            self.drone.target_system,
            self.drone.target_component,
            mavutil.mavlink.MAV_CMD_DO_SET_MODE,
            0, 1, 6, 0, 0, 0, 0, 0 
        )
        print("Computer is now flying the drone.")
    def start_mission(self):
        try:
            self.take_control()
            self.wake_up_motors()
            print(f"Lifting off to {TAKEOFF_HEIGHT} meters...")
            while self.current_location[2] > -TAKEOFF_HEIGHT + 0.5:
                self.update_location()
                self.set_speed(0, 0, -1.0) 
                time.sleep(0.1)
            print("Reached altitude. Pausing to stabilize...")
            for _ in range(20):
                self.set_speed(0, 0, 0)
                time.sleep(0.1)
            for index, destination in enumerate(FLIGHT_PATH):
                print(f"Heading to destination {index + 1}...")
                while True:
                    current_pos = self.update_location()
                    dist_x = destination[0] - current_pos[0]
                    dist_y = destination[1] - current_pos[1]
                    dist_z = destination[2] - current_pos[2]
                    distance_remaining = math.sqrt(dist_x**2 + dist_y**2 + dist_z**2)
                    if distance_remaining < ARRIVAL_DISTANCE:
                        print(f"Arrived at destination {index + 1}!")
                        break
                    speed_x = (dist_x / distance_remaining) * FLIGHT_SPEED
                    speed_y = (dist_y / distance_remaining) * FLIGHT_SPEED
                    speed_z = (dist_z / distance_remaining) * FLIGHT_SPEED
                    self.set_speed(speed_x, speed_y, speed_z)
                    time.sleep(0.1)
            print("Mission accomplished. Coming down for a landing...")
            while self.current_location[2] < -0.5: 
                self.update_location()
                self.set_speed(0, 0, 1.0) 
                time.sleep(0.1)
            print("Touchdown! Shutting down the motors.")
            self.drone.mav.command_long_send(
                self.drone.target_system,
                self.drone.target_component,
                mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
                0, 0, 0, 0, 0, 0, 0, 0 
            )
        except KeyboardInterrupt:
            print("\nMission aborted! Hitting the brakes and landing right here...")
            for _ in range(20):
                self.set_speed(0, 0, 0)
                time.sleep(0.1)
            self.drone.mav.command_long_send(
                self.drone.target_system,
                self.drone.target_component,
                mavutil.mavlink.MAV_CMD_NAV_LAND,
                0, 0, 0, 0, 0, 0, 0, 0
            )
if __name__ == "__main__":
    pilot = DronePilot()
    pilot.start_mission()