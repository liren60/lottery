import random
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt, QTimer

class RollingWindow(QWidget):
    def __init__(self, entries):
        super().__init__()
        self.entries = entries
        self.is_rolling = False
        self.initUI()

    def initUI(self):
        self.setWindowTitle("滚动抽奖")
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setStyleSheet("background-color: black;")
        layout = QVBoxLayout()
        self.label = QLabel("", self, alignment=Qt.AlignCenter)
        self.label.setStyleSheet("color: white; font-size: 500px;")
        layout.addWidget(self.label)
        self.setLayout(layout)
        self.showFullScreen()
        self.setFocusPolicy(Qt.StrongFocus)

    def start_rolling(self):
        self.is_rolling = True
        self.rolling_timer = QTimer(self)
        self.rolling_timer.timeout.connect(self.update_rolling_display)
        self.rolling_timer.start(100)

    def update_rolling_display(self):
        if self.is_rolling:
            selected_entry = random.choice(self.entries)
            self.label.setText(f"{selected_entry[0]} {selected_entry[1]}")
            self.label.setStyleSheet(f"color: {random.choice(['red', 'green', 'blue', 'purple', 'orange'])}; font-size: 500px;")

    def pause_rolling(self):
        self.is_rolling = False
        self.rolling_timer.stop()
        if self.entries:
            selected_entry = random.choice(self.entries)
            self.label.setText(f"{selected_entry[0]} {selected_entry[1]}")
            self.label.setStyleSheet("color: blue; font-size: 800px;")

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()
        elif event.key() == Qt.Key_Space:
            if self.is_rolling:
                self.pause_rolling()
            else:
                self.start_rolling()
