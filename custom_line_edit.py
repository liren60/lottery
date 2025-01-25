from PyQt5.QtWidgets import QLineEdit
from PyQt5.QtCore import Qt

class CustomLineEdit(QLineEdit):
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            # 按回车键时，调用父窗口的 add_entry 方法
            self.parent().add_entry()
        else:
            super().keyPressEvent(event)
