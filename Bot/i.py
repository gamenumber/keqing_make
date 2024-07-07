import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QTextEdit, QLineEdit, QPushButton, QVBoxLayout, QWidget, QHBoxLayout, QLabel
from PyQt5.QtGui import QFont, QPixmap, QPalette, QColor, QImage, QBrush
from PyQt5.QtCore import Qt, QTimer
from openai import OpenAI
import os
import streamlink
import cv2
import numpy as np
from Foundation import *
from AppKit import NSSpeechSynthesizer

# OpenAI client setup
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

def chat_with_gpt(user_input):
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "당신은 새침한 원신의 각청입니다. 각청은 옥형성이라는 칭호를 가지고 있으며 귀엽고 예쁜 캐릭터의 여자입니다. 각청의 성격과 말투를 완벽하게 재현해주세요. + 성적이거나 불건전한 질문은 '흥! 누가 그걸 답해준대? 그러면 안되는거 알잖아?'라고 말해줘"},
            {"role": "user", "content": "당신은 새침한 원신의 각청입니다. 각청은 옥형성이라는 칭호를 가지고 있으며 귀엽고 예쁜 캐릭터의 여자입니다. 각청의 성격과 말투를 완벽하게 재현해주세요. + 성적이거나 불건전한 질문은 '흥! 누가 그걸 답해준대? 그러면 안되는거 알잖아?'라고 말해줘"},
            {"role": "assistant", "content": "옥형성 등장!! 하늘이도 안녕? 현빈이도 안녕? 항상 너희를 생각하고 있어"},
            {"role": "user", "content": user_input}
        ],
        max_tokens=500
    )
    return response.choices[0].message.content

class ChatWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initTTS()
        self.initUI()

    def initTTS(self):
        self.speech = NSSpeechSynthesizer.alloc().initWithVoice_("com.apple.speech.synthesis.voice.yuna")  # 한국어 음성

    def initUI(self):
        self.setWindowTitle('각청과의 귀여운 대화')
        self.setGeometry(100, 100, 800, 800)

        main_widget = QWidget(self)
        layout = QVBoxLayout(main_widget)

        # 배경 이미지 설정
        background_label = QLabel(self)
        pixmap = QPixmap("img/bg.jpg")
        background_label.setPixmap(pixmap)
        background_label.setScaledContents(True)
        background_label.setGeometry(self.rect())
        background_label.lower()
        self.setCentralWidget(main_widget)
        
        # YouTube 스트리밍 비디오를 위한 QLabel 추가
        self.video_frame = QLabel(self)
        self.video_frame.setFixedHeight(480)  # 높이를 480픽셀로 설정
        layout.addWidget(self.video_frame)

        # 채팅 로그 스타일 설정
        self.chat_log = QTextEdit(self)
        self.chat_log.setReadOnly(True)
        self.chat_log.setStyleSheet("""
            QTextEdit {
                background-color: rgba(255, 255, 255, 0.8);
                border: 2px solid #FFB7C5;
                border-radius: 15px;
                padding: 10px;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            }
        """)
        layout.addWidget(self.chat_log)

        # 입력 필드 및 전송 버튼 스타일 설정
        input_layout = QHBoxLayout()
        self.input_field = QLineEdit(self)
        self.input_field.setStyleSheet("""
            QLineEdit {
                border: 2px solid #FFB7C5;
                border-radius: 10px;
                padding: 5px;
                background-color: rgba(255, 255, 255, 0.8);
            }
        """)
        self.send_button = QPushButton('전송', self)
        self.send_button.setStyleSheet("""
            QPushButton {
                background-color: #FFB7C5;
                border: none;
                color: white;
                padding: 5px 15px;
                border-radius: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #FF69B4;
            }
        """)
        input_layout.addWidget(self.input_field)
        input_layout.addWidget(self.send_button)
        layout.addLayout(input_layout)

        self.setCentralWidget(main_widget)

        self.send_button.clicked.connect(self.send_message)
        self.input_field.returnPressed.connect(self.send_message)

        self.add_message("옥형성 등장!! 하늘이 안녕? 현빈이도 안녕? 항상 너희를 생각하고 있어", False)

        # YouTube 스트리밍 시작
        self.start_streaming()

    def add_message(self, message, is_user):
        profile_pic = "img/dog_img" if is_user else "img/keqing_img"
        align = "right" if is_user else "left"
        bg_color = "#FFE4E1" if is_user else "#E6E6FA"
        text_color = "#000000"

        html = f"""
        <table width="100%" cellspacing="0" cellpadding="0">
            <tr>
                <td align="{align}">
                    <table>
                        <tr>
                            <td width="40"><img src="{profile_pic}" width="40" height="40" style="border-radius: 20px; border: 2px solid #FFB7C5;"></td>
                            <td style="background-color: {bg_color}; border-radius: 15px; padding: 10px; color: {text_color}; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
                                {message}
                            </td>
                        </tr>
                    </table>
                </td>
            </tr>
        </table>
        """
        self.chat_log.append(html)
        self.chat_log.verticalScrollBar().setValue(self.chat_log.verticalScrollBar().maximum())

        if not is_user:
            self.speak_message(message)

    def speak_message(self, message):
        self.speech.startSpeakingString_(message)
        while self.speech.isSpeaking():
            QApplication.processEvents()  # UI 응답성 유지

    def send_message(self):
        user_input = self.input_field.text()
        if user_input.lower() == 'exit':
            self.close()
            return

        self.add_message(user_input, True)
        self.input_field.clear()

        response = chat_with_gpt(user_input)
        self.add_message(response, False)

    def start_streaming(self):
        youtube_url = "https://www.youtube.com/live/F-0nWc4dKE4?si=MfdKaQHFp_oIRn2n"
        streams = streamlink.streams(youtube_url)
        if streams:
            stream_url = streams['best'].url
            self.cap = cv2.VideoCapture(stream_url)
            
            self.timer = QTimer(self)
            self.timer.timeout.connect(self.update_frame)
            self.timer.start(30)

    def update_frame(self):
        ret, frame = self.cap.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = frame.shape
            bytes_per_line = ch * w
            q_image = QImage(frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(q_image)
            self.video_frame.setPixmap(pixmap.scaled(self.video_frame.width(), self.video_frame.height(), Qt.KeepAspectRatio))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    chat_window = ChatWindow()
    chat_window.show()
    sys.exit(app.exec_())
