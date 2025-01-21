from PyQt5.QtCore import Qt, QRegExp
from PyQt5.QtGui import QTextCharFormat, QColor, QFont
from PyQt5.QtWidgets import QApplication, QTextEdit
from PyQt5.QtGui import QSyntaxHighlighter


class PythonHighlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super(PythonHighlighter, self).__init__(parent)

        # 주석 줄 포맷 설정
        self.commentFormat = QTextCharFormat()
        self.commentFormat.setForeground(QColor("gray"))  # 회색
        self.commentFormat.setFontItalic(True)  # 기울임꼴

    def highlightBlock(self, text):
        # 주석 패턴: 줄의 시작부터 `#`으로 시작하는 부분
        comment_pattern = QRegExp(r"#.*")
        index = comment_pattern.indexIn(text)
        while index >= 0:
            length = comment_pattern.matchedLength()
            self.setFormat(index, length, self.commentFormat)
            index = comment_pattern.indexIn(text, index + length)

        # 기본 블록 상태 초기화
        self.setCurrentBlockState(0)


class CodeEditor(QTextEdit):
    def __init__(self, parent=None):
        super(CodeEditor, self).__init__(parent)
        self.setFont(QFont("Courier", 10))
        self.highlighter = PythonHighlighter(self.document())  # 하이라이터 연결


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    editor = CodeEditor()
    editor.setPlainText("# 이 줄은 회색으로 표시됩니다.\nprint('Hello, World!')\n# 또 다른 주석입니다.")
    editor.show()
    sys.exit(app.exec_())

#
# import sys
# import time
# from PyQt5.QtCore import QThread, pyqtSignal
# from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel
#
# # 첫 번째 작업을 수행할 스레드 클래스
# class FirstThread(QThread):
#     # 데이터를 전달하는 신호 (인자 3개)
#     data_ready = pyqtSignal(int, float, str)
#
#     def run(self):
#         print("첫 번째 스레드 시작")
#         # 데이터 생성
#         time.sleep(2)
#         data1 = 42       # 정수
#         data2 = 3.14     # 실수
#         data3 = "PyQt5"  # 문자열
#         print("첫 번째 스레드 완료, 생성 데이터:", data1, data2, data3)
#         self.data_ready.emit(data1, data2, data3)  # 신호로 데이터 전달
#
# # 두 번째 작업을 수행할 스레드 클래스
# class SecondThread(QThread):
#     def __init__(self):
#         super().__init__()
#         self.data1 = None
#         self.data2 = None
#         self.data3 = None
#
#     def set_data(self, data1, data2, data3):
#         self.data1 = data1
#         self.data2 = data2
#         self.data3 = data3
#
#     def run(self):
#         print("두 번째 스레드 시작")
#         if self.data1 is not None and self.data2 is not None and self.data3 is not None:
#             print(f"두 번째 스레드에서 받은 데이터: {self.data1}, {self.data2}, {self.data3}")
#             time.sleep(3)  # 작업 시간
#             print("두 번째 스레드 완료")
#         else:
#             print("두 번째 스레드에 전달된 데이터 없음")
#
# # 메인 윈도우 클래스
# class MainWindow(QWidget):
#     def __init__(self):
#         super().__init__()
#         self.setWindowTitle("QThread 다중 데이터 전달 예제")
#         self.layout = QVBoxLayout()
#
#         self.label = QLabel("스레드 상태: 대기 중")
#         self.layout.addWidget(self.label)
#
#         self.button = QPushButton("작업 시작")
#         self.button.clicked.connect(self.start_threads)
#         self.layout.addWidget(self.button)
#
#         self.setLayout(self.layout)
#
#         # 스레드 생성
#         self.first_thread = FirstThread()
#         self.second_thread = SecondThread()
#
#         # 첫 번째 스레드의 데이터 신호를 연결
#         self.first_thread.data_ready.connect(self.on_data_ready)
#
#     def start_threads(self):
#         self.label.setText("스레드 상태: 첫 번째 스레드 실행 중")
#         self.first_thread.start()
#
#     def on_data_ready(self, data1, data2, data3):
#         self.label.setText("스레드 상태: 두 번째 스레드 실행 중")
#         print("메인 윈도우에서 받은 데이터:", data1, data2, data3)
#         self.second_thread.set_data(data1, data2, data3)
#         self.second_thread.start()
#
# if __name__ == "__main__":
#     app = QApplication(sys.argv)
#     window = MainWindow()
#     window.show()
#     sys.exit(app.exec_())