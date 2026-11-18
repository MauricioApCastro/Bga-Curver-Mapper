from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QColor, QIcon, QPainter, QPixmap
from PyQt5.QtWidgets import (
    QCheckBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QPushButton,
    QScrollArea,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from utils.styles import BTN_STYLE, COLORS, LEGENDA_TIPOS


def criar_card(title):
    frame = QFrame()
    frame.setStyleSheet(
        f"background: {COLORS['CARD']}; border: 1px solid #2A2A2A; border-radius: 6px;"
    )
    layout = QVBoxLayout(frame)
    layout.setContentsMargins(12, 12, 12, 12)
    layout.setSpacing(8)
    if title:
        label = QLabel(title)
        label.setStyleSheet("color: #555; font-size: 10px; font-weight: bold; letter-spacing: 1px;")
        layout.addWidget(label)
    return frame, layout


def _icone_circulo(cor, tamanho=12):
    pix = QPixmap(tamanho, tamanho)
    pix.fill(Qt.transparent)
    pintor = QPainter(pix)
    pintor.setRenderHint(QPainter.Antialiasing)
    pintor.setBrush(QColor(cor))
    pintor.setPen(Qt.NoPen)
    pintor.drawEllipse(0, 0, tamanho, tamanho)
    pintor.end()
    return QIcon(pix)


def criar_legenda(janela):
    barra = QFrame()
    barra.setStyleSheet("QFrame { background: transparent; border: none; }")
    linha = QHBoxLayout(barra)
    linha.setContentsMargins(0, 4, 0, 0)
    linha.setSpacing(8)
    linha.addStretch()
    janela.botoes_legenda = {}
    for tipo, nome in LEGENDA_TIPOS:
        botao = QPushButton(nome)
        botao.setIcon(_icone_circulo(COLORS[tipo]))
        botao.setIconSize(QSize(12, 12))
        botao.setCheckable(True)
        botao.setCursor(Qt.PointingHandCursor)
        botao.setToolTip(f"Mostrar pads do tipo: {nome}")
        cor = COLORS[tipo]
        botao.setStyleSheet(
            "QPushButton { color: #AAA; font-size: 11px; background: transparent; "
            "border: 1px solid transparent; border-radius: 10px; padding: 2px 8px; }"
            "QPushButton:hover { border-color: #444; }"
            f"QPushButton:checked {{ color: white; background: #1E1E1E; border-color: {cor}; }}"
        )
        botao.clicked.connect(lambda _checked, t=tipo: janela.filtrar_por_tipo(t))
        linha.addWidget(botao)
        janela.botoes_legenda[tipo] = botao
    linha.addStretch()
    barra.setFixedHeight(30)
    return barra


def criar_painel_lateral(janela):
    side = QVBoxLayout()
    side.setSpacing(10)
    side.setContentsMargins(0, 0, 6, 0)

    c_arq, l_arq = criar_card("PROJETOS & IMPORTACAO")
    l_arq.setSpacing(6)

    def rotulo(texto):
        lbl = QLabel(texto)
        lbl.setStyleSheet(
            "color: #777; font-size: 9px; font-weight: bold; border: none; background: transparent;"
        )
        return lbl

    janela.edit_busca_json = QLineEdit()
    janela.edit_busca_json.setPlaceholderText("Digite o codigo do BGA...")
    janela.edit_busca_json.setClearButtonEnabled(True)
    janela.edit_busca_json.setFixedHeight(32)
    janela.edit_busca_json.setStyleSheet(
        "background: #000; color: #00FF41; border: 1px solid #333; padding: 4px 6px; font-family: monospace;"
    )
    janela.edit_busca_json.textChanged.connect(janela.filtrar_json)
    janela.edit_busca_json.returnPressed.connect(janela.abrir_primeiro_json_filtrado)
    janela.lista_json = QListWidget()
    janela.lista_json.setFixedHeight(110)
    janela.lista_json.setStyleSheet(
        "QListWidget { background: #0A0A0A; color: #ACC; border: 1px solid #222; font-size: 11px; }"
        "QListWidget::item { padding: 3px 4px; }"
        "QListWidget::item:selected { background: #004488; color: white; }"
    )
    janela.lista_json.setVisible(False)
    janela.lista_json.itemClicked.connect(lambda _item: janela.abrir_projeto_json())

    janela.edit_busca_excel = QLineEdit()
    janela.edit_busca_excel.setPlaceholderText("Digite o nome da planilha...")
    janela.edit_busca_excel.setClearButtonEnabled(True)
    janela.edit_busca_excel.setFixedHeight(32)
    janela.edit_busca_excel.setStyleSheet(janela.edit_busca_json.styleSheet())
    janela.edit_busca_excel.textChanged.connect(janela.filtrar_excel)
    janela.edit_busca_excel.returnPressed.connect(janela.selecionar_unico_excel_filtrado)
    janela.lista_excel = QListWidget()
    janela.lista_excel.setFixedHeight(110)
    janela.lista_excel.setStyleSheet(janela.lista_json.styleSheet())
    janela.lista_excel.setVisible(False)
    janela.lista_excel.itemClicked.connect(janela.escolher_excel)
    btn_criar_bga = QPushButton("CRIAR BGA VAZIO")
    btn_criar_bga.setStyleSheet(BTN_STYLE)
    btn_criar_bga.setFixedHeight(34)
    btn_criar_bga.clicked.connect(janela.criar_bga_vazio)

    l_arq.addWidget(rotulo("ABRIR PROJETO"))
    l_arq.addWidget(janela.edit_busca_json)
    l_arq.addWidget(janela.lista_json)
    l_arq.addSpacing(10)
    l_arq.addWidget(rotulo("IMPORTAR PLANILHA"))
    l_arq.addWidget(janela.edit_busca_excel)
    l_arq.addWidget(janela.lista_excel)
    l_arq.addSpacing(10)
    l_arq.addWidget(btn_criar_bga)
    side.addWidget(c_arq)

    c_bus, l_bus = criar_card("FILTRAGEM DE SINAIS")
    janela.edit_busca = QLineEdit()
    janela.edit_busca.setPlaceholderText("Filtrar sinais...")
    janela.edit_busca.setStyleSheet(
        "background: #000; color: #00FF41; border: 1px solid #333; padding: 6px; font-family: monospace;"
    )
    janela.edit_busca.textChanged.connect(janela.filtrar_lista)
    janela.lista_sinais = QListWidget()
    janela.lista_sinais.setFixedHeight(110)
    janela.lista_sinais.setStyleSheet(
        "background: #0A0A0A; color: #ACC; border: none; font-size: 11px;"
    )
    janela.lista_sinais.itemClicked.connect(janela.destacar_sinal_lista)
    l_bus.addWidget(janela.edit_busca)
    l_bus.addWidget(janela.lista_sinais)
    side.addWidget(c_bus)

    c_edit, l_edit = criar_card("PROPRIEDADES DO PAD")
    janela.label_pad = QLabel("")
    janela.label_pad.setStyleSheet(
        f"color: {COLORS['TEXT']}; font-family: monospace; font-size: 16px; font-weight: bold;"
    )
    janela.edit_sinal = QTextEdit()
    janela.edit_sinal.setFixedHeight(90)
    janela.edit_sinal.textChanged.connect(janela.ao_editar_sinal)
    janela.edit_sinal.setStyleSheet(
        f"font-size: 13px; color: {COLORS['ACCENT']}; background: #000; border: 1px solid #222; font-family: 'Consolas', monospace; padding: 5px;"
    )
    l_edit.addWidget(janela.label_pad)
    l_edit.addWidget(janela.edit_sinal)
    side.addWidget(c_edit)

    c_utl, l_utl = criar_card("VISTA DO COMPONENTE")
    janela.chk_view = QCheckBox("MODO TOP VIEW")
    janela.chk_view.setStyleSheet("color: #888; font-size: 10px; font-weight: bold;")
    janela.chk_view.toggled.connect(janela.trocar_vista)
    janela.btn_vazio = QPushButton("ISOLAR AREA VAZIA")
    janela.btn_vazio.setCheckable(True)
    janela.btn_vazio.setStyleSheet(BTN_STYLE)
    janela.btn_vazio.clicked.connect(janela.toggle_modo_vazio)
    janela.btn_voltar = QPushButton("VOLTAR")
    janela.btn_voltar.setStyleSheet(BTN_STYLE)
    janela.btn_voltar.setEnabled(False)
    janela.btn_voltar.clicked.connect(janela.voltar_modo_vazio)
    l_utl.addWidget(janela.chk_view)
    l_utl.addWidget(janela.btn_vazio)
    l_utl.addWidget(janela.btn_voltar)
    side.addWidget(c_utl)

    side.addStretch()

    conteudo = QWidget()
    conteudo.setLayout(side)
    conteudo.setStyleSheet("QWidget#conteudo { background: transparent; }")
    conteudo.setObjectName("conteudo")

    rolagem = QScrollArea()
    rolagem.setWidgetResizable(True)
    rolagem.setFrameShape(QFrame.NoFrame)
    rolagem.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
    rolagem.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
    rolagem.setStyleSheet("QScrollArea { border: none; background: transparent; }")
    rolagem.setWidget(conteudo)

    janela.btn_salvar = QPushButton("SALVAR")
    janela.btn_salvar.setFixedHeight(45)
    janela.btn_salvar.clicked.connect(janela.salvar_anotacao)

    container = QWidget()
    externo = QVBoxLayout(container)
    externo.setContentsMargins(0, 0, 0, 0)
    externo.setSpacing(8)
    externo.addWidget(rolagem, 1)
    externo.addWidget(janela.btn_salvar)
    container.setFixedWidth(296)
    return container
