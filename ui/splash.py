import time

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QLabel, QProgressBar, QSplashScreen, QVBoxLayout, QWidget

from ui.widgets import PulseIcon
from utils.config import LOGO_PATH
from utils.styles import COLORS


def mostrar_splash(app):
    splash = QSplashScreen()
    splash.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
    splash.setStyleSheet("background-color:#050505;")

    screen_geometry = app.desktop().screenGeometry()
    splash.setFixedSize(screen_geometry.width(), screen_geometry.height())

    splash_layout = QVBoxLayout(splash)
    splash_layout.setAlignment(Qt.AlignCenter)

    pulse_icon = PulseIcon(LOGO_PATH)
    splash_layout.addWidget(pulse_icon, 0, Qt.AlignCenter)

    label_title = QLabel("BGA CURVE MAPPER")
    label_title.setStyleSheet(f"color: {COLORS['ACCENT']}; font-size: 42px; font-weight: bold; font-family: 'Segoe UI', sans-serif; letter-spacing: 4px;")
    label_title.setAlignment(Qt.AlignCenter)
    splash_layout.addWidget(label_title)

    progress_container = QWidget()
    progress_container.setFixedWidth(400)
    progress_layout = QVBoxLayout(progress_container)
    progress = QProgressBar()
    progress.setStyleSheet(f"""
        QProgressBar {{ border: 1px solid #222; background-color: #111; height: 6px; border-radius: 3px; }}
        QProgressBar::chunk {{ background-color: {COLORS['ACCENT']}; border-radius: 3px; }}
    """)
    progress.setRange(0, 100)
    progress.setFormat("")
    progress_layout.addWidget(progress)
    splash_layout.addWidget(progress_container, 0, Qt.AlignCenter)

    label_status = QLabel("CARREGANDO INTERFACE...")
    label_status.setStyleSheet("color: #555; font-size: 10px; font-family: monospace;")
    label_status.setAlignment(Qt.AlignCenter)
    splash_layout.addWidget(label_status)

    splash.showFullScreen()
    pulse_icon.anim_flash.start()
    app.processEvents()

    steps = [
        (20, "Varrendo diretórios de sistema..."),
        (50, "Indexando mapeamentos BGA..."),
        (80, "Sincronizando banco de dados local..."),
        (100, "Inicialização completa."),
    ]

    for valor, texto in steps:
        progress.setValue(valor)
        label_status.setText(texto.upper())
        app.processEvents()
        time.sleep(0.5)

    return splash
