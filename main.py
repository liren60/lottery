import sys
import random
import pandas as pd
import os
import json
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
                             QPushButton, QListWidget, QScrollArea, QMessageBox, QFileDialog, 
                             QInputDialog, QMenuBar, QMenu, QSizePolicy)
from PyQt5.QtCore import Qt, QTimer, QEvent

class CustomLineEdit(QLineEdit):
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            self.parent().add_entry()
        else:
            super().keyPressEvent(event)

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
        self.label.setStyleSheet("color: white; font-size: 500px;")
        self.prize_label = QLabel("", self, alignment=Qt.AlignCenter)
        self.prize_label.setStyleSheet("color: yellow; font-size: 100px;")
        layout.addWidget(self.prize_label)
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
            if self.prizes:
                current_prize = self.prizes[self.current_prize_index]
                self.prize_label.setText(f"当前奖项: {current_prize['name']} ({current_prize['count']}个)")
            self.label.setStyleSheet(f"color: {random.choice(['red', 'green', 'blue', 'purple', 'orange'])}; font-size: 500px; font-weight: bold; text-shadow: 2px 2px 4px rgba(0,0,0,0.5);")

    def pause_rolling(self):
        self.is_rolling = False
        self.rolling_timer.stop()
        if self.entries:
            selected_entry = random.choice(self.entries)
            self.label.setText(f"{selected_entry[0]} {selected_entry[1]}")
            if self.prizes:
                current_prize = self.prizes[self.current_prize_index]
                self.prize_label.setText(f"当前奖项: {current_prize['name']} ({current_prize['count']}个)")
                current_prize['count'] -= 1
                if current_prize['count'] <= 0:
                    self.current_prize_index += 1
                    if self.current_prize_index >= len(self.prizes):
                        # 创建 QMessageBox 并设置样式
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
                        self.close()  # 关闭当前窗口
                        self.parent.show()  # 重新显示主窗口
                        return
            self.label.setStyleSheet("color: blue; font-size: 800px;")

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()
            self.parent.show()  # 在按下Escape键时显示主窗口
        elif event.key() == Qt.Key_Space:
            if self.is_rolling:
                self.pause_rolling()
            else:
                self.start_rolling()

def get_data_path():
    home = os.path.expanduser("~")
    data_dir = os.path.join(home, '.my_app_data')
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    return os.path.join(data_dir, 'data.xlsx')

def get_settings_path():
    home = os.path.expanduser("~")
    settings_dir = os.path.join(home, '.my_app_data')
    if not os.path.exists(settings_dir):
        os.makedirs(settings_dir)
    return os.path.join(settings_dir, 'settings.json')

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
        
        self.load_settings()
        self.initUI()
        self.load_data()
        self.load_prizes()

    def initUI(self):
        self.setWindowTitle("编号与姓名滚动抽奖")
        layout = QVBoxLayout()

        menubar = QMenuBar(self)
        file_menu = menubar.addMenu('文件')
        file_menu.addAction('导入 Excel', self.import_excel)
        file_menu.addAction('导出 Excel', self.export_excel)
        file_menu.addAction('退出', self.exit_program)
        prize_menu = menubar.addMenu('奖品管理')
        prize_menu.addAction('添加奖品', self.add_prize)
        prize_menu.addAction('查看奖品', self.view_prizes)
        prize_menu.addAction('修改奖品', self.modify_prize)
        prize_menu.addAction('删除奖品', self.delete_prize)
        layout.setMenuBar(menubar)

        self.label = QLabel("编号 姓名", self, alignment=Qt.AlignCenter)
        self.label.setStyleSheet("font-size: 40px;")
        self.label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout.addWidget(self.label)

        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("姓名", self))
        self.name_entry = CustomLineEdit(self)
        self.name_entry.setPlaceholderText("请输入姓名")
        self.name_entry.returnPressed.connect(self.add_entry)
        self.name_entry.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        name_layout.addWidget(self.name_entry)
        layout.addLayout(name_layout)

        button_layout = QHBoxLayout()
        self.add_button = QPushButton("添加", self)
        self.add_button.clicked.connect(self.add_entry)
        button_layout.addWidget(self.add_button)
        self.save_button = QPushButton("保存", self)
        self.save_button.clicked.connect(self.save_data)
        button_layout.addWidget(self.save_button)
        layout.addLayout(button_layout)

        self.listbox = QListWidget(self)
        self.listbox.setSelectionMode(QListWidget.ExtendedSelection)
        self.listbox.itemClicked.connect(self.on_select)
        self.listbox.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(self.listbox)
        layout.addWidget(scroll)
        layout.setStretchFactor(scroll, 1)

        page_layout = QHBoxLayout()
        self.page_label = QLabel(f"当前页: {self.current_page + 1} / {self.total_pages}", self)
        page_layout.addWidget(self.page_label)
        page_layout.addWidget(QLabel("每页显示:", self))
        self.entries_per_page_entry = QLineEdit(str(self.entries_per_page), self)
        self.entries_per_page_entry.returnPressed.connect(self.update_entries_per_page)
        page_layout.addWidget(self.entries_per_page_entry)
        self.entries_per_page_button = QPushButton("设置", self)
        self.entries_per_page_button.clicked.connect(self.update_entries_per_page)
        page_layout.addWidget(self.entries_per_page_button)
        self.prev_button = QPushButton("上一页", self)
        self.prev_button.clicked.connect(self.prev_page)
        page_layout.addWidget(self.prev_button)
        self.next_button = QPushButton("下一页", self)
        self.next_button.clicked.connect(self.next_page)
        page_layout.addWidget(self.next_button)
        layout.addLayout(page_layout)

        delete_modify_layout = QHBoxLayout()
        self.delete_button = QPushButton("删除", self)
        self.delete_button.clicked.connect(self.delete_entry)
        delete_modify_layout.addWidget(self.delete_button)
        self.modify_button = QPushButton("修改", self)
        self.modify_button.clicked.connect(self.modify_entry)
        delete_modify_layout.addWidget(self.modify_button)
        layout.addLayout(delete_modify_layout)

        import_export_layout = QHBoxLayout()
        self.import_button = QPushButton("导入 Excel", self)
        self.import_button.clicked.connect(self.import_excel)
        import_export_layout.addWidget(self.import_button)
        self.export_button = QPushButton("导出 Excel", self)
        self.export_button.clicked.connect(self.export_excel)
        import_export_layout.addWidget(self.export_button)
        layout.addLayout(import_export_layout)

        start_stop_layout = QHBoxLayout()
        self.start_stop_button = QPushButton("开始(空格快捷键)", self)
        self.start_stop_button.clicked.connect(self.toggle_rolling)
        self.start_stop_button.setShortcut('Space')
        start_stop_layout.addWidget(self.start_stop_button)
        self.reset_button = QPushButton("复位", self)
        self.reset_button.clicked.connect(self.reset_lottery)
        start_stop_layout.addWidget(self.reset_button)
        self.exit_app_button = QPushButton("退出程序", self)
        self.exit_app_button.clicked.connect(self.exit_program)
        self.exit_app_button.setShortcut('Esc')
        start_stop_layout.addWidget(self.exit_app_button)
        layout.addLayout(start_stop_layout)

        self.setLayout(layout)
        self.resize(*self.window_size)

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
        file_path = get_data_path()
        if os.path.exists(file_path):
            try:
                df = pd.read_excel(file_path)
                self.entries = list(df.itertuples(index=False, name=None))
                self.current_id = max((entry[0] for entry in self.entries), default=0) + 1
                self.update_listbox()
                QMessageBox.information(self, "加载成功", "数据已成功从Excel文件中加载！")
            except Exception as e:
                QMessageBox.critical(self, "加载错误", f"加载Excel文件时发生错误: {str(e)}")
        else:
            QMessageBox.information(self, "数据加载", "默认文件不存在。")

    def save_data(self):
        if not self.entries:
            QMessageBox.warning(self, "没有数据", "没有要保存的数据！")
            return
        try:
            df = pd.DataFrame(self.entries, columns=['编号', '姓名'])
            df.to_excel(get_data_path(), index=False)
            self.save_backup()
            QMessageBox.information(self, "保存成功", "数据已成功保存至Excel文件！")
        except Exception as e:
            QMessageBox.critical(self, "保存错误", f"保存Excel文件时发生错误: {str(e)}")

    def save_backup(self):
        backup_dir = os.path.join(os.path.expanduser("~"), '.my_app_data', 'backups')
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)
        backup_files = sorted(os.listdir(backup_dir))
        if len(backup_files) >= 10:
            os.remove(os.path.join(backup_dir, backup_files[0]))
        backup_file_path = os.path.join(backup_dir, f'data_{pd.Timestamp.now().strftime("%Y%m%d%H%M%S")}.xlsx')
        df = pd.DataFrame(self.entries, columns=['编号', '姓名'])
        df.to_excel(backup_file_path, index=False)

    def add_entry(self):
        name = self.name_entry.text().strip()
        if not name:
            QMessageBox.warning(self, "输入错误", "请输入姓名！")
            return
        if any(entry[1] == name for entry in self.entries):
            QMessageBox.warning(self, "输入错误", "已有相同的姓名！")
            return
        self.entries.append((self.current_id, name))
        self.current_id += 1
        self.update_listbox()
        self.name_entry.clear()

    def delete_entry(self):
        if not self.listbox.selectedItems():
            QMessageBox.warning(self, "没有选择", "请先选择要删除的编号和姓名。")
            return
        for item in reversed(self.listbox.selectedItems()):
            self.entries.pop(self.listbox.row(item))
        self.update_listbox()

    def modify_entry(self):
        if not self.listbox.selectedItems():
            QMessageBox.warning(self, "没有选择", "请先选择要修改的编号和姓名。")
            return
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
            else:
                QMessageBox.warning(self, "输入错误", "每页显示的条目数必须大于0！")
        except ValueError:
            QMessageBox.warning(self, "输入错误", "请输入一个有效的数字！")

    def toggle_rolling(self):
        if self.is_rolling:
            self.pause_rolling()
        else:
            self.start_rolling()
        self.start_stop_button.setFocus()

    def start_rolling(self):
        if not self.entries:
            QMessageBox.warning(self, "没有数据", "请先添加编号和姓名！")
            return
        self.rolling_window = RollingWindow(self.entries, self.prizes, self)
        self.rolling_window.show()
        self.rolling_window.start_rolling()
        self.hide()  # 在进行抽奖时隐藏主窗口

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
        if not self.entries:
            QMessageBox.warning(self, "没有数据", "没有要导出的数据！")
            return
        fname = QFileDialog.getSaveFileName(self, '导出Excel', os.getcwd(), "Excel files (*.xlsx)")
        if fname[0]:
            try:
                df = pd.DataFrame(self.entries, columns=['编号', '姓名'])
                df.to_excel(fname[0], index=False)
            except Exception as e:
                QMessageBox.critical(self, "导出错误", f"导出Excel文件时发生错误: {str(e)}")

    def exit_program(self):
        self.save_settings()
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

    def load_settings(self):
        settings_path = get_settings_path()
        if os.path.exists(settings_path):
            with open(settings_path, 'r') as f:
                settings = json.load(f)
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
        settings_path = get_settings_path()
        with open(settings_path, 'w') as f:
            json.dump(settings, f)

    def load_prizes(self):
        self.prizes = []  # 重置奖品列表
        prize_file_path = os.path.join(os.path.expanduser("~"), '.my_app_data', 'prizes.json')
        if os.path.exists(prize_file_path):
            with open(prize_file_path, 'r') as f:
                self.prizes = json.load(f)

    def add_prize(self):
        name, ok = QInputDialog.getText(self, "添加奖品", "请输入奖品名称（如'汽车'）：")
        if ok and name:
            count, ok = QInputDialog.getInt(self, "添加奖品", "请输入奖品数量（如1）：", 1, 1)
            if ok:
                self.prizes.append({'name': name, 'count': count, 'original_count': count})
                self.save_prizes()
                QMessageBox.information(self, "添加奖品", f"已添加奖品: {name} - {count}个")

    def view_prizes(self):
        if not self.prizes:
            QMessageBox.information(self, "查看奖品", "当前没有奖品。")
            return
        prize_info = '\n'.join([f"{prize['name']} - {prize['count']}个" for prize in self.prizes])
        QMessageBox.information(self, "查看奖品", f"当前奖品列表:\n{prize_info}")

    def modify_prize(self):
        if not self.prizes:
            QMessageBox.information(self, "修改奖品", "当前没有奖品。")
            return
        prize_names = [prize['name'] for prize in self.prizes]
        name, ok = QInputDialog.getItem(self, "修改奖品", "请选择要修改的奖品：", prize_names, 0, False)
        if ok and name:
            prize = next((prize for prize in self.prizes if prize['name'] == name), None)
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
        if not self.prizes:
            QMessageBox.information(self, "删除奖品", "当前没有奖品。")
            return
        prize_names = [prize['name'] for prize in self.prizes]
        name, ok = QInputDialog.getItem(self, "删除奖品", "请选择要删除的奖品：", prize_names, 0, False)
        if ok and name:
            self.prizes = [prize for prize in self.prizes if prize['name'] != name]
            self.save_prizes()
            QMessageBox.information(self, "删除奖品", f"奖品 {name} 已删除。")

    def save_prizes(self):
        prize_file_path = os.path.join(os.path.expanduser("~"), '.my_app_data', 'prizes.json')
        with open(prize_file_path, 'w') as f:
            json.dump(self.prizes, f)

    def reset_lottery(self):
        for prize in self.prizes:
            # 如果奖品没有 'original_count' 键，就用当前的 'count' 作为 'original_count'
            if 'original_count' not in prize:
                prize['original_count'] = prize['count']
            prize['count'] = prize['original_count']
        if hasattr(self, 'rolling_window'):
            self.rolling_window.close()
        self.show()  # 确保主窗口显示
        QMessageBox.information(self, "复位抽奖", "抽奖状态已复位。")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = RandomNumberRolling()
    app.aboutToQuit.connect(ex.save_data)
    app.aboutToQuit.connect(ex.save_settings)
    ex.show()
    sys.exit(app.exec_())