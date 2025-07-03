import sys
import logging
from PyQt6.QtWidgets import QApplication
from ui import MainWindow
from state import load_last_key

# Настройка логирования
logging.basicConfig(
    filename="vebforvpn.log",
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(module)s: %(message)s"
)

def main():
    logging.info("Запуск приложения vebforvpn")
    app = QApplication(sys.argv)
    window = MainWindow()
    last_key = load_last_key()
    if last_key:
        logging.info("Загружен последний ключ")
        window.set_key(last_key)
    window.show()
    # Добавим предупреждение, если xray не найден
    import shutil
    if shutil.which("xray") is None:
        from PyQt6.QtWidgets import QMessageBox
        logging.error("Не найден исполняемый файл 'xray'")
        QMessageBox.critical(window, "Ошибка", "Не найден исполняемый файл 'xray'.\nУстановите xray-core и убедитесь, что он в PATH.")
    # Логируем завершение приложения
    exit_code = app.exec()
    logging.info(f"Завершение приложения, код выхода: {exit_code}")
    # Для отладки: логируем, что приложение завершилось штатно
    if exit_code == 0:
        logging.info("Приложение завершено штатно (VPN отключён или закрыто пользователем)")
    else:
        logging.warning(f"Приложение завершено с ошибкой, код: {exit_code}")
    sys.exit(exit_code)

if __name__ == "__main__":
    main()
