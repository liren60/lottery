import os
import json
import random
import pandas as pd
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
                             QPushButton, QListWidget, QScrollArea, QMessageBox, QFileDialog, 
                             QInputDialog, QMenuBar, QMenu)
from PyQt5.QtCore import Qt, QTimer
from custom_line_edit import CustomLineEdit
from rolling_window import RollingWindow

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

        self.load_settings()  # 加载设置
        self.initUI()
        self.load_data()

    def initUI(self):
        self.setWindowTitle("编号与姓名滚动抽奖")
        layout = QVBoxLayout()

        # 创建菜单栏
        menubar = QMenuBar(self)
        file_menu = menubar.addMenu('文件')
        file_menu.addAction('导入 Excel', self.import_excel)
        file_menu.addAction('导出 Excel', self.export_excel)
        file_menu.addAction('退出', self.exit_program)
        layout.setMenuBar(menubar)

        # 标题
        self.label = QLabel("编号 姓名", self, alignment=Qt.AlignCenter)
        self.label.setStyleSheet("font-size: 40px;")  # 设置初始字体大小
        layout.addWidget(self.label)

        # 姓名输入框
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("姓名", self))
        self.name_entry = CustomLineEdit(self)  # 使用自定义的LineEdit
        self.name_entry.setPlaceholderText("请输入姓名")  # 设置提示词
        self.name_entry.returnPressed.connect(self.add_entry)  # 添加回车快捷键
        name_layout.addWidget(self.name_entry)
        layout.addLayout(name_layout)

        # 添加和保存按钮
        button_layout = QHBoxLayout()
        self.add_button = QPushButton("添加", self)
        self.add_button.clicked.connect(self.add_entry)
        button_layout.addWidget(self.add_button)
        self.save_button = QPushButton("保存", self)
        self.save_button.clicked.connect(self.save_data)
        button_layout.addWidget(self.save_button)
        layout.addLayout(button_layout)

        # 显示条目的列表框
        self.listbox = QListWidget(self)
        self.listbox.setSelectionMode(QListWidget.ExtendedSelection)  # 设置为扩展选择模式
        self.listbox.itemClicked.connect(self.on_select)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(self.listbox)
        layout.addWidget(scroll)
        layout.setStretchFactor(scroll, 1)

        # 分页控制
        page_layout = QHBoxLayout()
        self.page_label = QLabel(f"当前页: {self.current_page + 1} / {self.total_pages}", self)
        page_layout.addWidget(self.page_label)
        page_layout.addWidget(QLabel("每页显示:", self))
        self.entries_per_page_entry = QLineEdit(str(self.entries_per_page), self)
        self.entries_per_page_entry.returnPressed.connect(self.update_entries_per_page)  # 添加回车快捷键
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

        # 删除和修改按钮
        delete_modify_layout = QHBoxLayout()
        self.delete_button = QPushButton("删除", self)
        self.delete_button.clicked.connect(self.delete_entry)
        delete_modify_layout.addWidget(self.delete_button)
        self.modify_button = QPushButton("修改", self)
        self.modify_button.clicked.connect(self.modify_entry)
        delete_modify_layout.addWidget(self.modify_button)
        layout.addLayout(delete_modify_layout)

        # 导入/导出Excel
        import_export_layout = QHBoxLayout()
        self.import_button = QPushButton("导入 Excel", self)
        self.import_button.clicked.connect(self.import_excel)
        import_export_layout.addWidget(self.import_button)
        self.export_button = QPushButton("导出 Excel", self)
        self.export_button.clicked.connect(self.export_excel)
        import_export_layout.addWidget(self.export_button)
        layout.addLayout(import_export_layout)

        # 开始/停止和退出按钮
        start_stop_layout = QHBoxLayout()
        self.start_stop_button = QPushButton("开始(空格快捷键)", self)
        self.start_stop_button.clicked.connect(self.toggle_rolling)
        self.start_stop_button.setShortcut('Space')
        start_stop_layout.addWidget(self.start_stop_button)
        self.exit_app_button = QPushButton("退出程序", self)
        self.exit_app_button.clicked.connect(self.exit_program)
        self.exit_app_button.setShortcut('Esc')
        start_stop_layout.addWidget(self.exit_app_button)
        layout.addLayout(start_stop_layout)

        self.setLayout(layout)

        # 设置窗口大小
        self.resize(*self.window_size)

    def load_data(self):
        exe_dir = os.path.dirname(os.path.abspath(sys.executable))
        file_path = os.path.join(exe_dir, 'data.xlsx')
        if os.path.exists(file_path):
            try:
                df = pd.read_excel(file_path)
                self.entries = list(df.itertuples(index=False, name=None))
                self.current_id = max((entry[0] for entry in self.entries), default=0) + 1
                self.update_listbox()
            except Exception as e:
                QMessageBox.critical(self, "加载错误", f"加载Excel文件时发生错误: {str(e)}")
        else:
            QMessageBox.information(self, "数据加载", "默认文件不存在。")

    def save_data(self):
        if not self.entries:
            QMessageBox.warning(self, "没有数据", "没有要保存的数据！")
            return
        exe_dir = os.path.dirname(os.path.abspath(sys.executable))
        file_path = os.path.join(exe_dir, 'data.xlsx')
        try:
            df = pd.DataFrame(self.entries, columns=['编号', '姓名'])
            df.to_excel(file_path, index=False)
            self.save_backup()
        except Exception as e:
            QMessageBox.critical(self, "保存错误", f"保存Excel文件时发生错误: {str(e)}")

    def save_backup(self):
        exe_dir = os.path.dirname(os.path.abspath(sys.executable))
        backup_dir = os.path.join(exe_dir, 'backups')
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
                self.save_settings()  # 保存设置
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
        self.rolling_window = RollingWindow(self.entries)
        self.rolling_window.show()
        self.rolling_window.start_rolling()

    def pause_rolling(self):
        if hasattr(self, 'rolling_window'):
            self.rolling_window.pause_rolling()

    def on_select(self, item):
        pass  # 选择逻辑在键盘事件中处理

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
        self.save_data()
        self.save_settings()  # 保存设置
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
        settings_path = os.path.join(os.path.dirname(os.path.abspath(sys.executable)), 'settings.json')
        if os.path.exists(settings_path):
            with open(settings_path, 'r') as f:
                settings = json.load(f)
                self.entries_per_page = settings.get('entries_per_page', 10)
                self.current_page = settings.get('current_page', 0)
                self.window_size = tuple(settings.get('window_size', (800, 1000)))

    def save_settings(self):
        settings = {
            'entries_per_page': self.entries_per_page,
            'current_page': self.current_page,
            'window_size': (self.width(), self.height())
        }
        settings_path = os.path.join(os.path.dirname(os.path.abspath(sys.executable)), 'settings.json')
        with open(settings_path, 'w') as f:
            json.dump(settings, f)
