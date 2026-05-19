from PyQt5.QtCore import QEasingCurve, QPropertyAnimation, QSize, Qt
from PyQt5.QtGui import QPainter, QPixmap
from PyQt5.QtWidgets import QGraphicsOpacityEffect, QPushButton, QWidget

from utils.styles import COLORS


class BGAPad(QPushButton):
    def __init__(self, coord, info=None):
        super().__init__(coord)
        self.coord = coord
        self.info = info or {"sinal": "NC", "tipo": "DEFAULT", "detalhes": "NC"}
        self.setFixedSize(28, 28)
        self.visivel = True
        self.destacado = False

        self.efeito_opacidade = QGraphicsOpacityEffect(self)
        self.efeito_opacidade.setOpacity(1.0)
        self.setGraphicsEffect(self.efeito_opacidade)

        self.anim_piscar = QPropertyAnimation(self.efeito_opacidade, b"opacity")
        self.anim_piscar.setDuration(600)
        self.anim_piscar.setStartValue(1.0)
        self.anim_piscar.setEndValue(0.15)
        self.anim_piscar.setEasingCurve(QEasingCurve.InOutSine)
        self.anim_piscar.setLoopCount(-1)

        self.atualizar_estilo()

    def atualizar_estilo(self, selecionado=False):
        if not self:
            return
        try:
            if not self.visivel:
                self.setStyleSheet("background: transparent; border: none;")
                self.setEnabled(False)
                self.setText("")
                self.anim_piscar.stop()
                return

            cor_base = COLORS.get(self.info.get("tipo", "DEFAULT"), COLORS["DEFAULT"])

            if selecionado:
                border = f"3px solid {COLORS['ACCENT']}"
                if self.anim_piscar.state() != QPropertyAnimation.Running:
                    self.anim_piscar.start()
            else:
                if self.anim_piscar.state() == QPropertyAnimation.Running:
                    self.anim_piscar.stop()
                self.efeito_opacidade.setOpacity(1.0)
                border = f"3px solid {COLORS['HIGHLIGHT']}" if self.destacado else "1px solid #333"

            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: {cor_base}; color: white;
                    border: {border}; border-radius: 14px;
                    font-size: 7px; font-weight: bold;
                }}
                QPushButton:hover {{ background-color: white; color: black; border: 2px solid {COLORS['ACCENT']}; }}
            """)
        except RuntimeError:
            pass


class PulseIcon(QWidget):
    def __init__(self, pixmap_path, parent=None):
        super().__init__(parent)
        self.pixmap = QPixmap(pixmap_path)
        if self.pixmap.isNull():
            self.pixmap = QPixmap(200, 200)
            self.pixmap.fill(Qt.transparent)

        self.pixmap = self.pixmap.scaled(300, 300, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.setFixedSize(QSize(320, 320))

        self.efeito_opacidade = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.efeito_opacidade)

        self.anim_flash = QPropertyAnimation(self.efeito_opacidade, b"opacity")
        self.anim_flash.setDuration(1200)
        self.anim_flash.setStartValue(1.0)
        self.anim_flash.setEndValue(0.4)
        self.anim_flash.setEasingCurve(QEasingCurve.InOutQuad)
        self.anim_flash.setLoopCount(-1)

    def paintEvent(self, event):
        painter = QPainter(self)
        pos_x = (self.width() - self.pixmap.width()) // 2
        pos_y = (self.height() - self.pixmap.height()) // 2
        painter.drawPixmap(pos_x, pos_y, self.pixmap)
