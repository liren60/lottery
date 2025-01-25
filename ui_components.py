from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QListWidget, QScrollArea, QFileDialog, QInputDialog, QMenuBar, QMenu, QSizePolicy
from PyQt5.QtCore import Qt

class CustomLineEdit(QLineEdit):
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            self.parent().add_entry()
        else:
            super().keyPressEvent(event)

def create_menu_bar(parent):
    menubar = QMenuBar(parent)
    file_menu = menubar.addMenu('文件')
    file_menu.addAction('导入 Excel', parent.import_excel)
    file_menu.addAction('导出 Excel', parent.export_excel)
    file_menu.addAction('退出', parent.exit_program)
    
    prize_menu = menubar.addMenu('奖品管理')
    prize_menu.addAction('添加奖品', parent.add_prize)
    prize_menu.addAction('查看奖品', parent.view_prizes)
    prize_menu.addAction('修改奖品', parent.modify_prize)
    prize_menu.addAction('删除奖品', parent.delete_prize)
    return menubar

def setup_main_ui(parent):
    layout = QVBoxLayout()
    layout.setMenuBar(create_menu_bar(parent))

    parent.label = QLabel("编号 姓名", parent, alignment=Qt.AlignCenter)
    parent.label.setStyleSheet("font-size: 40px;")
    parent.label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
    layout.addWidget(parent.label)

    name_layout = QHBoxLayout()
    name_layout.addWidget(QLabel("姓名", parent))
    parent.name_entry = CustomLineEdit(parent)
    parent.name_entry.setPlaceholderText("请输入姓名")
    parent.name_entry.returnPressed.connect(parent.add_entry)
    parent.name_entry.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
    name_layout.addWidget(parent.name_entry)
    layout.addLayout(name_layout)

    button_layout = QHBoxLayout()
    parent.add_button = QPushButton("添加", parent)
    parent.add_button.clicked.connect(parent.add_entry)
    button_layout.addWidget(parent.add_button)
    parent.save_button = QPushButton("保存", parent)
    parent.save_button.clicked.connect(parent.save_data)
    button_layout.addWidget(parent.save_button)
    layout.addLayout(button_layout)

    parent.listbox = QListWidget(parent)
    parent.listbox.setSelectionMode(QListWidget.ExtendedSelection)
    parent.listbox.itemClicked.connect(parent.on_select)
    parent.listbox.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
    scroll = QScrollArea()
    scroll.setWidgetResizable(True)
    scroll.setWidget(parent.listbox)
    layout.addWidget(scroll)
    layout.setStretchFactor(scroll, 1)

    page_layout = QHBoxLayout()
    parent.page_label = QLabel(f"当前页: 1 / 1", parent)
    page_layout.addWidget(parent.page_label)
    page_layout.addWidget(QLabel("每页显示:", parent))
    parent.entries_per_page_entry = QLineEdit("10", parent)
    parent.entries_per_page_entry.returnPressed.connect(parent.update_entries_per_page)
    page_layout.addWidget(parent.entries_per_page_entry)
    parent.entries_per_page_button = QPushButton("设置", parent)
    parent.entries_per_page_button.clicked.connect(parent.update_entries_per_page)
    page_layout.addWidget(parent.entries_per_page_button)
    parent.prev_button = QPushButton("上一页", parent)
    parent.prev_button.clicked.connect(parent.prev_page)
    page_layout.addWidget(parent.prev_button)
    parent.next_button = QPushButton("下一页", parent)
    parent.next_button.clicked.connect(parent.next_page)
    page_layout.addWidget(parent.next_button)
    layout.addLayout(page_layout)

    delete_modify_layout = QHBoxLayout()
    parent.delete_button = QPushButton("删除", parent)
    parent.delete_button.clicked.connect(parent.delete_entry)
    delete_modify_layout.addWidget(parent.delete_button)
    parent.modify_button = QPushButton("修改", parent)
    parent.modify_button.clicked.connect(parent.modify_entry)
    delete_modify_layout.addWidget(parent.modify_button)
    layout.addLayout(delete_modify_layout)

    import_export_layout = QHBoxLayout()
    parent.import_button = QPushButton("导入 Excel", parent)
    parent.import_button.clicked.connect(parent.import_excel)
    import_export_layout.addWidget(parent.import_button)
    parent.export_button = QPushButton("导出 Excel", parent)
    parent.export_button.clicked.connect(parent.export_excel)
    import_export_layout.addWidget(parent.export_button)
    layout.addLayout(import_export_layout)

    start_stop_layout = QHBoxLayout()
    parent.start_stop_button = QPushButton("开始(空格快捷键)", parent)
    parent.start_stop_button.clicked.connect(parent.toggle_rolling)
    parent.start_stop_button.setShortcut('Space')
    start_stop_layout.addWidget(parent.start_stop_button)
    parent.reset_button = QPushButton("复位", parent)
    parent.reset_button.clicked.connect(parent.reset_lottery)
    start_stop_layout.addWidget(parent.reset_button)
    parent.exit_app_button = QPushButton("退出程序", parent)
    parent.exit_app_button.clicked.connect(parent.exit_program)
    parent.exit_app_button.setShortcut('Esc')
    start_stop_layout.addWidget(parent.exit_app_button)
    layout.addLayout(start_stop_layout)

    return layout