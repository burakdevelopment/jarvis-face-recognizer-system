# JARVIS Face Recognizer System

**AI-Powered Smart Door & Face Recognition Security System**

**JARVIS Face Recognizer System** is a professional-grade, real-time face recognition security system designed for smart door and access control applications.
It leverages **Computer Vision** and **Deep Learning** techniques to detect, recognize, and interact with visitors in real time.

The system distinguishes between **known residents** and **unknown visitors**, provides **natural voice feedback** using **Google Text-to-Speech (gTTS)**, and includes an intelligent **automatic face registration workflow**.

![image1](https://github.com/user-attachments/assets/16c152fb-4e74-4e46-a0b0-3e370a9b7d1f)
---
![image2](https://github.com/user-attachments/assets/6e4552ed-7318-4683-9c7f-161491c6235c)

**Repository:**
[https://github.com/burakdevelopment/jarvis-face-recognizer-system](https://github.com/burakdevelopment/jarvis-face-recognizer-system)

---

## 🌟 Key Features

### 🔍 Face Recognition

* Real-time face detection and recognition
* Uses **HOG (Histogram of Oriented Gradients)** for fast detection
* Optimized for low-power devices (Raspberry Pi)

### 🔊 Smart Audio Feedback

* Natural voice output via **Google Text-to-Speech (gTTS)**
* Asynchronous audio processing (no video freezing)
* Local **audio caching** for offline use after first generation

### 🧠 Intelligent Visitor Registration

* Automatic detection of unknown visitors
* Camera-facing prompt with visual countdown
* Movement-tolerant registration logic
* High-quality face crop saving

### 👥 Multi-Person Logic

* Unknown visitors are prioritized
* Handles multiple faces in the same frame

### ⚡ Performance Optimizations

* Frame skipping to reduce CPU load
* Dynamic frame scaling for higher FPS
* Raspberry Pi 4 / 5 compatible

---

## 🛠️ Hardware Requirements

* **PC:** Any system with Python 3.x
* **Raspberry Pi:** 4B (4GB / 8GB recommended) or Pi 5
* **Camera:** USB Webcam or Raspberry Pi Camera Module
* **Audio:** 3.5mm jack or USB speakers
* **Network:** Required only for first-time TTS generation

---

## 📦 Installation

### Clone Repository

```bash
git clone https://github.com/burakdevelopment/jarvis-face-recognizer-system.git
cd jarvis-face-recognizer-system
```

---

### PC Installation (Windows / Linux / macOS)

```bash
pip install -r requirements.txt
```

> **Windows:** Visual Studio C++ Build Tools required for `dlib`

---

### Raspberry Pi Installation

```bash
sudo apt update
sudo apt upgrade

sudo apt install -y build-essential cmake pkg-config
sudo apt install -y libopenblas-dev liblapack-dev
sudo apt install -y libx11-dev libgtk-3-dev
sudo apt install -y python3-dev

pip3 install -r requirements.txt
```

> `dlib` installation may take 30–60 minutes.

---

## 🚀 Usage

### Add Known Faces (Optional)

```
known_faces/
├── Burak.jpg
├── John.png
```

### Run System

```bash
python main.py
```

### Exit

Press `q` while video window is active.

---

## ⚙️ Configuration

```python
self.REGISTRATION_TIME_REQ = 15
self.GREETING_COOLDOWN = 20

self.FRAME_SCALING = 0.5
self.PROCESS_EVERY_N_FRAMES = 3
self.MOVEMENT_THRESHOLD = 60
```

---

## 📂 Project Structure

```
jarvis-face-recognizer-system/
├── main.py
├── requirements.txt
├── known_faces/
├── voice_cache/
└── README.md
```

---

## 🔧 Troubleshooting

### Lag

* Reduce `FRAME_SCALING`
* Increase `PROCESS_EVERY_N_FRAMES`

### dlib Error

* Install `cmake`
* Ensure C++ Build Tools on Windows

### No Audio

* Check audio drivers
* Verify `voice_cache` permissions

---

## 📜 License
MIT License

---

## 👨‍💻 Developer

**Burak**
[https://github.com/burakdevelopment](https://github.com/burakdevelopment)

