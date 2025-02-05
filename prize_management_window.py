from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem, QPushButton, QInputDialog, QMessageBox
from PyQt5.QtCore import Qt

class PrizeManagementWindow(QWidget):
    def __init__(self, prizes, parent):
        super().__init__()
        self.prizes = prizes
        self.parent = parent
        self.initUI()

    def initUI(self):
        self.setWindowTitle("奖品管理")
        layout = QVBoxLayout()

        self.table = QTableWidget(len(self.prizes), 2)
        self.table.setHorizontalHeaderLabels(["奖品名称", "奖品数量"])
        self.table.setEditTriggers(QTableWidget.DoubleClicked)
        self.table.cellChanged.connect(self.cell_changed)

        for row, prize in enumerate(self.prizes):
            self.table.setItem(row, 0, QTableWidgetItem(prize['name']))
            self.table.setItem(row, 1, QTableWidgetItem(str(prize['count'])))

        layout.addWidget(self.table)

        button_layout = QHBoxLayout()
        add_button = QPushButton("添加奖品")
        add_button.clicked.connect(self.add_prize)
        button_layout.addWidget(add_button)

        delete_button = QPushButton("删除奖品")
        delete_button.clicked.connect(self.delete_prize)
        button_layout.addWidget(delete_button)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def cell_changed(self, row, column):
        if column == 0:
            self.prizes[row]['name'] = self.table.item(row, column).text()
        elif column == 1:
            try:
                self.prizes[row]['count'] = int(self.table.item(row, column).text())
            except ValueError:
                QMessageBox.warning(self, "输入错误", "奖品数量必须是整数")
                self.table.item(row, column).setText(str(self.prizes[row]['count']))

        self.parent.save_prizes()

    def add_prize(self):
        name, ok = QInputDialog.getText(self, "添加奖品", "请输入奖品名称：")
        if ok and name:
            count, ok = QInputDialog.getInt(self, "添加奖品", "请输入奖品数量：", 1, 1)
            if ok:
                self.prizes.append({'name': name, 'count': count, 'original_count': count})
                self.table.insertRow(self.table.rowCount())
                self.table.setItem(self.table.rowCount() - 1, 0, QTableWidgetItem(name))
                self.table.setItem(self.table.rowCount() - 1, 1, QTableWidgetItem(str(count)))
                self.parent.save_prizes()

    def delete_prize(self):
        selected_items = self.table.selectedItems()
        if selected_items:
            row = selected_items[0].row()
            self.prizes.pop(row)
            self.table.removeRow(row)
            self.parent.save_prizes()
