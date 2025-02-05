from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QMessageBox
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont
import random
from collections import deque

class RollingWindow(QWidget):
    def __init__(self, entries, prizes, parent):
        super().__init__()
        self.entries = entries
        self.prizes = prizes
        self.is_rolling = False
        self.current_prize_index = 0
        self.parent = parent  # 保存对父窗口的引用
        self.font_size = 30  # 默认值，稍后会在 update_font_size 中更新
        self.random_sequence = deque(random.sample(entries, len(entries)))  # 预生成随机序列
        self.initUI()

    def initUI(self):
        self.setWindowTitle("滚动抽奖")
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setStyleSheet("background-color: black;")
        layout = QVBoxLayout()
        self.prize_label = QLabel("", self, alignment=Qt.AlignCenter)
        self.label = QLabel("", self, alignment=Qt.AlignCenter)
        layout.addWidget(self.prize_label)
        layout.addWidget(self.label)
        self.setLayout(layout)
        self.showFullScreen()
        self.setFocusPolicy(Qt.StrongFocus)
        self.update_font_size()

    def update_font_size(self):
        """根据屏幕大小动态调整字体大小"""
        screen_geometry = self.screen().availableGeometry()
        self.font_size = screen_geometry.height() // 8  # 根据屏幕高度计算字体大小

        # 使用 QFont 设置字体大小
        font = QFont()
        font.setPointSize(self.font_size)
        self.label.setFont(font)
        self.label.setStyleSheet("color: white; font-weight: bold;")
        
        prize_font = QFont()
        prize_font.setPointSize(self.font_size // 3)
        self.prize_label.setFont(prize_font)
        self.prize_label.setStyleSheet("color: yellow;")

    def resizeEvent(self, event):
        """窗口大小变化时调整字体大小"""
        self.update_font_size()
        super().resizeEvent(event)

    def start_rolling(self):
        """开始滚动"""
        if not self.entries:
            self.show_message(QMessageBox.Warning, "错误", "没有可用的抽奖条目！")
            return
        self.is_rolling = True
        self.rolling_timer = QTimer(self)
        self.rolling_timer.timeout.connect(self.update_rolling_display)
        self.rolling_timer.start(100)

    def update_rolling_display(self):
        """更新滚动显示"""
        if self.is_rolling:
            if not self.random_sequence:
                self.random_sequence = deque(random.sample(self.entries, len(self.entries)))
            selected_entry = self.random_sequence.popleft()
            self.label.setText(f"{selected_entry[0]} {selected_entry[1]}")
            if self.prizes:
                current_prize = self.prizes[self.current_prize_index]
                self.prize_label.setText(f"当前奖项: {current_prize['name']} ({current_prize['count']}个)")
            # 动态改变文字颜色，字体大小使用 self.font_size
            self.label.setStyleSheet(
                f"color: {random.choice(['red', 'green', 'blue', 'purple', 'orange'])}; "
                f"font-size: {self.font_size}px; font-weight: bold; text-shadow: 2px 2px 4px rgba(0,0,0,0.5);"
            )

    def pause_rolling(self):
        """暂停滚动并抽奖"""
        self.is_rolling = False
        self.rolling_timer.stop()
        if self.entries:
            selected_entry = random.choice(self.entries)
            self.label.setText(f"{selected_entry[0]} {selected_entry[1]}")
            self.entries.remove(selected_entry)  # 移除已抽中的条目
            if self.prizes:
                current_prize = self.prizes[self.current_prize_index]
                self.prize_label.setText(f"当前奖项: {current_prize['name']} ({current_prize['count']}个)")
                if current_prize['count'] > 0:
                    current_prize['count'] -= 1
                if current_prize['count'] <= 0:
                    # 使用自定义消息弹窗样式
                    self.show_message(QMessageBox.Information, "提示",
                                      f"奖品 {current_prize['name']} 已抽完，即将切换到下一个奖品！")
                    self.current_prize_index += 1
                    if self.current_prize_index >= len(self.prizes):
                        msg_box = QMessageBox(self)
                        msg_box.setWindowTitle("抽奖结束")
                        msg_box.setText("所有奖品已抽完！")
                        msg_box.setStyleSheet("""
                            QMessageBox { background-color: white; color: black; }
                            QMessageBox QLabel { color: green; background-color: lightgray; }
                            QMessageBox QPushButton { background-color: lightgray; border: 1px solid gray; padding: 5px; }
                        """)
                        msg_box.exec_()
                        self.close()
                        self.parent.show()
                        return
        # 暂停时固定字体颜色为蓝色，字体大小使用 self.font_size
        self.label.setStyleSheet(
            f"color: blue; font-size: {self.font_size}px; font-weight: bold;"
        )

    def keyPressEvent(self, event):
        """键盘事件处理"""
        if event.key() == Qt.Key_Escape:
            reply = self.show_message(QMessageBox.Question, '确认退出', '确定要退出抽奖吗？', buttons=QMessageBox.Yes | QMessageBox.No, defaultButton=QMessageBox.No)
            if reply == QMessageBox.Yes:
                self.close()
                self.parent.show()
        elif event.key() == Qt.Key_Space:
            if self.is_rolling:
                self.pause_rolling()
            else:
                self.start_rolling()

    def show_message(self, icon, title, text, buttons=QMessageBox.Ok, defaultButton=QMessageBox.Ok):
        """
        辅助函数：显示一个自定义样式的消息弹窗
        icon：QMessageBox.Icon 枚举，如 QMessageBox.Warning
        title：弹窗标题
        text：弹窗信息文本
        buttons：弹窗按钮
        defaultButton：默认按钮
        返回按钮点击的结果
        """
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(title)
        msg_box.setText(text)
        msg_box.setIcon(icon)
        msg_box.setStandardButtons(buttons)
        msg_box.setDefaultButton(defaultButton)
        # 设置白色背景和黑色文字
        msg_box.setStyleSheet("background-color: white; color: black;")
        return msg_box.exec_()
