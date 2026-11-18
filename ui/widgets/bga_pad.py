from PyQt5.QtCore import QEasingCurve, QPropertyAnimation
from PyQt5.QtWidgets import QGraphicsOpacityEffect, QPushButton

from models.pad_model import PadModel, identificar_tipo_sinal
from utils.styles import COLORS


class BGAPad(QPushButton):
    def __init__(self, coord, info=None, tamanho=28):
        super().__init__(coord)
        self.coord = coord
        self.info = info or PadModel().to_dict()
        self.tamanho = tamanho
        self.setFixedSize(tamanho, tamanho)
        self.visivel = True
        self.destacado = False
        self.esmaecido = False
        self.agrupado = False

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

    def aplicar_tamanho(self, tamanho):
        self.tamanho = tamanho
        self.setFixedSize(tamanho, tamanho)
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

            tipo = identificar_tipo_sinal(self.info.get("sinal", ""))
            cor_base = COLORS.get(tipo, COLORS["DEFAULT"])
            espessura = 3 if self.tamanho >= 16 else 1

            if selecionado:
                border = f"{espessura}px solid {COLORS['ACCENT']}"
                if self.anim_piscar.state() != QPropertyAnimation.Running:
                    self.anim_piscar.start()
            else:
                if self.anim_piscar.state() == QPropertyAnimation.Running:
                    self.anim_piscar.stop()
                self.efeito_opacidade.setOpacity(0.18 if self.esmaecido else 1.0)
                if self.agrupado:
                    border = f"{espessura}px solid {COLORS['ACCENT']}"
                elif self.destacado:
                    border = f"{espessura}px solid {COLORS['HIGHLIGHT']}"
                else:
                    border = "1px solid #333"

            raio = max(1, self.tamanho // 2)
            fonte = max(4, min(7, self.tamanho // 4))

            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: {cor_base}; color: white;
                    border: {border}; border-radius: {raio}px;
                    font-size: {fonte}px; font-weight: bold;
                }}
                QPushButton:hover {{ background-color: white; color: black; border: 2px solid {COLORS['ACCENT']}; }}
            """)
        except RuntimeError:
            pass
