# PID Controller Animation in Python with Matplotlib

This repository contains the Python code to generate an MP4 animation comparing the behavior of Proportional (P), Proportional–Integral (PI), and Proportional–Integral–Derivative (PID) controllers.

The animation visualizes the response of a simple system to a setpoint change for each controller type, highlighting key characteristics such as steady-state error, overshoot, and settling time. It’s designed with a focus on pedagogical clarity, featuring smooth transitions between phases and dynamic axis-limit adjustments.

## Features

* Visual comparison of P, PI, and PID controller responses
* Display of setpoint, system output, and error
* Visualization of the control effort applied
* Animated transitions for titles, descriptions, and phase changes
* Automatic adjustment of Y-axis limits for optimal viewing of each phase
* Code commented in English (with French annotations for key terms)

## Technologies Used

* **Python 3.12.9**
* **Matplotlib**: Plotting and animation (`FuncAnimation`)
* **NumPy**: Numerical computations and array handling
* **FFmpeg**: Required to save the animation as MP4 (must be installed separately and available in your system PATH)

## Prerequisites

Before running the script, ensure you have:

1. Python 3.6 or newer
2. The required Python libraries:

   ```bash
   pip install numpy matplotlib
   ```
3. FFmpeg: See installation instructions for your OS at [ffmpeg.org](https://ffmpeg.org/download.html)

## Usage

1. Clone this repository:

   ```bash
   git clone https://github.com/bkoensgen/python-pid-animation.git
   ```
2. Change into the project directory:

   ```bash
   cd python-pid-animation
   ```
3. Run the main Python script (e.g., `pid_animation.py`):

   ```bash
   python pid_animation.py
   ```

   An MP4 video file will be generated in the current directory.

## Key Parameters

You can adjust the main simulation and animation settings at the top of the script:

* `SETPOINT` – Target value for the system
* `INITIAL_POSITION` – Starting position of the system
* `PHASE_DURATION` – Simulation time per controller phase
* PID gains (`Kp`, `Ki`, `Kd`) defined in the `configs_pid` list
* Animation settings like `FPS` and `PAUSE_FRAMES`

## License

This project is released under the MIT License.

---

Feel free to reach out on [LinkedIn](https://www.linkedin.com/in/benjamin-koensgen-6459711b1) if you have any questions or suggestions!
