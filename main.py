import cv2
import face_recognition
import os
import threading
import time
import numpy as np
from datetime import datetime
from gtts import gTTS
import pygame
import hashlib

class AudioSystem:
    
    def __init__(self):
        self.CACHE_DIR = "voice_cache"
        if not os.path.exists(self.CACHE_DIR):
            os.makedirs(self.CACHE_DIR)
        
        
        try:
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=4096)
        except pygame.error:
            print("[Ses Hatası] Ses kartı bulunamadı veya meşgul.")

        self.is_playing = False

    def _play_thread(self, filepath):
        self.is_playing = True
        try:
            pygame.mixer.music.load(filepath)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                time.sleep(0.1)
        except Exception as e:
            print(f"[Ses Oynatma Hatası]: {e}")
        self.is_playing = False

    def speak(self, text):
        
        if self.is_playing:
            return  

        
        filename = hashlib.md5(text.encode()).hexdigest() + ".mp3"
        filepath = os.path.join(self.CACHE_DIR, filename)

        if not os.path.exists(filepath):
            print(f"[Ses] Yeni ses oluşturuluyor: '{text}'")
            try:
                tts = gTTS(text=text, lang='tr')
                tts.save(filepath)
            except Exception as e:
                print(f"[İnternet Hatası] Ses oluşturulamadı: {e}")
                return

        
        threading.Thread(target=self._play_thread, args=(filepath,), daemon=True).start()

class SmartDoorSystem:
    def __init__(self):
        
        self.KNOWN_FACES_DIR = "known_faces"
        self.REGISTRATION_TIME_REQ = 15
        self.GREETING_COOLDOWN = 20
        
        
        self.FRAME_SCALING = 0.5            
        self.PROCESS_EVERY_N_FRAMES = 3     
        self.MOVEMENT_THRESHOLD = 60        
        self.MISSING_FACE_TOLERANCE = 10    

        
        self.known_face_encodings = []
        self.known_face_names = []
        
        self.unknown_timer_start = None
        self.last_unknown_center = None
        self.missing_face_counter = 0       
        
        self.last_greeted_time = {}
        
        
        if not os.path.exists(self.KNOWN_FACES_DIR):
            os.makedirs(self.KNOWN_FACES_DIR)
            
        
        self.audio = AudioSystem()
        self.load_known_faces()

        
        self.audio.speak("Sistem başlatıldı.")

    def load_known_faces(self):
        print("[Sistem] Yüz veritabanı yükleniyor...")
        self.known_face_encodings = []
        self.known_face_names = []
        
        for filename in os.listdir(self.KNOWN_FACES_DIR):
            if filename.endswith((".jpg", ".png", ".jpeg")):
                path = os.path.join(self.KNOWN_FACES_DIR, filename)
                image = face_recognition.load_image_file(path)
                encodings = face_recognition.face_encodings(image)
                if encodings:
                    self.known_face_encodings.append(encodings[0])
                    name = os.path.splitext(filename)[0].split('_')[0].capitalize()
                    self.known_face_names.append(name)
        print(f"[Sistem] {len(self.known_face_names)} kişi yüklendi.")

    def save_new_face(self, frame, face_location):
        top, right, bottom, left = face_location
        scale = int(1/self.FRAME_SCALING)
        margin = 30
        
        h, w, _ = frame.shape
        top = max(0, (top * scale) - margin)
        left = max(0, (left * scale) - margin)
        bottom = min(h, (bottom * scale) + margin)
        right = min(w, (right * scale) + margin)
        
        face_image = frame[top:bottom, left:right]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"Misafir_{timestamp}.jpg"
        
        save_path = os.path.join(self.KNOWN_FACES_DIR, filename)
        cv2.imwrite(save_path, face_image)
        
        
        self.load_known_faces() 
        self.audio.speak("Teşekkürler. Yüzünüz başarıyla kaydedildi.")
        return True

    def run(self):
        video_capture = cv2.VideoCapture(0)
        video_capture.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        video_capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

        frame_count = 0
        
        
        current_face_locations = []
        current_face_names = []
        current_knowns = []
        current_unknown_loc = None 

        print("[Sistem] Aktif.")

        while True:
            ret, frame = video_capture.read()
            if not ret:
                break
            
            
            if frame_count % self.PROCESS_EVERY_N_FRAMES == 0:
                
                
                small_frame = cv2.resize(frame, (0, 0), fx=self.FRAME_SCALING, fy=self.FRAME_SCALING)
                rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
                
                
                current_face_locations = face_recognition.face_locations(rgb_small_frame)
                current_face_encodings = face_recognition.face_encodings(rgb_small_frame, current_face_locations)

                current_face_names = []
                current_knowns = []
                temp_unknown_locs = []

                
                for idx, face_encoding in enumerate(current_face_encodings):
                    matches = face_recognition.compare_faces(self.known_face_encodings, face_encoding, tolerance=0.5)
                    name = "Tanimsiz"

                    if True in matches:
                        first_match_index = matches.index(True)
                        name = self.known_face_names[first_match_index]
                        current_knowns.append(name)
                    else:
                        temp_unknown_locs.append(current_face_locations[idx])

                    current_face_names.append(name)
                
                
                current_unknown_loc = None
                if temp_unknown_locs:
                    
                    current_unknown_loc = max(temp_unknown_locs, key=lambda loc: (loc[2]-loc[0]) * (loc[1]-loc[3]))

            frame_count += 1

            
            current_time = time.time()

            
            for name in current_knowns:
                if current_time - self.last_greeted_time.get(name, 0) > self.GREETING_COOLDOWN:
                    msg = f"Merhaba tekrardan hoşgeldiniz efendim."
                    
                    if current_unknown_loc:
                        msg += " Yanınızdaki misafir için kayıt işlemi gerekiyor."
                    self.audio.speak(msg)
                    self.last_greeted_time[name] = current_time

            
            if current_unknown_loc:
                
                self.missing_face_counter = 0
                
                top, right, bottom, left = current_unknown_loc
                center_x, center_y = (left + right) / 2, (top + bottom) / 2
                
                
                if current_time - self.last_greeted_time.get("Tanimsiz", 0) > self.GREETING_COOLDOWN:
                    if not current_knowns: 
                        self.audio.speak("Merhaba hoşgeldiniz. Yüzünüzü tanıtmak için lütfen sabit durun.")
                    self.last_greeted_time["Tanimsiz"] = current_time

                
                is_stable = False
                if self.last_unknown_center:
                    prev_x, prev_y = self.last_unknown_center
                    dist = np.sqrt((center_x - prev_x)**2 + (center_y - prev_y)**2)
                    
                    if dist < self.MOVEMENT_THRESHOLD:
                        is_stable = True
                    else:
                        
                        pass
                
                self.last_unknown_center = (center_x, center_y)

                if is_stable:
                    if self.unknown_timer_start is None:
                        self.unknown_timer_start = current_time
                    
                    elapsed = current_time - self.unknown_timer_start
                    remaining = int(self.REGISTRATION_TIME_REQ - elapsed)
                    
                    
                    scale = int(1/self.FRAME_SCALING)
                    cv2.putText(frame, f"SABIT DURUN: {remaining}", (50, 50), 
                                cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 255), 3)

                    if elapsed >= self.REGISTRATION_TIME_REQ:
                        if self.save_new_face(frame, current_unknown_loc):
                            self.unknown_timer_start = None
                            current_unknown_loc = None 
                else:
                    
                    pass

            else:
                
                self.missing_face_counter += 1
                if self.missing_face_counter > self.MISSING_FACE_TOLERANCE:
                    self.unknown_timer_start = None
                    self.last_unknown_center = None

            
            for (top, right, bottom, left), name in zip(current_face_locations, current_face_names):
                scale = int(1/self.FRAME_SCALING)
                top *= scale
                right *= scale
                bottom *= scale
                left *= scale
                
                color = (0, 255, 0) if name != "Tanimsiz" else (0, 0, 255)
                cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
                cv2.putText(frame, name, (left, bottom + 25), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)

            cv2.imshow('Giris Kamerasi', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        video_capture.release()
        cv2.destroyAllWindows()
        pygame.mixer.quit()

if __name__ == "__main__":
    app = SmartDoorSystem()
    app.run()