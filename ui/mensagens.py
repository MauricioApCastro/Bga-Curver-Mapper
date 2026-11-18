from PyQt5.QtWidgets import QMessageBox

from utils.styles import COLORS


def _estilo():
    return f"""
        QMessageBox {{ background: {COLORS['CARD']}; }}
        QMessageBox QLabel {{ color: {COLORS['TEXT']}; font-size: 12px; }}
        QMessageBox QPushButton {{
            background: #252525; color: #EEE; border: 1px solid #333;
            padding: 6px 16px; border-radius: 3px; font-size: 11px;
            min-width: 70px;
        }}
        QMessageBox QPushButton:hover {{ background: #353535; border-color: #555; }}
        """


def mostrar(parent, titulo, texto, icone=QMessageBox.Information):
    caixa = QMessageBox(parent)
    caixa.setWindowTitle(titulo)
    caixa.setText(texto)
    caixa.setIcon(icone)
    caixa.setStyleSheet(_estilo())
    caixa.exec_()


def perguntar(parent, titulo, texto, botoes, padrao=None):
    """Mostra uma pergunta com botoes em portugues.

    `botoes` e uma lista de (rotulo, papel); devolve o rotulo escolhido ou None
    se a caixa for fechada sem escolha.
    """
    caixa = QMessageBox(parent)
    caixa.setWindowTitle(titulo)
    caixa.setText(texto)
    caixa.setIcon(QMessageBox.Question)
    caixa.setStyleSheet(_estilo())
    criados = {}
    for rotulo, papel in botoes:
        criados[caixa.addButton(rotulo, papel)] = rotulo
    if padrao is not None:
        for botao, rotulo in criados.items():
            if rotulo == padrao:
                caixa.setDefaultButton(botao)
    caixa.exec_()
    return criados.get(caixa.clickedButton())
