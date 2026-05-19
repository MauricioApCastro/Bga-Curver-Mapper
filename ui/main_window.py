import os

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from services.excel_service import importar_excel
from services.file_service import garantir_pastas, listar_arquivos
from services.json_service import carregar_json, salvar_json
from ui.widgets import BGAPad
from utils.bga_utils import (
    BANCO_PADRAO,
    checar_area_vazia,
    criar_info_pad,
    listar_sinais,
    normalizar_banco,
)
from utils.config import DATA_DIR, DEFAULT_DATABASE, EXCEL_DIR, ICON_PATH
from utils.styles import BTN_STYLE, COLORS, COMBO_STYLE


class BGAVisualizer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("BGA ANALYZER PRO")
        self.setWindowIcon(QIcon(ICON_PATH))
        self.pasta_db, self.pasta_excel = DATA_DIR, EXCEL_DIR
        garantir_pastas(self.pasta_db, self.pasta_excel)

        self.arquivo_atual = os.path.join(self.pasta_db, DEFAULT_DATABASE)
        self.pad_selecionado = None
        self.pads_objetos = {}
        self.view_bottom = False
        self.modo_vazio = False
        self.ponto_clicado_1 = None

        self.dados = self.carregar_banco()
        self.init_ui()
        self.atualizar_grid()
        self.atualizar_listas()

    def carregar_banco(self, caminho=None):
        alvo = caminho or self.arquivo_atual
        return normalizar_banco(carregar_json(alvo, BANCO_PADRAO.copy()))

    def create_card(self, title):
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

    def init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(10, 10, 10, 10)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll.setStyleSheet("border: none; background: #000;")
        self.grid_widget = QWidget()
        self.grid_layout = QGridLayout(self.grid_widget)
        self.scroll.setWidget(self.grid_widget)
        main_layout.addWidget(self.scroll, 4)

        side = QVBoxLayout()
        side.setSpacing(12)

        c_arq, l_arq = self.create_card("PROJETOS & IMPORTAÇÃO")
        self.combo_json = QComboBox()
        self.combo_json.setStyleSheet(COMBO_STYLE)
        btn_abrir = QPushButton("CARREGAR JSON")
        btn_abrir.setStyleSheet(BTN_STYLE)
        btn_abrir.clicked.connect(self.abrir_projeto_json)
        self.combo_excel = QComboBox()
        self.combo_excel.setStyleSheet(COMBO_STYLE)
        btn_import = QPushButton("IMPORTAR EXCEL")
        btn_import.setStyleSheet("QPushButton { background: #301934; color: #DDA0DD; border: 1px solid #4B0082; padding: 6px; border-radius: 3px; } QPushButton:hover { background: #4B0082; }")
        btn_import.clicked.connect(self.executar_mapeamento_completo)
        for widget in [self.combo_json, btn_abrir, self.combo_excel, btn_import]:
            l_arq.addWidget(widget)
        side.addWidget(c_arq)

        c_bus, l_bus = self.create_card("FILTRAGEM DE BARRAMENTO")
        self.edit_busca = QLineEdit()
        self.edit_busca.setPlaceholderText("Filtrar sinais...")
        self.edit_busca.setStyleSheet("background: #000; color: #00FF41; border: 1px solid #333; padding: 6px; font-family: monospace;")
        self.edit_busca.textChanged.connect(self.filtrar_lista)
        self.lista_sinais = QListWidget()
        self.lista_sinais.setFixedHeight(140)
        self.lista_sinais.setStyleSheet("background: #0A0A0A; color: #ACC; border: none; font-size: 11px;")
        self.lista_sinais.itemClicked.connect(self.destacar_sinal_lista)
        l_bus.addWidget(self.edit_busca)
        l_bus.addWidget(self.lista_sinais)
        side.addWidget(c_bus)

        c_edit, l_edit = self.create_card("PROPRIEDADES DO PAD")
        self.label_pad = QLabel("ID: --")
        self.label_pad.setStyleSheet(f"color: {COLORS['TEXT']}; font-family: monospace; font-size: 16px; font-weight: bold;")
        self.edit_sinal = QTextEdit()
        self.edit_sinal.setFixedHeight(120)
        self.edit_sinal.setStyleSheet(f"font-size: 13px; color: {COLORS['ACCENT']}; background: #000; border: 1px solid #222; font-family: 'Consolas', monospace; padding: 5px;")
        l_edit.addWidget(self.label_pad)
        l_edit.addWidget(self.edit_sinal)
        side.addWidget(c_edit)

        c_utl, l_utl = self.create_card("VISTA DO COMPONENTE")
        self.chk_view = QCheckBox("MODO TOP VIEW")
        self.chk_view.setStyleSheet("color: #888; font-size: 10px; font-weight: bold;")
        self.chk_view.toggled.connect(self.trocar_vista)
        self.btn_vazio = QPushButton("ISOLAR ÁREA VAZIA")
        self.btn_vazio.setCheckable(True)
        self.btn_vazio.setStyleSheet(BTN_STYLE)
        self.btn_vazio.clicked.connect(self.toggle_modo_vazio)
        l_utl.addWidget(self.chk_view)
        l_utl.addWidget(self.btn_vazio)
        side.addWidget(c_utl)

        self.btn_salvar = QPushButton("SINCRONIZAR BANCO")
        self.btn_salvar.setFixedHeight(45)
        self.btn_salvar.setStyleSheet(f"QPushButton {{ background: #004488; color: white; font-weight: bold; border-radius: 4px; font-size: 11px; }} QPushButton:hover {{ background: #0055AA; }}")
        self.btn_salvar.clicked.connect(self.salvar_anotacao)
        side.addWidget(self.btn_salvar)
        side.addStretch()
        main_layout.addLayout(side, 1)
        self.setStyleSheet(f"background: {COLORS['BG']};")

    def ao_clicar_pad(self):
        pad = self.sender()
        if self.modo_vazio:
            if not self.ponto_clicado_1:
                self.ponto_clicado_1 = pad.coord
                self.btn_vazio.setText("SELECIONE O FIM")
            else:
                self.dados["chip_config"].setdefault("vazio", [])
                self.dados["chip_config"]["vazio"].append({"p1": self.ponto_clicado_1, "p2": pad.coord})
                self.ponto_clicado_1 = None
                self.btn_vazio.setText("ÁREA OK! PRÓXIMA?")
                self.atualizar_grid()
            return

        if self.pad_selecionado:
            self.pad_selecionado.atualizar_estilo(selecionado=False)
        for pad_obj in self.pads_objetos.values():
            if pad_obj.destacado:
                pad_obj.destacado = False
                pad_obj.atualizar_estilo(selecionado=False)

        self.lista_sinais.clearSelection()
        self.pad_selecionado = pad
        self.pad_selecionado.atualizar_estilo(selecionado=True)
        self.label_pad.setText(f"ID: {pad.coord}")
        self.edit_sinal.setText(pad.info.get("detalhes", pad.info.get("sinal", "NC")))

    def destacar_sinal_lista(self, item):
        nome_sinal = item.text()
        primeiro_foco = None
        if self.pad_selecionado:
            self.pad_selecionado.atualizar_estilo(selecionado=False)
        for pad in self.pads_objetos.values():
            pad.destacado = pad.info.get("sinal") == nome_sinal
            if pad.destacado and not primeiro_foco:
                primeiro_foco = pad
            pad.atualizar_estilo(selecionado=False)
        if primeiro_foco:
            self.pad_selecionado = primeiro_foco
            self.pad_selecionado.atualizar_estilo(selecionado=True)
            self.label_pad.setText(f"ID: {self.pad_selecionado.coord}")
            self.edit_sinal.setText(self.pad_selecionado.info.get("detalhes", "NC"))
            self.scroll.ensureWidgetVisible(self.pad_selecionado)

    def toggle_modo_vazio(self):
        self.modo_vazio = self.btn_vazio.isChecked()
        if not self.modo_vazio:
            self.btn_vazio.setText("ISOLAR ÁREA VAZIA")
            salvar_json(self.arquivo_atual, self.dados)
            self.atualizar_grid()
        else:
            self.ponto_clicado_1 = None
            self.btn_vazio.setText("SELECIONE O INÍCIO")

    def atualizar_grid(self):
        for i in reversed(range(self.grid_layout.count())):
            item = self.grid_layout.itemAt(i)
            if item and item.widget():
                if isinstance(item.widget(), BGAPad):
                    item.widget().anim_piscar.stop()
                item.widget().deleteLater()

        self.pads_objetos = {}
        config = self.dados["chip_config"]
        letras = config.get("letras", [])
        colunas = list(range(1, config.get("colunas", 26) + 1))
        if self.view_bottom:
            colunas.reverse()

        lista_vazios = config.get("vazio", [])
        if isinstance(lista_vazios, dict):
            lista_vazios = [lista_vazios]

        for r, letra in enumerate(letras):
            for vc, rc in enumerate(colunas):
                coord = f"{letra}{rc}"
                pad = BGAPad(coord, self.dados["pinagem"].get(coord))
                if lista_vazios and checar_area_vazia(coord, lista_vazios, letras):
                    pad.visivel = False
                    pad.atualizar_estilo()
                pad.clicked.connect(self.ao_clicar_pad)
                self.grid_layout.addWidget(pad, r, vc)
                self.pads_objetos[coord] = pad
        self.atualizar_lista_sinais()

    def salvar_anotacao(self):
        if not self.pad_selecionado:
            return
        conteudo = self.edit_sinal.toPlainText().strip()
        self.dados["pinagem"][self.pad_selecionado.coord] = criar_info_pad(conteudo)
        salvar_json(self.arquivo_atual, self.dados)
        self.pad_selecionado.info = self.dados["pinagem"][self.pad_selecionado.coord]
        self.pad_selecionado.atualizar_estilo(selecionado=True)
        self.atualizar_lista_sinais()

    def abrir_projeto_json(self):
        nome = self.combo_json.currentText()
        if "Nenhum" in nome:
            return
        self.arquivo_atual = os.path.join(self.pasta_db, nome)
        self.dados = self.carregar_banco(self.arquivo_atual)
        self.atualizar_grid()

    def filtrar_lista(self, texto):
        for i in range(self.lista_sinais.count()):
            item = self.lista_sinais.item(i)
            item.setHidden(texto.upper() not in item.text().upper())

    def atualizar_lista_sinais(self):
        self.lista_sinais.clear()
        self.lista_sinais.addItems(listar_sinais(self.dados))

    def executar_mapeamento_completo(self):
        nome = self.combo_excel.currentText()
        if "Nenhum" in nome:
            return
        try:
            caminho = os.path.join(self.pasta_excel, nome)
            self.arquivo_atual = os.path.join(self.pasta_db, nome.lower().replace(".xlsm", ".json"))
            self.dados = importar_excel(caminho)
            salvar_json(self.arquivo_atual, self.dados)
            self.atualizar_grid()
            self.atualizar_listas()
        except Exception as erro:
            QMessageBox.critical(self, "Erro", str(erro))

    def atualizar_listas(self):
        self.combo_json.clear()
        self.combo_excel.clear()
        jsons = listar_arquivos(self.pasta_db, ".json")
        self.combo_json.addItems(jsons) if jsons else self.combo_json.addItem("Nenhum JSON")
        excels = listar_arquivos(self.pasta_excel, ".xlsm")
        self.combo_excel.addItems(excels) if excels else self.combo_excel.addItem("Nenhum Excel")

    def trocar_vista(self, checked):
        self.view_bottom = checked
        self.chk_view.setText("MODO BOTTOM VIEW" if checked else "MODO TOP VIEW")
        self.atualizar_grid()
