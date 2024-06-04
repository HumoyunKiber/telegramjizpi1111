import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QLabel, QLineEdit, QMessageBox
import cv2
import face_recognition
import sqlite3
import numpy as np
import concurrent.futures

class FaceApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.initCamera()

    def initUI(self):
        self.setWindowTitle("Face Recognition App")
        self.setGeometry(100, 100, 400, 300)

        self.layout = QVBoxLayout()

        self.register_btn = QPushButton("Ishchilarni ro'yxatga olish", self)
        self.register_btn.clicked.connect(self.register)
        self.layout.addWidget(self.register_btn)

        self.attendance_btn = QPushButton("Yo'qlama qilish", self)
        self.attendance_btn.clicked.connect(self.attendance)
        self.layout.addWidget(self.attendance_btn)

        self.setLayout(self.layout)

    def initCamera(self):
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
        self.cap.set(cv2.CAP_PROP_FPS, 30)

    def register(self):
        self.name_label = QLabel("Ishchining ismi:", self)
        self.layout.addWidget(self.name_label)

        self.name_input = QLineEdit(self)
        self.layout.addWidget(self.name_input)

        self.phone_label = QLabel("Ishchining telefon raqami:", self)
        self.layout.addWidget(self.phone_label)

        self.phone_input = QLineEdit(self)
        self.layout.addWidget(self.phone_input)

        self.capture_btn = QPushButton("Yuzni aniqlash", self)
        self.capture_btn.clicked.connect(self.capture_face)
        self.layout.addWidget(self.capture_btn)

    def capture_face(self):
        name = self.name_input.text()
        phone = self.phone_input.text()

        if not name or not phone:
            QMessageBox.warning(self, "Xato", "Iltimos, barcha maydonlarni to'ldiring!")
            return

        ret, frame = self.cap.read()

        if not ret:
            QMessageBox.warning(self, "Xato", "Kamerani yoqing!")
            return

        rgb_frame = frame[:, :, ::-1]
        encodings = face_recognition.face_encodings(rgb_frame)
        if encodings:
            encoding = encodings[0]
            self.save_face_to_db(name, phone, encoding)
            QMessageBox.information(self, "Muvaffaqiyatli", "Yuz muvaffaqiyatli ro'yxatga olindi!")
        else:
            QMessageBox.warning(self, "Xato", "Yuz topilmadi!")

    def save_face_to_db(self, name, phone, encoding):
        conn = sqlite3.connect('faces.db')
        c = conn.cursor()
        c.execute('INSERT INTO faces (name, phone, encoding) VALUES (?, ?, ?)', (name, phone, encoding.tobytes()))
        conn.commit()
        conn.close()

    def load_known_faces_from_db(self):
        known_face_encodings = []
        known_face_names = []

        conn = sqlite3.connect('faces.db')
        c = conn.cursor()
        c.execute('SELECT name, encoding FROM faces')
        rows = c.fetchall()
        for row in rows:
            name, encoding = row
            known_face_encodings.append(np.frombuffer(encoding, dtype=np.float64))
            known_face_names.append(name)
        conn.close()

        return known_face_encodings, known_face_names

    def attendance(self):
        known_face_encodings, known_face_names = self.load_known_faces_from_db()
        
        frame_counter = 0
        frame_skip = 5  # Har 5 kadrdan birini tahlil qilish
        
        while True:
            ret, frame = self.cap.read()
            if not ret:
                break
            
            if frame_counter % frame_skip == 0:
                rgb_frame = frame[:, :, ::-1]
                face_locations = face_recognition.face_locations(rgb_frame)
                face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
                
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future_to_face = {executor.submit(self.process_face, face_encoding, known_face_encodings): (face_location, face_encoding) for face_location, face_encoding in zip(face_locations, face_encodings)}

                    for future in concurrent.futures.as_completed(future_to_face):
                        face_location, face_encoding = future_to_face[future]
                        try:
                            name, color = future.result()
                        except Exception as exc:
                            name, color = "Nomalum", (0, 0, 255)  # Red

                        top, right, bottom, left = face_location
                        cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
                        cv2.putText(frame, name, (left + 6, bottom - 6), cv2.FONT_HERSHEY_DUPLEX, 0.8, (255, 255, 255), 1)
            
            cv2.imshow("Yo'qlama qilish", frame)
            frame_counter += 1
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        self.cap.release()
        cv2.destroyAllWindows()

    def process_face(self, face_encoding, known_face_encodings):
        matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
        name = "Nomalum"
        color = (0, 0, 255)  # Red

        face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
        best_match_index = np.argmin(face_distances)
        if matches[best_match_index]:
            name = known_face_names[best_match_index]
            color = (0, 255, 0)  # Green

        return name, color

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = FaceApp()
    ex.show()
    sys.exit(app.exec_())
