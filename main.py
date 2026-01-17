import cv2
import face_recognition
import os
import threading
import time
import numpy as np
import logging
import io
import hashlib
from datetime import datetime
from typing import List, Tuple, Optional, Any
from gtts import gTTS
import pygame


class Config:
    
    CAMERA_INDEX = 0
    DISPLAY_WIDTH = 1184
    DISPLAY_HEIGHT = 659
    FRAME_SCALING = 0.5  #0.5 = faster processing
    PROCESS_EVERY_N_FRAMES = 2  #skip frames to reduce CPU load

    
    REGISTRATION_TIME_REQ = 5  #seconds to register a new face
    MOVEMENT_THRESHOLD = 50    #pixel distance to consider "stable"
    MISSING_FACE_TOLERANCE = 10 #frames to wait before resetting timer
    FACE_MATCH_TOLERANCE = 0.5 #lower is stricter

    MSG_WELCOME = "Hello, welcome..."
    MSG_SCANNING = "Scanning..."
    
    LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'


logging.basicConfig(level=logging.INFO, format=Config.LOG_FORMAT)
logger = logging.getLogger("JarvisFRS")

class SecureAudioHandler:
    def __init__(self):
        try:
            
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=4096)
            logger.info("Audio system initialized successfully.")
        except pygame.error as e:
            logger.error(f"Audio device not found: {e}")

        self.is_playing = False
        self.audio_cache = {} 
        
        
        self._preload_audio(Config.MSG_WELCOME)

    def _preload_audio(self, text: str):
        try:
            
            msg_hash = hashlib.sha256(text.encode()).hexdigest()
            
            if msg_hash not in self.audio_cache:
                tts = gTTS(text=text, lang='en') 
                fp = io.BytesIO()
                tts.write_to_fp(fp)
                fp.seek(0)
                self.audio_cache[msg_hash] = fp.read()
                logger.debug(f"Audio cached in RAM: '{text}'")
        except Exception as e:
            logger.error(f"Failed to synthesize audio: {e}")

    def _play_thread(self, audio_bytes: bytes):
        self.is_playing = True
        try:
            sound_data = io.BytesIO(audio_bytes)
            pygame.mixer.music.load(sound_data)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                time.sleep(0.1)
        except Exception as e:
            logger.error(f"Playback error: {e}")
        finally:
            self.is_playing = False

    def speak(self, text: str):
        if self.is_playing:
            return

        msg_hash = hashlib.sha256(text.encode()).hexdigest()
        
        
        if msg_hash not in self.audio_cache:
            self._preload_audio(text)
        
        if msg_hash in self.audio_cache:
            threading.Thread(target=self._play_thread, 
                             args=(self.audio_cache[msg_hash],), 
                             daemon=True).start()

class SmartGuardian:
    def __init__(self):
        self.known_face_encodings: List[np.ndarray] = []
        self.known_face_names: List[str] = []
        
        
        self.person_counter = 1
        self.unknown_timer_start = None
        self.last_unknown_center = None
        self.missing_face_counter = 0
        
        
        self.welcome_message_delivered = False
        
        
        self.audio = SecureAudioHandler()
        
        logger.info("System Ready. Mode: Volatile Storage (RAM Only).")

    def register_face_memory(self, face_encoding: np.ndarray) -> str:
        new_name = f"Person {self.person_counter}"
        self.known_face_encodings.append(face_encoding)
        self.known_face_names.append(new_name)
        self.person_counter += 1
        
        logger.info(f"New identity registered in volatile memory: {new_name}")
        return new_name

    def run(self):
        video_capture = cv2.VideoCapture(Config.CAMERA_INDEX)
        
        video_capture.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        video_capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

        if not video_capture.isOpened():
            logger.critical("Cannot open camera.")
            return

        frame_count = 0
        
        
        current_face_locations = []
        current_face_names = []
        current_unknown_data = [] 

        logger.info("Surveillance started. Press 'q' to exit.")

        try:
            while True:
                ret, frame = video_capture.read()
                if not ret:
                    logger.warning("Failed to grab frame.")
                    break
                
                
                if frame_count % Config.PROCESS_EVERY_N_FRAMES == 0:
                    
                    
                    small_frame = cv2.resize(frame, (0, 0), fx=Config.FRAME_SCALING, fy=Config.FRAME_SCALING)
                    rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
                    
                    
                    current_face_locations = face_recognition.face_locations(rgb_small_frame)
                    current_face_encodings = face_recognition.face_encodings(rgb_small_frame, current_face_locations)

                    current_face_names = []
                    current_unknown_data = [] 

                    
                    if len(current_face_locations) > 0:
                        
                        if not self.welcome_message_delivered:
                            logger.info("Visitor detected. Playing welcome message.")
                            self.audio.speak(Config.MSG_WELCOME)
                            self.welcome_message_delivered = True
                    else:
                        
                        if self.welcome_message_delivered:
                            logger.info("Area cleared. Resetting greeting trigger.")
                            self.welcome_message_delivered = False

                    
                    for idx, face_encoding in enumerate(current_face_encodings):
                        matches = face_recognition.compare_faces(self.known_face_encodings, 
                                                               face_encoding, 
                                                               tolerance=Config.FACE_MATCH_TOLERANCE)
                        name = "Unknown"

                        if True in matches:
                            first_match_index = matches.index(True)
                            name = self.known_face_names[first_match_index]
                        else:
                            
                            current_unknown_data.append((current_face_locations[idx], face_encoding))

                        current_face_names.append(name)

                frame_count += 1
                current_time = time.time()

                
                target_unknown = None
                if current_unknown_data:
                    
                    target_unknown = max(current_unknown_data, 
                                       key=lambda x: (x[0][2]-x[0][0]) * (x[0][1]-x[0][3]))

                if target_unknown:
                    self.missing_face_counter = 0
                    u_loc, u_enc = target_unknown
                    
                    top, right, bottom, left = u_loc
                    center_x, center_y = (left + right) / 2, (top + bottom) / 2
                    
                    
                    is_stable = False
                    if self.last_unknown_center:
                        prev_x, prev_y = self.last_unknown_center
                        dist = np.sqrt((center_x - prev_x)**2 + (center_y - prev_y)**2)
                        
                        if dist < Config.MOVEMENT_THRESHOLD:
                            is_stable = True
                    
                    self.last_unknown_center = (center_x, center_y)

                    if is_stable:
                        if self.unknown_timer_start is None:
                            self.unknown_timer_start = current_time
                        
                        elapsed = current_time - self.unknown_timer_start
                        remaining = int(Config.REGISTRATION_TIME_REQ - elapsed)
                        
                        
                        scale = int(1/Config.FRAME_SCALING)
                        
                        txt_loc = (left * scale, (top * scale) - 20)
                        
                    
                        cv2.putText(frame, f"Registering: {remaining}s", txt_loc, 
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

                        if elapsed >= Config.REGISTRATION_TIME_REQ:
                            self.register_face_memory(u_enc)
                            self.unknown_timer_start = None 
                    else:
                        pass
                else:
                    
                    self.missing_face_counter += 1
                    if self.missing_face_counter > Config.MISSING_FACE_TOLERANCE:
                        self.unknown_timer_start = None
                        self.last_unknown_center = None

                
                for (top, right, bottom, left), name in zip(current_face_locations, current_face_names):
                    scale = int(1/Config.FRAME_SCALING)
                    top *= scale
                    right *= scale
                    bottom *= scale
                    left *= scale
                    
                   
                    color = (0, 255, 0) if name != "Unknown" else (0, 0, 255)
                    
                    
                    cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
                    
                    
                    cv2.rectangle(frame, (left, bottom - 30), (right, bottom), color, cv2.FILLED)
                    cv2.putText(frame, name, (left + 6, bottom - 6), 
                                cv2.FONT_HERSHEY_DUPLEX, 0.6, (255, 255, 255), 1)

                
                final_display = cv2.resize(frame, (Config.DISPLAY_WIDTH, Config.DISPLAY_HEIGHT))
                
                
                cv2.putText(final_display, "JarvisFRS v1.0", (10, 30), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

                cv2.imshow('JarvisFRS', final_display)

                if cv2.waitKey(1) & 0xFF == ord('q'):
                    logger.info("User requested shutdown.")
                    break
        
        except Exception as e:
            logger.critical(f"Unexpected crash: {e}")
        finally:
            
            logger.info("releasing resources...")
            video_capture.release()
            cv2.destroyAllWindows()
            pygame.mixer.quit()
            logger.info("System shutdown complete.")

if __name__ == "__main__":
    app = SmartGuardian()
    app.run()
