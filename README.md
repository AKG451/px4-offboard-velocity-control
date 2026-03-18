# PX4 SITL Autonomous OFFBOARD Control & Custom Gazebo Environment

## Architecture Overview

Standard UAV waypoint navigation typically relies on Ground Control Stations (GCS) like **QGroundControl**, which abstract away underlying flight dynamics and make custom autonomous logic difficult to implement.

This repository demonstrates a **fully autonomous PX4 simulation pipeline** that bypasses external GCS software and directly controls the UAV through MAVLink.

The system consists of two primary components:

### 1. Custom Physics Environment
A custom **Gazebo `.world` file** modeling a realistic suburban test environment including:

- Static obstacles
- Terrain elevation mapping
- Custom collision meshes
- Structured navigation space for waypoint testing

### 2. Autonomous Control Node
A **Python-based autonomous controller** that communicates directly with **PX4 SITL** using `pymavlink`.

Key characteristics:

- No MAVROS dependency
- No QGroundControl required
- Direct MAVLink command interface
- OFFBOARD mode control
- Velocity-based navigation

Instead of sending absolute position targets, the controller computes and publishes **velocity vectors** in the `LOCAL_POSITION_NED` frame to guide the UAV toward logical waypoints.

---

# Core Dependencies

The following software stack is required:

- **PX4 Autopilot (SITL)**
- **Gazebo Classic (v11)**
- **Python 3.x**
- **pymavlink**

> Note: This architecture intentionally excludes **MAVROS** and **QGroundControl** during operation to ensure zero external interference with the control pipeline.

---

# Execution Pipeline

## 1. Launch the Custom Simulation Environment

Ensure your PX4 SITL environment is sourced.

Export the custom world file before starting the build:

```bash
export PX4_SITL_WORLD=obstacle make px4_sitl gazebo-classic
```

This launches:

- PX4 SITL
- Gazebo Classic
- MAVLink communication bridge

---

## 2. Execute the Autonomous Controller

Once the simulation environment is running and MAVLink messages are being broadcast, launch the control node in a new terminal.

```bash
python3 fly.py
```

---

# Expected Behavior

After execution the following sequence occurs automatically:

1. The script establishes a **direct MAVLink connection** to the PX4 SITL instance.
2. The UAV **arms automatically**.
3. The controller **forces OFFBOARD mode**.
4. Continuous **velocity setpoints** are published to navigate the UAV along the predefined `FLIGHT_PATH`.
5. When no motion is required the UAV **maintains hover** by publishing a zero velocity vector.
6. Upon mission completion or keyboard interrupt, the script executes a **safe landing sequence** using:

```
MAV_CMD_NAV_LAND
```

---
# License

This project is provided for research and educational purposes.