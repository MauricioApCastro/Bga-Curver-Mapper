from PyQt5.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFrame,
    QLabel,
    QLineEdit,
    QListWidget,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
)

from utils.styles import BTN_STYLE, COLORS, COMBO_STYLE


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


def criar_painel_lateral(janela):
    side = QVBoxLayout()
    side.setSpacing(12)

    c_arq, l_arq = criar_card("PROJETOS & IMPORTAÇÃO")
    janela.combo_json = QComboBox()
    janela.combo_json.setStyleSheet(COMBO_STYLE)
    btn_abrir = QPushButton("CARREGAR JSON")
    btn_abrir.setStyleSheet(BTN_STYLE)
    btn_abrir.clicked.connect(janela.abrir_projeto_json)
    janela.combo_excel = QComboBox()
    janela.combo_excel.setStyleSheet(COMBO_STYLE)
    btn_import = QPushButton("IMPORTAR EXCEL")
    btn_import.setStyleSheet("QPushButton { background: #301934; color: #DDA0DD; border: 1px solid #4B0082; padding: 6px; border-radius: 3px; } QPushButton:hover { background: #4B0082; }")
    btn_import.clicked.connect(janela.executar_mapeamento_completo)
    for widget in [janela.combo_json, btn_abrir, janela.combo_excel, btn_import]:
        l_arq.addWidget(widget)
    side.addWidget(c_arq)

    c_bus, l_bus = criar_card("FILTRAGEM DE BARRAMENTO")
    janela.edit_busca = QLineEdit()
    janela.edit_busca.setPlaceholderText("Filtrar sinais...")
    janela.edit_busca.setStyleSheet("background: #000; color: #00FF41; border: 1px solid #333; padding: 6px; font-family: monospace;")
    janela.edit_busca.textChanged.connect(janela.filtrar_lista)
    janela.lista_sinais = QListWidget()
    janela.lista_sinais.setFixedHeight(140)
    janela.lista_sinais.setStyleSheet("background: #0A0A0A; color: #ACC; border: none; font-size: 11px;")
    janela.lista_sinais.itemClicked.connect(janela.destacar_sinal_lista)
    l_bus.addWidget(janela.edit_busca)
    l_bus.addWidget(janela.lista_sinais)
    side.addWidget(c_bus)

    c_edit, l_edit = criar_card("PROPRIEDADES DO PAD")
    janela.label_pad = QLabel("ID: --")
    janela.label_pad.setStyleSheet(f"color: {COLORS['TEXT']}; font-family: monospace; font-size: 16px; font-weight: bold;")
    janela.edit_sinal = QTextEdit()
    janela.edit_sinal.setFixedHeight(120)
    janela.edit_sinal.setStyleSheet(f"font-size: 13px; color: {COLORS['ACCENT']}; background: #000; border: 1px solid #222; font-family: 'Consolas', monospace; padding: 5px;")
    l_edit.addWidget(janela.label_pad)
    l_edit.addWidget(janela.edit_sinal)
    side.addWidget(c_edit)

    c_utl, l_utl = criar_card("VISTA DO COMPONENTE")
    janela.chk_view = QCheckBox("MODO TOP VIEW")
    janela.chk_view.setStyleSheet("color: #888; font-size: 10px; font-weight: bold;")
    janela.chk_view.toggled.connect(janela.trocar_vista)
    janela.btn_vazio = QPushButton("ISOLAR ÁREA VAZIA")
    janela.btn_vazio.setCheckable(True)
    janela.btn_vazio.setStyleSheet(BTN_STYLE)
    janela.btn_vazio.clicked.connect(janela.toggle_modo_vazio)
    l_utl.addWidget(janela.chk_view)
    l_utl.addWidget(janela.btn_vazio)
    side.addWidget(c_utl)

    janela.btn_salvar = QPushButton("SINCRONIZAR BANCO")
    janela.btn_salvar.setFixedHeight(45)
    janela.btn_salvar.setStyleSheet(f"QPushButton {{ background: #004488; color: white; font-weight: bold; border-radius: 4px; font-size: 11px; }} QPushButton:hover {{ background: #0055AA; }}")
    janela.btn_salvar.clicked.connect(janela.salvar_anotacao)
    side.addWidget(janela.btn_salvar)
    side.addStretch()
    return side

