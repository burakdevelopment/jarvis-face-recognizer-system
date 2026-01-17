# 🛡️ Jarvis Face Recognizer System JarvisFRS

![Python](https://img.shields.io/badge/Python-3.8%2B-blue) ![Security](https://img.shields.io/badge/Security-RAM%20Only-green) ![License](https://img.shields.io/badge/License-MIT-orange) ![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Raspberry%20Pi-grey)

<img width="736" height="597" alt="image" src="https://github.com/user-attachments/assets/4c66b73b-fdc0-4289-a6cb-8ca926b98e30" />

**JarvisFRS** is a privacy-focused, real-time face recognition and greeting system designed for secure environments (schools, offices, private facilities). 

Unlike traditional surveillance systems, **JarvisFRS operates strictly in Volatile Memory (RAM)**. It creates temporary biometric profiles for visitors that are automatically destroyed when the system shuts down, ensuring compliance with strict privacy regulations (GDPR/KVKK).

## 🌟 Key Features

### 🔒 Privacy & Security First
* **Volatile Memory Storage:** No face data or images are ever written to the hard disk. All biometric encodings reside in RAM.
* **Secure Audio Handling:** Generated speech files are cached in memory using **SHA-256** hashing, preventing file system clutter and data persistence.
* **Automatic Data Purge:** Upon termination, all visitor data is instantly wiped.

### 🧠 Intelligent Logic
* **Smart Crowd Greeting:** Detects groups of people and issues a **single** welcome message ("Hello, welcome to our school...") to avoid repetitive audio spam. It resets only when the area is clear.
* **5-Second Registration Rule:** To prevent false positives, a visitor must look at the camera stably for 5 seconds before being registered as a "Guest" in the temporary session.
* **Anti-Jitter Tracking:** Includes a movement threshold algorithm to maintain tracking even if the visitor moves their head slightly.

### ⚡ Performance Optimized
* **Frame Skipping:** Processes facial recognition every N frames (configurable) to reduce CPU usage by up to 60%.
* **Dynamic Resolution:** Processing is done on a scaled-down frame, while the GUI output is rendered at a crisp **1184x659** resolution.
* **Async Audio:** Audio playback runs on separate threads to ensure the video feed never freezes.

## 🛠️ Hardware Requirements

* **PC:** Windows, macOS, or Linux with Python 3.x installed.
* **Raspberry Pi:** Model 4B (4GB/8GB) or Pi 5 recommended.
* **Camera:** USB Webcam or Raspberry Pi Camera Module.
* **Internet:** Required only for the *initial* generation of speech synthesis (gTTS).

## 📦 Installation

### 1. Clone the Repository and Install Dependencies

```bash
git clone https://github.com/burakdevelopment/jarvis-face-recognizer-system
cd jarvis-face-recognizer-system
pip install -r requirements.txt
```


### 2. Install Dependencies (Raspberry Pi / Linux)

```bash
sudo apt-get update
sudo apt-get install build-essential cmake pkg-config
sudo apt-get install libopenblas-dev liblapack-dev
sudo apt-get install libx11-dev libgtk-3-dev python3-dev
pip3 install -r requirements.txt
```

## 🚀 Usage

```bash
python main.py
```
* To Quit: Press q on the keyboard while the window is active.
* Note: Since this is a RAM-only system, all registered "Person X" identities will be reset every time you restart the application.

## ⚙️ Configuration

* You can customize the system behavior by editing the Config class in main.py:
```bash
class Config:
    REGISTRATION_TIME_REQ = 5      #seconds required to register a face
    MOVEMENT_THRESHOLD = 50        #sensitivity for head movement
    MSG_WELCOME = "Hello..."       #custom greeting text
    PROCESS_EVERY_N_FRAMES = 2     #increase to 3 or 4 for slower CPUs (Raspberry Pi)
```

## 🔧 Troubleshooting

* "dlib" Installation Fail: Make sure you have installed CMake (pip install cmake) and, on Windows, Visual Studio Build Tools (C++).
* Audio Stuttering: If running on very old hardware, increase PROCESS_EVERY_N_FRAMES to 3.
* Camera Not Opening: Check CAMERA_INDEX = 0. Try changing it to 1 or 2 if you have multiple cameras.

## 📜 License

**This project is licensed under the MIT License - see the LICENSE file for details.**
