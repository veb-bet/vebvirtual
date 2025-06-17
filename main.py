import sys
import json
import subprocess
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QLabel,
                             QLineEdit, QPushButton, QMessageBox, QSystemTrayIcon, QMenu)
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QProcess
from PyQt6.QtGui import QAction
from ss_parser import parse_ss_link
import os

CONFIG_PATH = "config.json"
SS_LOCAL_EXECUTABLE = "ss-local.exe"
ICON_PATH = "icon.png"


class ShadowsocksApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PurpleShadowsocks")
        self.setFixedSize(400, 250)
        self.setWindowIcon(QIcon(ICON_PATH))

        self.ss_process = None
        self.create_tray()

        self.setStyleSheet("""
            QWidget {
                background-color: #0f0f0f;
                color: #eeeeee;
                font-family: 'Segoe UI';
            }
            QLineEdit, QPushButton {
                font-size: 14px;
                padding: 8px;
                border-radius: 6px;
            }
            QLineEdit {
                background-color: #222222;
                color: #dddddd;
                border: 1px solid #444;
            }
            QPushButton {
                background-color: #6A0DAD;
                color: white;
            }
            QPushButton:hover {
                background-color: #7B1FA2;
            }
        """
        )

        layout = QVBoxLayout()

        self.label = QLabel("Вставьте ss:// ссылку")
        layout.addWidget(self.label)

        self.input = QLineEdit()
        layout.addWidget(self.input)

        self.connect_button = QPushButton("Подключить")
        self.connect_button.clicked.connect(self.toggle_vpn)
        layout.addWidget(self.connect_button)

        self.setLayout(layout)
        self.load_last()

    def create_tray(self):
        self.tray = QSystemTrayIcon(QIcon(ICON_PATH))
        self.tray.setToolTip("PurpleShadowsocks")

        menu = QMenu()
        show_action = QAction("Показать окно")
        show_action.triggered.connect(self.showNormal)
        menu.addAction(show_action)

        quit_action = QAction("Выход")
        quit_action.triggered.connect(self.exit_app)
        menu.addAction(quit_action)

        self.tray.setContextMenu(menu)
        self.tray.show()

    def load_last(self):
        if os.path.exists(CONFIG_PATH):
            with open(CONFIG_PATH, 'r') as f:
                data = json.load(f)
                self.input.setText(data.get("ss_url", ""))

    def save_last(self, ss_url):
        with open(CONFIG_PATH, 'w') as f:
            json.dump({"ss_url": ss_url}, f)

    def toggle_vpn(self):
        if self.ss_process:
            self.ss_process.kill()
            self.ss_process = None
            self.connect_button.setText("Подключить")
            QMessageBox.information(self, "Отключено", "Shadowsocks отключен")
            return

        ss_url = self.input.text().strip()
        try:
            config = parse_ss_link(ss_url)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))
            return

        self.save_last(ss_url)

        config_path = "temp_config.json"
        with open(config_path, 'w') as f:
            json.dump(config, f)

        if not os.path.exists(SS_LOCAL_EXECUTABLE):
            QMessageBox.critical(self, "Ошибка", f"Не найден {SS_LOCAL_EXECUTABLE}")
            return

        self.ss_process = QProcess()
        self.ss_process.start(SS_LOCAL_EXECUTABLE, ["-c", config_path])
        self.connect_button.setText("Отключить")
        QMessageBox.information(self, "Подключено", f"Shadowsocks подключен на порт {config['local_port']}")

    def exit_app(self):
        if self.ss_process:
            self.ss_process.kill()
        self.tray.hide()
        QApplication.quit()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ShadowsocksApp()
    window.show()
    sys.exit(app.exec())
