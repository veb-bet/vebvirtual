from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QLineEdit, QPushButton, QLabel, QComboBox, QHBoxLayout
)
from PyQt6.QtCore import Qt, QTimer
from theme import apply_theme
from vpn import VPNManager
from state import save_last_key

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("vebforvpn")
        self.setMinimumSize(400, 250)
        self.vpn_manager = VPNManager(self.on_status_update)
        self.init_ui()
        apply_theme(self, "light")

    def init_ui(self):
        central = QWidget()
        layout = QVBoxLayout()
        self.key_input = QLineEdit()
        self.key_input.setPlaceholderText("Вставьте VPN ключ...")
        self.status_label = QLabel("Отключено")
        self.speed_label = QLabel("Скорость: 0 кбит/с")
        self.error_label = QLabel("")
        self.theme_box = QComboBox()
        self.theme_box.addItems(["Светлая", "Тёмная"])
        self.theme_box.currentIndexChanged.connect(self.change_theme)
        self.connect_btn = QPushButton("Подключиться")
        self.connect_btn.clicked.connect(self.toggle_vpn)

        layout.addWidget(self.key_input)
        layout.addWidget(self.connect_btn)
        layout.addWidget(self.status_label)
        layout.addWidget(self.speed_label)
        layout.addWidget(self.error_label)
        hlayout = QHBoxLayout()
        hlayout.addWidget(QLabel("Тема:"))
        hlayout.addWidget(self.theme_box)
        layout.addLayout(hlayout)
        central.setLayout(layout)
        self.setCentralWidget(central)

    def set_key(self, key):
        self.key_input.setText(key)

    def change_theme(self, idx):
        theme = "light" if idx == 0 else "dark"
        apply_theme(self, theme)

    def toggle_vpn(self):
        key = self.key_input.text().strip()
        if not key:
            self.error_label.setText("Введите ключ!")
            return
        save_last_key(key)
        if self.vpn_manager.is_running():
            self.vpn_manager.stop()
            self.connect_btn.setText("Подключиться")
        else:
            self.vpn_manager.start(key)
            self.connect_btn.setText("Отключить")

    def on_status_update(self, status, speed=0, error=""):
        self.status_label.setText(status)
        self.speed_label.setText(f"Скорость: {speed} кбит/с")
        self.error_label.setText(error)
