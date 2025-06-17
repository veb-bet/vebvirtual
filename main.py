import sys
import json
import shutil
import os
import time
import psutil
import requests
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QLabel,
                             QLineEdit, QPushButton, QMessageBox, QSystemTrayIcon, QMenu)
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QProcess, QTimer
from PyQt6.QtGui import QAction
from ss_parser import parse_ss_link

CONFIG_PATH = os.path.expanduser("~/.config/vebvpn/config.json") 
SS_LOCAL_EXECUTABLE = "ss-local"
ICON_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "icon.png") 
TEST_URL = "https://www.google.com"
TEST_TIMEOUT = 5

class ShadowsocksApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("vebvpn")
        self.setFixedSize(400, 300) 
        self.setWindowIcon(QIcon(ICON_PATH))
        os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
        self.ss_process = None
        self.connection_status = False
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
            QLabel#statusLabel {
                font-weight: bold;
                font-size: 14px;
                padding: 5px;
                border-radius: 4px;
            }
        """
        )

        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(15, 15, 15, 15)

        self.label = QLabel("Вставьте ss:// ссылку")
        layout.addWidget(self.label)

        self.input = QLineEdit()
        layout.addWidget(self.input)

        # Статусная панель
        status_layout = QVBoxLayout()
        status_layout.setSpacing(5)
        
        self.status_label = QLabel("Статус: Отключено")
        self.status_label.setObjectName("statusLabel")
        self.status_label.setStyleSheet("background-color: #d32f2f; padding: 5px;")
        status_layout.addWidget(self.status_label)
        
        self.speed_label = QLabel("Скорость: ↑ 0 KB/s, ↓ 0 KB/s")
        status_layout.addWidget(self.speed_label)
        
        self.latency_label = QLabel("Задержка: -")
        status_layout.addWidget(self.latency_label)
        
        layout.addLayout(status_layout)

        self.connect_button = QPushButton("Подключить")
        self.connect_button.clicked.connect(self.toggle_vpn)
        layout.addWidget(self.connect_button)

        self.setLayout(layout)
        self.load_last()

        # Таймеры для обновления информации
        self.speed_timer = QTimer(self)
        self.speed_timer.timeout.connect(self.update_speed)
        self.status_timer = QTimer(self)
        self.status_timer.timeout.connect(self.check_connection_status)

        # Переменные для отслеживания скорости
        self.prev_upload = 0
        self.prev_download = 0
        self.prev_time = time.time()

    def create_tray(self):
        self.tray = QSystemTrayIcon(QIcon(ICON_PATH))
        self.tray.setToolTip("vebvpn")

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
            self.stop_vpn()
            return

        ss_url = self.input.text().strip()
        try:
            config = parse_ss_link(ss_url)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))
            return

        self.save_last(ss_url)

        # Используем временную директорию
        config_dir = os.path.expanduser("~/.config/vebvpn")
        os.makedirs(config_dir, exist_ok=True)
        config_path = os.path.join(config_dir, "temp_config.json")
        
        with open(config_path, 'w') as f:
            json.dump(config, f)

        # Проверяем наличие ss-local в PATH
        ss_local_path = shutil.which("ss-local")
        if not ss_local_path:
            QMessageBox.critical(self, "Ошибка", "ss-local не найден в PATH. Убедитесь, что shadowsocks-libev установлен.")
            return

        try:
            self.ss_process = QProcess()
            # Запускаем с абсолютным путем
            self.ss_process.start(ss_local_path, ["-c", config_path, "-u"])
            
            # Ждем запуска процесса
            if not self.ss_process.waitForStarted(3000):
                raise Exception("Не удалось запустить ss-local")
                
            # Обновляем UI
            self.connect_button.setText("Отключить")
            self.status_label.setText("Статус: Подключение...")
            self.status_label.setStyleSheet("background-color: #ffa000; padding: 5px;")
            
            # Запускаем мониторинг
            self.speed_timer.start(1000)
            self.status_timer.start(3000)
            self.prev_time = time.time()
            
            # Инициализируем счетчики сети
            net_io = psutil.net_io_counters()
            self.prev_upload = net_io.bytes_sent
            self.prev_download = net_io.bytes_recv
            
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка подключения: {str(e)}")
            if self.ss_process:
                self.ss_process.kill()
                self.ss_process = None

    def stop_vpn(self):
        if self.ss_process:
            self.ss_process.kill()
            self.ss_process = None
            
        self.connection_status = False
        self.connect_button.setText("Подключить")
        self.status_label.setText("Статус: Отключено")
        self.status_label.setStyleSheet("background-color: #d32f2f; padding: 5px;")
        self.speed_label.setText("Скорость: ↑ 0 KB/s, ↓ 0 KB/s")
        self.latency_label.setText("Задержка: -")
        
        # Останавливаем таймеры
        self.speed_timer.stop()
        self.status_timer.stop()
        
        QMessageBox.information(self, "Отключено", "Shadowsocks отключен")

    def update_speed(self):
        try:
            net_io = psutil.net_io_counters()
            current_upload = net_io.bytes_sent
            current_download = net_io.bytes_recv
            current_time = time.time()
            
            time_diff = current_time - self.prev_time
            if time_diff > 0:
                upload_speed = (current_upload - self.prev_upload) / time_diff
                download_speed = (current_download - self.prev_download) / time_diff
                
                # Конвертируем в KB/s
                upload_speed_kb = upload_speed / 1024
                download_speed_kb = download_speed / 1024
                
                self.speed_label.setText(f"Скорость: ↑ {upload_speed_kb:.1f} KB/s, ↓ {download_speed_kb:.1f} KB/s")
            
            self.prev_upload = current_upload
            self.prev_download = current_download
            self.prev_time = current_time
        except Exception as e:
            print(f"Ошибка обновления скорости: {str(e)}")

    def check_connection_status(self):
        try:
            # Проверяем доступность процесса
            if not self.ss_process or self.ss_process.state() != QProcess.ProcessState.Running:
                self.stop_vpn()
                return

            # Проверяем работоспособность прокси
            start_time = time.time()
            response = requests.get(
                TEST_URL,
                proxies={'http': 'socks5://127.0.0.1:1080', 'https': 'socks5://127.0.0.1:1080'},
                timeout=TEST_TIMEOUT
            )
            latency = int((time.time() - start_time) * 1000)  # в мс
            
            if response.status_code == 200:
                self.connection_status = True
                self.status_label.setText("Статус: Подключено")
                self.status_label.setStyleSheet("background-color: #388e3c; padding: 5px;")
                self.latency_label.setText(f"Задержка: {latency} мс")
            else:
                self.connection_status = False
                self.status_label.setText("Статус: Ошибка подключения")
                self.status_label.setStyleSheet("background-color: #d32f2f; padding: 5px;")
                
        except requests.exceptions.RequestException:
            self.connection_status = False
            self.status_label.setText("Статус: Нет соединения")
            self.status_label.setStyleSheet("background-color: #d32f2f; padding: 5px;")
            self.latency_label.setText("Задержка: -")
        except Exception as e:
            print(f"Ошибка проверки статуса: {str(e)}")

    def exit_app(self):
        self.stop_vpn()
        self.tray.hide()
        QApplication.quit()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ShadowsocksApp()
    window.show()
    sys.exit(app.exec())