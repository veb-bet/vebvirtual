import subprocess
import tempfile
import os
import threading
import time
import shutil
from parser import parse_key, generate_xray_config


class VPNManager:
    def __init__(self, status_callback):
        self.proc = None
        self.status_callback = status_callback
        self.monitor_thread = None
        self.running = False

    def is_running(self):
        return self.proc is not None and self.proc.poll() is None

    def start(self, key):
        # Check if xray binary is available
        if shutil.which("xray") is None:
            self.status_callback("Ошибка", 0, "Не найден исполняемый файл 'xray'. Установите xray-core и убедитесь, что он в PATH.")
            return
        config = parse_key(key)
        if not config:
            self.status_callback("Ошибка", 0, "Неверный ключ")
            return
        xray_conf = generate_xray_config(config)
        with tempfile.NamedTemporaryFile("w", delete=False, suffix=".json") as f:
            f.write(xray_conf)
            conf_path = f.name
        self.proc = subprocess.Popen(
            ["xray", "-c", conf_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        self.running = True
        self.status_callback("Подключено", 0, "")
        self.monitor_thread = threading.Thread(target=self.monitor, daemon=True)
        self.monitor_thread.start()

    def stop(self):
        if self.proc:
            self.proc.terminate()
            self.proc = None
        self.running = False
        self.status_callback("Отключено", 0, "")

    def monitor(self):
        while self.running and self.is_running():
            # ...existing code...
            speed = 0  # TODO: parse speed from xray logs or use netstat
            self.status_callback("Подключено", speed, "")
            time.sleep(1)
        if self.running:
            self.status_callback("Ошибка", 0, "VPN отключён")