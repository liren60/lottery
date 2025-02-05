import sys
import os
import pandas as pd
from PyQt5.QtWidgets import QApplication, QWidget, QInputDialog, QMessageBox, QFileDialog, QVBoxLayout, QPushButton, QListView
from PyQt5.QtCore import Qt, QAbstractItemModel, QModelIndex
from ui_components import setup_main_ui, CustomLineEdit
from data_management import DataManager
from rolling_window import RollingWindow
from prize_management_window import PrizeManagementWindow
import random

class EntryModel(QAbstractItemModel):
    def __init__(self, entries, parent=None):
        super().__init__(parent)
        self.entries = entries

    def rowCount(self, parent=QModelIndex()):
        return len(self.entries)

    def columnCount(self, parent=QModelIndex()):
        return 2

    def data(self, index, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            row, column = index.row(), index.column()
            if column == 0:
                return str(self.entries[row][0])
            elif column == 1:
                return self.entries[row][1]
        return None

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return ['编号', '姓名'][section]
        return None

    def index(self, row, column, parent=QModelIndex()):
        return self.createIndex(row, column)

    def parent(self, index):
        return QModelIndex()

class RandomNumberRolling(QWidget):
    def __init__(self):
        super().__init__()
        self.entries = []
        self.current_id = 1
        self.last_selected = None
        self.is_rolling = False
        self.is_fullscreen = False
        self.current_page = 0
        self.entries_per_page = 10
        self.total_pages = 1
        self.window_size = (800, 1000)
        self.prizes = []
        self.data_manager = DataManager()

        self.load_settings()
        self.initUI()
        self.load_data()
        self.load_prizes()

    def initUI(self):
        self.setWindowTitle("编号与姓名滚动抽奖")
        layout = setup_main_ui(self)
        self.setLayout(layout)
        self.resize(*self.window_size)

        self.model = EntryModel(self.entries, self)
        self.listbox = QListView(self)
        self.listbox.setModel(self.model)

        # 添加奖品管理按钮
        prize_management_button = QPushButton("管理奖品", self)
        prize_management_button.clicked.connect(self.open_prize_management)
        layout.addWidget(prize_management_button)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            if self.name_entry.hasFocus():
                self.add_entry()
        elif event.key() == Qt.Key_Delete:
            self.delete_entry()
        elif event.key() == Qt.Key_F:
            self.toggle_fullscreen()
        super().keyPressEvent(event)

    def load_data(self):
        self.entries = self.data_manager.load_data()
        if self.entries:
            self.current_id = max(entry[0] for entry in self.entries) + 1
        self.update_listbox()

    def save_data(self):
        if self.entries:
            self.data_manager.save_data(self.entries)

    def load_settings(self):
        settings = self.data_manager.load_settings()
        self.entries_per_page = settings.get('entries_per_page', 10)
        self.current_page = settings.get('current_page', 0)
        self.window_size = tuple(settings.get('window_size', (800, 1000)))
        self.prizes = settings.get('prizes', [])

    def save_settings(self):
        settings = {
            'entries_per_page': self.entries_per_page,
            'current_page': self.current_page,
            'window_size': (self.width(), self.height()),
            'prizes': self.prizes
        }
        self.data_manager.save_settings(settings)

    def load_prizes(self):
        self.prizes = self.data_manager.load_prizes()

    def save_prizes(self):
        self.data_manager.save_prizes(self.prizes)

    def add_entry(self):
        name = self.name_entry.text().strip()
        if name:
            if not any(entry[1] == name for entry in self.entries):
                self.entries.append((self.current_id, name))
                self.current_id += 1
                self.update_listbox()
                self.name_entry.clear()
                QMessageBox.information(self, "添加条目", f"成功添加条目: {name}")
            else:
                QMessageBox.warning(self, "添加条目", f"条目 '{name}' 已存在！")
        else:
            QMessageBox.warning(self, "添加条目", "请输入姓名！")

    def delete_entry(self):
        if self.listbox.selectedItems():
            for item in reversed(self.listbox.selectedItems()):
                self.entries.pop(self.listbox.row(item))
            self.update_listbox()
            QMessageBox.information(self, "删除条目", "选中条目已删除。")
        else:
            QMessageBox.warning(self, "删除条目", "请先选择要删除的条目。")

    def modify_entry(self):
        if self.listbox.selectedItems():
            current_item = self.listbox.selectedItems()[0]
            row = self.listbox.row(current_item)
            current_name = self.entries[row][1]
            new_name, ok = QInputDialog.getText(self, "修改姓名", "请输入新的姓名：", text=current_name)
            if ok and new_name:
                self.entries[row] = (self.entries[row][0], new_name)
                self.update_listbox()

    def update_listbox(self):
        self.listbox.clear()
        start, end = self.current_page * self.entries_per_page, (self.current_page + 1) * self.entries_per_page
        for entry in self.entries[start:min(end, len(self.entries))]:
            self.listbox.addItem(f"{entry[0]} {entry[1]}")
        self.total_pages = (len(self.entries) + self.entries_per_page - 1) // self.entries_per_page
        self.page_label.setText(f"当前页: {self.current_page + 1} / {self.total_pages}")

    def prev_page(self):
        if self.current_page > 0:
            self.current_page -= 1
            self.update_listbox()

    def next_page(self):
        if (self.current_page + 1) * self.entries_per_page < len(self.entries):
            self.current_page += 1
            self.update_listbox()

    def update_entries_per_page(self):
        try:
            new_entries = int(self.entries_per_page_entry.text())
            if new_entries > 0:
                self.entries_per_page = new_entries
                self.current_page = 0
                self.update_listbox()
                self.save_settings()
        except ValueError:
            pass

    def toggle_rolling(self):
        if self.is_rolling:
            self.pause_rolling()
        else:
            self.start_rolling()
        self.start_stop_button.setFocus()

    def start_rolling(self):
        if self.entries and any(prize['count'] > 0 for prize in self.prizes):
            self.rolling_window = RollingWindow(self.entries, self.prizes, self)
            self.rolling_window.show()
            self.rolling_window.start_rolling()
            self.hide()
        else:
            QMessageBox.warning(self, "无法开始抽奖", "没有可用的奖品或奖品数量为0。")

    def pause_rolling(self):
        if hasattr(self, 'rolling_window'):
            self.rolling_window.pause_rolling()

    def on_select(self, item):
        pass

    def import_excel(self):
        fname = QFileDialog.getOpenFileName(self, '导入Excel', os.getcwd(), "Excel files (*.xlsx)")
        if fname[0]:
            try:
                df = pd.read_excel(fname[0])
                self.entries = list(df.itertuples(index=False, name=None))
                self.current_id = max((entry[0] for entry in self.entries), default=0) + 1
                self.update_listbox()
            except Exception as e:
                QMessageBox.critical(self, "导入错误", f"导入Excel文件时发生错误: {str(e)}")

    def export_excel(self):
        if self.entries:
            fname = QFileDialog.getSaveFileName(self, '导出Excel', os.getcwd(), "Excel files (*.xlsx)")
            if fname[0]:
                try:
                    df = pd.DataFrame(self.entries, columns=['编号', '姓名'])
                    df.to_excel(fname[0], index=False)
                except Exception as e:
                    QMessageBox.critical(self, "导出错误", f"导出Excel文件时发生错误: {str(e)}")

    def exit_program(self):
        self.save_settings()
        self.save_data()
        QApplication.quit()

    def toggle_fullscreen(self):
        if self.is_fullscreen:
            self.showNormal()
            for i in range(self.layout().count()):
                item = self.layout().itemAt(i)
                if item.widget() and item.widget() != self.label:
                    item.widget().show()
        else:
            self.showFullScreen()
            for i in range(self.layout().count()):
                item = self.layout().itemAt(i)
                if item.widget() and item.widget() != self.label:
                    item.widget().hide()
        self.is_fullscreen = not self.is_fullscreen
        self.start_stop_button.setFocus()

    def add_prize(self):
        name, ok = QInputDialog.getText(self, "添加奖品", "请输入奖品名称（如'汽车'）：")
        if ok and name:
            count, ok = QInputDialog.getInt(self, "添加奖品", "请输入奖品数量（如1）：", 1, 1)
            if ok:
                self.prizes.append({'name': name, 'count': count, 'original_count': count})
                self.save_prizes()
                QMessageBox.information(self, "添加奖品", f"已添加奖品: {name} - {count}个")

    def view_prizes(self):
        if self.prizes:
            prize_info = '\n'.join([f"{prize['name']} - {prize['count']}个" for prize in self.prizes])
            QMessageBox.information(self, "查看奖品", f"当前奖品列表:\n{prize_info}")
        else:
            QMessageBox.information(self, "查看奖品", "当前没有奖品。")

    def modify_prize(self):
        if self.prizes:
            prize_names = [prize['name'] for prize in self.prizes]
            name, ok = QInputDialog.getItem(self, "修改奖品", "请选择要修改的奖品：", prize_names, 0, False)
            if ok and name:
                prize = next((p for p in self.prizes if p['name'] == name), None)
                if prize:
                    new_name, ok = QInputDialog.getText(self, "修改奖品", "请输入新的奖品名称：", text=prize['name'])
                    if ok and new_name:
                        new_count, ok = QInputDialog.getInt(self, "修改奖品", "请输入新的奖品数量：", value=prize['count'], min=1)
                        if ok:
                            prize['name'] = new_name
                            prize['count'] = new_count
                            prize['original_count'] = new_count
                            self.save_prizes()
                            QMessageBox.information(self, "修改奖品", f"奖品已修改为: {new_name} - {new_count}个")

    def delete_prize(self):
        if self.prizes:
            prize_names = [prize['name'] for prize in self.prizes]
            name, ok = QInputDialog.getItem(self, "删除奖品", "请选择要删除的奖品：", prize_names, 0, False)
            if ok and name:
                self.prizes = [prize for prize in self.prizes if prize['name'] != name]
                self.save_prizes()
                QMessageBox.information(self, "删除奖品", f"奖品 {name} 已删除。")

    def reset_lottery(self):
        # 确保每个奖品都有 'original_count' 属性并将其重置
        for prize in self.prizes:
            prize['count'] = prize['original_count']  # 使用 'original_count' 重置 'count'
        
        # 保存重置后的奖品状态
        self.save_prizes()

        # 关闭任何现存的滚动窗口
        if hasattr(self, 'rolling_window') and self.rolling_window:
            self.rolling_window.close()
            del self.rolling_window

        # 确保主窗口显示
        self.show()
        
        # 显示复位成功的消息
        QMessageBox.information(self, "复位抽奖", "抽奖状态已复位。")

    def open_prize_management(self):
        self.prize_management_window = PrizeManagementWindow(self.prizes, self)
        self.prize_management_window.show()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = RandomNumberRolling()
    app.aboutToQuit.connect(ex.save_data)
    app.aboutToQuit.connect(ex.save_settings)
    ex.show()
    sys.exit(app.exec_())