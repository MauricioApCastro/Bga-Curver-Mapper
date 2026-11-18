import os
import platform
import sys
import webbrowser
from urllib.parse import quote

from PyQt5.QtCore import QT_VERSION_STR, Qt
from PyQt5.QtGui import QFont, QGuiApplication
from PyQt5.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QPlainTextEdit,
    QPushButton,
    QVBoxLayout,
)

from ui.mensagens import mostrar
from utils.config import (
    APP_NAME,
    APP_VERSION,
    BASE_DIR,
    LOG_FILE,
    SUPPORT_EMAIL,
    USER_FILES_DIR,
)
from utils.styles import BTN_STYLE, COLORS

GUIA_PATH = os.path.join(BASE_DIR, "docs", "GUIA_USUARIO.txt")
TERMOS_PATH = os.path.join(BASE_DIR, "docs", "TERMOS_USO.txt")
PRIVACIDADE_PATH = os.path.join(BASE_DIR, "docs", "PRIVACIDADE.txt")

ESTILO_DIALOGO = (
    f"QDialog {{ background: {COLORS['BG']}; }}"
    f"QLabel {{ color: {COLORS['TEXT']}; font-size: 12px; }}"
)


def _ler_texto(caminho):
    for codificacao in ("utf-8-sig", "cp1252"):
        try:
            with open(caminho, "r", encoding=codificacao) as arquivo:
                return arquivo.read()
        except UnicodeDecodeError:
            continue
        except OSError:
            return None
    return None


def _abrir_caminho(parent, caminho):
    try:
        if sys.platform == "win32":
            os.startfile(caminho)
        else:
            webbrowser.open("file://" + quote(caminho))
    except OSError as erro:
        mostrar(parent, "Nao foi possivel abrir", str(erro))


def informacoes_sistema():
    linhas = [
        f"{APP_NAME} {APP_VERSION}",
        f"Windows/OS: {platform.platform()}",
        f"Python: {platform.python_version()} | Qt: {QT_VERSION_STR}",
        f"Pasta de arquivos: {USER_FILES_DIR}",
        f"Log: {LOG_FILE}",
    ]
    return "\n".join(linhas)


class _DialogoBase(QDialog):
    def __init__(self, parent, titulo, largura=640):
        super().__init__(parent)
        self.setWindowTitle(titulo)
        self.setMinimumWidth(largura)
        self.setStyleSheet(ESTILO_DIALOGO)
        self.layout_principal = QVBoxLayout(self)
        self.layout_principal.setContentsMargins(20, 18, 20, 16)
        self.layout_principal.setSpacing(12)

    def titulo(self, texto):
        rotulo = QLabel(texto)
        rotulo.setStyleSheet(f"color: {COLORS['ACCENT']}; font-size: 17px; font-weight: bold;")
        self.layout_principal.addWidget(rotulo)

    def botao(self, texto, acao):
        botao = QPushButton(texto)
        botao.setStyleSheet(BTN_STYLE)
        botao.setMinimumHeight(32)
        botao.clicked.connect(acao)
        return botao


def mostrar_texto(parent, titulo, caminho):
    dialogo = _DialogoBase(parent, titulo, 720)
    dialogo.resize(760, 620)
    dialogo.titulo(titulo)
    visor = QPlainTextEdit()
    visor.setReadOnly(True)
    visor.setFont(QFont("Consolas", 10))
    visor.setStyleSheet("background: #0A0A0A; color: #CCC; border: 1px solid #222; padding: 8px;")
    texto = _ler_texto(caminho)
    visor.setPlainText(texto if texto is not None else "Documento nao encontrado.")
    dialogo.layout_principal.addWidget(visor, 1)
    fechar = dialogo.botao("FECHAR", dialogo.accept)
    linha = QHBoxLayout()
    linha.addStretch()
    linha.addWidget(fechar)
    dialogo.layout_principal.addLayout(linha)
    dialogo.exec_()


def mostrar_guia(parent):
    mostrar_texto(parent, "Guia de uso", GUIA_PATH)


def mostrar_termos(parent):
    mostrar_texto(parent, "Termos de uso", TERMOS_PATH)


def mostrar_privacidade(parent):
    mostrar_texto(parent, "Privacidade", PRIVACIDADE_PATH)


def mostrar_suporte(parent):
    dialogo = _DialogoBase(parent, "Suporte", 560)
    dialogo.titulo("Ajuda e suporte")

    intro = QLabel(
        "Precisa de ajuda? Consulte primeiro o Guia de uso (menu Ajuda > Guia de uso, F1).\n"
        "Se o problema continuar, entre em contato e envie as informacoes abaixo."
    )
    intro.setWordWrap(True)
    dialogo.layout_principal.addWidget(intro)

    rotulo_contato = QLabel(f"Contato: {SUPPORT_EMAIL}")
    rotulo_contato.setTextInteractionFlags(Qt.TextSelectableByMouse)
    dialogo.layout_principal.addWidget(rotulo_contato)

    info = QPlainTextEdit(informacoes_sistema())
    info.setReadOnly(True)
    info.setFont(QFont("Consolas", 9))
    info.setFixedHeight(110)
    info.setStyleSheet("background: #000; color: #00FF41; border: 1px solid #333; padding: 6px;")
    dialogo.layout_principal.addWidget(info)

    def copiar():
        QGuiApplication.clipboard().setText(informacoes_sistema())
        mostrar(dialogo, "Suporte", "Informacoes copiadas. Cole na mensagem ao suporte.")

    def abrir_log():
        if os.path.exists(LOG_FILE):
            _abrir_caminho(dialogo, LOG_FILE)
        else:
            mostrar(dialogo, "Suporte", "Nenhum registro de erros foi gerado ainda.")

    def enviar_email():
        assunto = quote(f"Suporte {APP_NAME} {APP_VERSION}")
        corpo = quote(informacoes_sistema())
        webbrowser.open(f"mailto:{SUPPORT_EMAIL}?subject={assunto}&body={corpo}")

    linha1 = QHBoxLayout()
    linha1.addWidget(dialogo.botao("Copiar informacoes", copiar))
    linha1.addWidget(dialogo.botao("Abrir pasta de arquivos", lambda: _abrir_caminho(dialogo, USER_FILES_DIR)))
    dialogo.layout_principal.addLayout(linha1)

    linha2 = QHBoxLayout()
    linha2.addWidget(dialogo.botao("Abrir registro de erros", abrir_log))
    if SUPPORT_EMAIL:
        linha2.addWidget(dialogo.botao("Enviar e-mail", enviar_email))
    dialogo.layout_principal.addLayout(linha2)

    fechar = dialogo.botao("FECHAR", dialogo.accept)
    linha3 = QHBoxLayout()
    linha3.addStretch()
    linha3.addWidget(fechar)
    dialogo.layout_principal.addLayout(linha3)
    dialogo.exec_()


def mostrar_sobre(parent):
    dialogo = _DialogoBase(parent, f"Sobre o {APP_NAME}", 420)
    dialogo.titulo(f"{APP_NAME}")
    versao = QLabel(f"Versao {APP_VERSION}")
    versao.setStyleSheet("color: #888; font-size: 12px;")
    dialogo.layout_principal.addWidget(versao)

    descricao = QLabel(
        "Ferramenta para visualizar, importar e mapear a pinagem de componentes BGA, "
        "com busca de sinais, cores por tipo de pad e selecao em grupo.\n\n"
        f"Contato: {SUPPORT_EMAIL}"
    )
    descricao.setWordWrap(True)
    dialogo.layout_principal.addWidget(descricao)

    linha = QHBoxLayout()
    linha.addWidget(dialogo.botao("Termos de uso", lambda: mostrar_termos(dialogo)))
    linha.addWidget(dialogo.botao("Privacidade", lambda: mostrar_privacidade(dialogo)))
    dialogo.layout_principal.addLayout(linha)

    fechar = dialogo.botao("FECHAR", dialogo.accept)
    linha_fechar = QHBoxLayout()
    linha_fechar.addStretch()
    linha_fechar.addWidget(fechar)
    dialogo.layout_principal.addLayout(linha_fechar)
    dialogo.exec_()
