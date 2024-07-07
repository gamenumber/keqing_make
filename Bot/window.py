import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QTextEdit, QLineEdit, QPushButton, QVBoxLayout, QWidget, QHBoxLayout, QLabel
from PyQt5.QtGui import QPixmap, QImage, QTextCursor
from PyQt5.QtCore import Qt
import pyttsx3

import os
from openai import OpenAI  # OpenAI 사용 시 필요한 라이브러리

# OpenAI API 설정
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

def chat_with_gpt(user_input):
    # OpenAI와 대화하기 위한 함수
    response = client.Chat.Completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "당신은 새침한 원신의 각청입니다. 각청은 옥형성이라는 칭호를 가지고 있으며 귀엽고 예쁜 캐릭터의 여자입니다. 각청의 성격과 말투를 완벽하게 재현해주세요. + 성적이거나 불건전한 질문은 '흥! 누가 그걸 답해준대? 그러면 안되는거 알잖아?'라고 말해줘"},
            {"role": "user", "content": user_input}
        ],
        max_tokens=500
    )
    return response.choices[0].message.content

class ChatWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.initTTS()  # TTS 초기화

    def initUI(self):
        self.setWindowTitle('각청과의 귀여운 대화')
        self.setGeometry(100, 100, 800, 800)

        main_widget = QWidget(self)
        layout = QVBoxLayout(main_widget)

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

    def initTTS(self):
        # TTS 초기화 함수
        self.tts_engine = pyttsx3.init()
        self.tts_engine.setProperty('rate', 150)  # 속도 설정 (기본값은 200)
        self.tts_engine.setProperty('volume', 0.9)  # 볼륨 설정 (기본값은 1.0)

    def add_message(self, message, is_user):
        # 채팅 메시지 추가 함수
        profile_pic = "img/dog_img" if is_user else "img/keqing_img"
        align = Qt.AlignRight if is_user else Qt.AlignLeft
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

        # 각청이 대답할 때 TTS로 음성 출력
        if not is_user:
            self.speak_message(message)

    def speak_message(self, message):
        # 메시지를 TTS로 읽어주는 함수
        self.tts_engine.say(message)
        self.tts_engine.runAndWait()

    def send_message(self):
        # 메시지 전송 함수
        user_input = self.input_field.text()
        if user_input.lower() == 'exit':
            self.close()
            return

        self.add_message(user_input, True)
        self.input_field.clear()

        response = chat_with_gpt(user_input)
        self.add_message(response, False)

    def closeEvent(self, event):
        # 종료 시 TTS 엔진 정리
        self.tts_engine.stop()
        event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    chat_window = ChatWindow()
    chat_window.show()
    sys.exit(app.exec_())
