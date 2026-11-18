import time

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QFrame,
    QGraphicsDropShadowEffect,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QSplashScreen,
    QVBoxLayout,
    QWidget,
)

from utils.styles import COLORS


def mostrar_splash(app):
    splash = QSplashScreen()
    splash.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
    splash.setStyleSheet("""
        QSplashScreen {
            background: qradialgradient(
                cx: 0.5, cy: 0.36, radius: 1.0,
                fx: 0.5, fy: 0.28,
                stop: 0 #173126,
                stop: 0.36 #09100E,
                stop: 1 #020303
            );
        }
    """)

    screen_geometry = app.desktop().screenGeometry()
    splash.setFixedSize(screen_geometry.width(), screen_geometry.height())

    splash_layout = QVBoxLayout(splash)
    splash_layout.setAlignment(Qt.AlignCenter)
    splash_layout.setContentsMargins(48, 48, 48, 48)

    panel = QFrame()
    panel.setObjectName("splashPanel")
    panel_width = max(760, screen_geometry.width() - 96)
    panel_height = max(460, screen_geometry.height() - 96)
    panel.setFixedSize(panel_width, panel_height)
    panel.setStyleSheet("""
        QFrame#splashPanel {
            background: rgba(8, 12, 11, 232);
            border: 1px solid rgba(0, 255, 65, 92);
            border-radius: 8px;
        }
    """)
    shadow = QGraphicsDropShadowEffect(panel)
    shadow.setBlurRadius(54)
    shadow.setColor(Qt.black)
    shadow.setOffset(0, 22)
    panel.setGraphicsEffect(shadow)

    panel_layout = QHBoxLayout(panel)
    panel_layout.setContentsMargins(82, 72, 82, 70)
    panel_layout.setSpacing(0)

    content = QWidget()
    content_layout = QVBoxLayout(content)
    content_layout.setContentsMargins(0, 2, 0, 0)
    content_layout.setSpacing(18)
    content_layout.setAlignment(Qt.AlignVCenter)

    label_kicker = QLabel("INICIALIZANDO AMBIENTE")
    label_kicker.setStyleSheet("""
        color: #7FAE98;
        font-size: 13px;
        font-weight: 600;
        font-family: 'Segoe UI', sans-serif;
    """)
    label_kicker.setAlignment(Qt.AlignLeft)
    content_layout.addWidget(label_kicker)

    label_title = QLabel("BGA Mapper")
    label_title.setStyleSheet(f"""
        color: {COLORS['ACCENT']};
        font-size: 72px;
        font-weight: 700;
        font-family: 'Segoe UI', sans-serif;
    """)
    label_title.setAlignment(Qt.AlignLeft)
    content_layout.addWidget(label_title)

    label_subtitle = QLabel("Mapeamento visual de componentes BGA com leitura local de planilhas e projetos.")
    label_subtitle.setWordWrap(True)
    label_subtitle.setStyleSheet("""
        color: #BBD1C7;
        font-size: 20px;
        font-family: 'Segoe UI', sans-serif;
    """)
    label_subtitle.setAlignment(Qt.AlignLeft)
    content_layout.addWidget(label_subtitle)

    status_box = QFrame()
    status_box.setObjectName("statusBox")
    status_box.setStyleSheet("""
        QFrame#statusBox {
            background: rgba(3, 6, 5, 176);
            border: 1px solid rgba(112, 151, 132, 64);
            border-radius: 6px;
        }
    """)
    status_layout = QVBoxLayout(status_box)
    status_layout.setContentsMargins(24, 22, 24, 22)
    status_layout.setSpacing(12)

    status_header = QLabel("STATUS")
    status_header.setStyleSheet("color: #5F7D70; font-size: 15px; font-family: 'Consolas', monospace;")
    status_layout.addWidget(status_header)

    label_status = QLabel("Preparando interface...")
    label_status.setStyleSheet("color: #D7E8DF; font-size: 18px; font-family: 'Segoe UI', sans-serif;")
    status_layout.addWidget(label_status)

    progress_container = QWidget()
    progress_layout = QVBoxLayout(progress_container)
    progress_layout.setContentsMargins(0, 10, 0, 0)
    progress_layout.setSpacing(8)

    progress_meta = QHBoxLayout()
    progress_meta.setContentsMargins(0, 0, 0, 0)
    label_progress = QLabel("0%")
    label_progress.setStyleSheet(f"color: {COLORS['ACCENT']}; font-size: 15px; font-family: 'Consolas', monospace;")
    label_progress.setAlignment(Qt.AlignRight)
    progress_meta.addStretch()
    progress_meta.addWidget(label_progress)
    progress_layout.addLayout(progress_meta)

    progress = QProgressBar()
    progress.setStyleSheet(f"""
        QProgressBar {{
            border: 1px solid #243A30;
            background-color: #030504;
            min-height: 16px;
            max-height: 16px;
            border-radius: 6px;
        }}
        QProgressBar::chunk {{
            background: qlineargradient(
                x1: 0, y1: 0, x2: 1, y2: 0,
                stop: 0 #00A2FF,
                stop: 0.5 {COLORS['ACCENT']},
                stop: 1 #D7FF5F
            );
            border-radius: 6px;
        }}
    """)
    progress.setRange(0, 100)
    progress.setFormat("")
    progress_layout.addWidget(progress)
    status_layout.addWidget(progress_container)
    content_layout.addWidget(status_box)

    label_footer = QLabel("Banco local | Excel | Visualizador BGA")
    label_footer.setStyleSheet("color: #668478; font-size: 13px; font-family: 'Consolas', monospace;")
    label_footer.setAlignment(Qt.AlignLeft)
    content_layout.addWidget(label_footer)

    panel_layout.addWidget(content, 1, Qt.AlignVCenter)
    splash_layout.addWidget(panel, 0, Qt.AlignCenter)

    splash.showFullScreen()
    app.processEvents()

    steps = [
        (20, "Preparando pastas de trabalho..."),
        (50, "Indexando mapeamentos BGA..."),
        (80, "Sincronizando banco de dados local..."),
        (100, "Inicialização completa."),
    ]

    for valor, texto in steps:
        progress.setValue(valor)
        label_progress.setText(f"{valor}%")
        label_status.setText(texto)
        app.processEvents()
        time.sleep(0.42)

    return splash
