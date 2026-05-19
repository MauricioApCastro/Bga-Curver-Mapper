from PyQt5.QtCore import QEasingCurve, QPropertyAnimation, QSize, Qt
from PyQt5.QtGui import QPainter, QPixmap
from PyQt5.QtWidgets import QGraphicsOpacityEffect, QWidget


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

