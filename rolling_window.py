from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QMessageBox
from PyQt5.QtCore import Qt, QTimer
import random
from PyQt5.QtGui import QFont  # 添加这一行

class RollingWindow(QWidget):
    def __init__(self, entries, prizes, parent):
        super().__init__()
        self.entries = entries
        self.prizes = prizes
        self.is_rolling = False
        self.current_prize_index = 0
        self.parent = parent  # 保存对父窗口的引用
        self.initUI()

    def initUI(self):
        self.setWindowTitle("滚动抽奖")
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setStyleSheet("background-color: black;")
        layout = QVBoxLayout()
        self.label = QLabel("", self, alignment=Qt.AlignCenter)
        self.label.setStyleSheet("color: white;")
        self.prize_label = QLabel("", self, alignment=Qt.AlignCenter)
        self.prize_label.setStyleSheet("color: yellow;")
        layout.addWidget(self.prize_label)
        layout.addWidget(self.label)
        self.setLayout(layout)
        self.showFullScreen()
        self.setFocusPolicy(Qt.StrongFocus)
        self.adjust_font_sizes()  # 调整字体大小

    def adjust_font_sizes(self):
        screen = self.screen()
        screen_size = screen.size()
        font_size_label = screen_size.height() // 10
        font_size_prize_label = screen_size.height() // 20
        self.label.setFont(QFont('Arial', font_size_label))
        self.prize_label.setFont(QFont('Arial', font_size_prize_label))

    def start_rolling(self):
        self.is_rolling = True
        self.rolling_timer = QTimer(self)
        self.rolling_timer.timeout.connect(self.update_rolling_display)
        self.rolling_timer.start(100)

    def update_rolling_display(self):
        if self.is_rolling:
            selected_entry = random.choice(self.entries)
            self.label.setText(f"{selected_entry[0]} {selected_entry[1]}")
            if self.prizes:
                current_prize = self.prizes[self.current_prize_index]
                self.prize_label.setText(f"当前奖项: {current_prize['name']} ({current_prize['count']}个)")
            self.label.setStyleSheet(f"color: {random.choice(['red', 'green', 'blue', 'purple', 'orange'])}; font-weight: bold; text-shadow: 2px 2px 4px rgba(0,0,0,0.5);")
            self.adjust_font_sizes()  # 调整字体大小

    def pause_rolling(self):
        self.is_rolling = False
        self.rolling_timer.stop()
        if self.entries:
            selected_entry = random.choice(self.entries)
            self.label.setText(f"{selected_entry[0]} {selected_entry[1]}")
            if self.prizes:
                current_prize = self.prizes[self.current_prize_index]
                self.prize_label.setText(f"当前奖项: {current_prize['name']} ({current_prize['count']}个)")
                # 确保奖品数量不会变成负数
                if current_prize['count'] > 0:
                    current_prize['count'] -= 1
                if current_prize['count'] <= 0:
                    self.current_prize_index += 1
                    if self.current_prize_index >= len(self.prizes):
                        msg_box = QMessageBox(self)
                        msg_box.setWindowTitle("抽奖结束")
                        msg_box.setText("所有奖品已抽完！")
                        msg_box.setStyleSheet("""
                            QMessageBox {
                                background-color: white;
                            }
                            QMessageBox QLabel {
                                color: green;
                                background-color: lightgray;
                            }
                            QMessageBox QPushButton {
                                background-color: lightgray;
                                border: 1px solid gray;
                                padding: 5px;
                            }
                        """)
                        msg_box.exec_()
                        self.close()
                        self.parent.show()
                        return
            self.label.setStyleSheet("color: blue;")
            self.adjust_font_sizes()  # 调整字体大小

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()
            self.parent.show()
        elif event.key() == Qt.Key_Space:
            if self.is_rolling:
                self.pause_rolling()
            else:
                self.start_rolling()