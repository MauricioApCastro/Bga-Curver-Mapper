from PyQt5.QtCore import QEasingCurve, QPropertyAnimation, QSize, Qt
from PyQt5.QtGui import QColor, QPainter, QPen, QPixmap
from PyQt5.QtWidgets import QGraphicsOpacityEffect, QWidget


class PulseIcon(QWidget):
    def __init__(self, pixmap_path, parent=None):
        super().__init__(parent)
        self.pixmap = QPixmap(pixmap_path)
        if self.pixmap.isNull():
            self.pixmap = QPixmap(220, 220)
            self.pixmap.fill(Qt.transparent)

        self.pixmap = self.pixmap.scaled(260, 260, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.setFixedSize(QSize(320, 300))

        self.efeito_opacidade = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.efeito_opacidade)

        self.anim_flash = QPropertyAnimation(self.efeito_opacidade, b"opacity")
        self.anim_flash.setDuration(1400)
        self.anim_flash.setStartValue(1.0)
        self.anim_flash.setEndValue(0.62)
        self.anim_flash.setEasingCurve(QEasingCurve.InOutQuad)
        self.anim_flash.setLoopCount(-1)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)

        center_x = self.width() // 2
        center_y = self.height() // 2
        glow_color = QColor(0, 255, 65)

        for radius, alpha, width in ((132, 28, 2), (112, 44, 2), (92, 62, 1)):
            pen = QPen(glow_color)
            pen.setWidth(width)
            glow_color.setAlpha(alpha)
            pen.setColor(glow_color)
            painter.setPen(pen)
            painter.drawEllipse(center_x - radius, center_y - radius, radius * 2, radius * 2)

        pos_x = (self.width() - self.pixmap.width()) // 2
        pos_y = (self.height() - self.pixmap.height()) // 2
        painter.drawPixmap(pos_x, pos_y, self.pixmap)
