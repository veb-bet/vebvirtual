from PyQt6.QtGui import QPalette, QColor

def apply_theme(window, theme):
    palette = QPalette()
    accent = QColor(128, 0, 255)
    if theme == "dark":
        palette.setColor(QPalette.ColorRole.Window, QColor(30, 30, 30))
        palette.setColor(QPalette.ColorRole.WindowText, QColor(220, 220, 220))
        palette.setColor(QPalette.ColorRole.Button, QColor(40, 40, 40))
        palette.setColor(QPalette.ColorRole.ButtonText, accent)
    else:
        palette.setColor(QPalette.ColorRole.Window, QColor(245, 245, 245))
        palette.setColor(QPalette.ColorRole.WindowText, QColor(30, 30, 30))
        palette.setColor(QPalette.ColorRole.Button, QColor(230, 230, 255))
        palette.setColor(QPalette.ColorRole.ButtonText, accent)
    window.setPalette(palette)
