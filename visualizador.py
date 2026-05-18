import sys, json, os, re, time
import pandas as pd
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QGridLayout, 
                             QPushButton, QVBoxLayout, QHBoxLayout, QLabel, 
                             QFrame, QScrollArea, QCheckBox, QTextEdit, QLineEdit, 
                             QListWidget, QMessageBox, QComboBox, QSplashScreen, 
                             QProgressBar, QGraphicsOpacityEffect)
from PyQt5.QtGui import QIcon, QPixmap, QPainter, QImage, QColor
from PyQt5.QtCore import (Qt, QTimer, QSize, QPropertyAnimation, QEasingCurve, 
                          pyqtProperty)

# Configurações de Cores
COLORS = {
    "VCC": "#FF4500", "GND": "#1A237E", "SIGNAL": "#00A2FF",
    "DEFAULT": "#757575", "BG": "#0F0F0F", "CARD": "#1A1A1A",
    "TEXT": "#CCCCCC", "ACCENT": "#00FF41", "HIGHLIGHT": "#FFFF00"
}

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
        if not self: return
        try:
            if not self.visivel:
                self.setStyleSheet("background: transparent; border: none;")
                self.setEnabled(False); self.setText("")
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
                
                if self.destacado: border = f"3px solid {COLORS['HIGHLIGHT']}"
                else: border = "1px solid #333"
            
            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: {cor_base}; color: white;
                    border: {border}; border-radius: 14px;
                    font-size: 7px; font-weight: bold;
                }}
                QPushButton:hover {{ background-color: white; color: black; border: 2px solid {COLORS['ACCENT']}; }}
            """)
        except RuntimeError: pass

class PulseIcon(QWidget):
    def __init__(self, pixmap_path, parent=None):
        super().__init__(parent)
        self.pixmap = QPixmap(pixmap_path)
        if self.pixmap.isNull():
            # Fallback caso a imagem não carregue
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

class BGAVisualizer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("BGA ANALYZER PRO")
        self.setWindowIcon(QIcon('logo.png'))
        self.pasta_db, self.pasta_excel = 'banco_de_dados', 'excels'
        for p in [self.pasta_db, self.pasta_excel]:
            if not os.path.exists(p): os.makedirs(p)
        
        self.arquivo_atual = os.path.join(self.pasta_db, 'database.json')
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
        if os.path.exists(alvo):
            try:
                with open(alvo, 'r', encoding='utf-8') as f: 
                    d = json.load(f)
                    if "vazio" in d["chip_config"] and isinstance(d["chip_config"]["vazio"], dict):
                        d["chip_config"]["vazio"] = [d["chip_config"]["vazio"]]
                    return d
            except: pass
        return {"chip_config": {"colunas": 26, "letras": [], "vazio": []}, "pinagem": {}}

    def create_card(self, title):
        f = QFrame(); f.setStyleSheet(f"background: {COLORS['CARD']}; border: 1px solid #2A2A2A; border-radius: 6px;")
        l = QVBoxLayout(f); l.setContentsMargins(12, 12, 12, 12); l.setSpacing(8)
        if title:
            lbl = QLabel(title); lbl.setStyleSheet("color: #555; font-size: 10px; font-weight: bold; letter-spacing: 1px;")
            l.addWidget(lbl)
        return f, l

    def init_ui(self):
        central = QWidget(); self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(10, 10, 10, 10)

        self.scroll = QScrollArea(); self.scroll.setWidgetResizable(True)
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll.setStyleSheet("border: none; background: #000;")
        self.grid_widget = QWidget(); self.grid_layout = QGridLayout(self.grid_widget)
        self.scroll.setWidget(self.grid_widget)
        main_layout.addWidget(self.scroll, 4)

        side = QVBoxLayout(); side.setSpacing(12)
        BTN_STYLE = "QPushButton { background: #252525; color: #EEE; border: 1px solid #333; padding: 6px; border-radius: 3px; font-size: 11px; } QPushButton:hover { background: #353535; border-color: #555; }"
        COMBO_STYLE = "QComboBox { background: #111; color: #ACC; border: 1px solid #333; padding: 4px; } QComboBox::drop-down { border: none; }"

        c_arq, l_arq = self.create_card("PROJETOS & IMPORTAÇÃO")
        self.combo_json = QComboBox(); self.combo_json.setStyleSheet(COMBO_STYLE)
        btn_abrir = QPushButton("CARREGAR JSON"); btn_abrir.setStyleSheet(BTN_STYLE)
        btn_abrir.clicked.connect(self.abrir_projeto_json)
        self.combo_excel = QComboBox(); self.combo_excel.setStyleSheet(COMBO_STYLE)
        btn_import = QPushButton("IMPORTAR EXCEL"); btn_import.setStyleSheet("QPushButton { background: #301934; color: #DDA0DD; border: 1px solid #4B0082; padding: 6px; border-radius: 3px; } QPushButton:hover { background: #4B0082; }")
        btn_import.clicked.connect(self.executar_mapeamento_completo)
        for w in [self.combo_json, btn_abrir, self.combo_excel, btn_import]: l_arq.addWidget(w)
        side.addWidget(c_arq)

        c_bus, l_bus = self.create_card("FILTRAGEM DE BARRAMENTO")
        self.edit_busca = QLineEdit(); self.edit_busca.setPlaceholderText("Filtrar sinais..."); self.edit_busca.setStyleSheet("background: #000; color: #00FF41; border: 1px solid #333; padding: 6px; font-family: monospace;")
        self.edit_busca.textChanged.connect(self.filtrar_lista)
        self.lista_sinais = QListWidget(); self.lista_sinais.setFixedHeight(140); self.lista_sinais.setStyleSheet("background: #0A0A0A; color: #ACC; border: none; font-size: 11px;")
        self.lista_sinais.itemClicked.connect(self.destacar_sinal_lista)
        l_bus.addWidget(self.edit_busca); l_bus.addWidget(self.lista_sinais)
        side.addWidget(c_bus)

        c_edit, l_edit = self.create_card("PROPRIEDADES DO PAD")
        self.label_pad = QLabel("ID: --"); self.label_pad.setStyleSheet(f"color: {COLORS['TEXT']}; font-family: monospace; font-size: 16px; font-weight: bold;")
        self.edit_sinal = QTextEdit(); self.edit_sinal.setFixedHeight(120)
        self.edit_sinal.setStyleSheet(f"font-size: 13px; color: {COLORS['ACCENT']}; background: #000; border: 1px solid #222; font-family: 'Consolas', monospace; padding: 5px;")
        l_edit.addWidget(self.label_pad); l_edit.addWidget(self.edit_sinal)
        side.addWidget(c_edit)

        c_utl, l_utl = self.create_card("VISTA DO COMPONENTE")
        self.chk_view = QCheckBox("MODO TOP VIEW"); self.chk_view.setStyleSheet("color: #888; font-size: 10px; font-weight: bold;")
        self.chk_view.toggled.connect(self.trocar_vista)
        self.btn_vazio = QPushButton("ISOLAR ÁREA VAZIA"); self.btn_vazio.setCheckable(True); self.btn_vazio.setStyleSheet(BTN_STYLE)
        self.btn_vazio.clicked.connect(self.toggle_modo_vazio)
        l_utl.addWidget(self.chk_view); l_utl.addWidget(self.btn_vazio)
        side.addWidget(c_utl)

        self.btn_salvar = QPushButton("💾 SINCRONIZAR BANCO"); self.btn_salvar.setFixedHeight(45)
        self.btn_salvar.setStyleSheet(f"QPushButton {{ background: #004488; color: white; font-weight: bold; border-radius: 4px; font-size: 11px; }} QPushButton:hover {{ background: #0055AA; }}")
        self.btn_salvar.clicked.connect(self.salvar_anotacao)
        side.addWidget(self.btn_salvar); side.addStretch()
        main_layout.addLayout(side, 1)
        self.setStyleSheet(f"background: {COLORS['BG']};")

    def ao_clicar_pad(self):
        pad = self.sender()
        if self.modo_vazio:
            if not self.ponto_clicado_1: 
                self.ponto_clicado_1 = pad.coord
                self.btn_vazio.setText("➜ SELECIONE O FIM")
            else:
                if "vazio" not in self.dados["chip_config"]: self.dados["chip_config"]["vazio"] = []
                self.dados["chip_config"]["vazio"].append({"p1": self.ponto_clicado_1, "p2": pad.coord})
                self.ponto_clicado_1 = None
                self.btn_vazio.setText("➜ ÁREA OK! PRÓXIMA?")
                self.atualizar_grid()
            return
        
        if self.pad_selecionado: self.pad_selecionado.atualizar_estilo(selecionado=False)
        for p in self.pads_objetos.values():
            if p.destacado: p.destacado = False; p.atualizar_estilo(selecionado=False)
        
        self.lista_sinais.clearSelection()
        self.pad_selecionado = pad
        self.pad_selecionado.atualizar_estilo(selecionado=True)
        self.label_pad.setText(f"ID: {pad.coord}")
        self.edit_sinal.setText(pad.info.get("detalhes", pad.info.get("sinal", "NC")))

    def destacar_sinal_lista(self, item):
        nome_sinal = item.text(); primeiro_foco = None
        if self.pad_selecionado: self.pad_selecionado.atualizar_estilo(selecionado=False)
        for p in self.pads_objetos.values():
            p.destacado = (p.info.get("sinal") == nome_sinal)
            if p.destacado and not primeiro_foco: primeiro_foco = p
            p.atualizar_estilo(selecionado=False)
        if primeiro_foco:
            self.pad_selecionado = primeiro_foco
            self.pad_selecionado.atualizar_estilo(selecionado=True)
            self.label_pad.setText(f"ID: {self.pad_selecionado.coord}")
            self.edit_sinal.setText(self.pad_selecionado.info.get("detalhes", "NC"))
            self.scroll.ensureWidgetVisible(self.pad_selecionado)

    def checar_vazio(self, coord, lista_vazios, lista_letras):
        try:
            m = re.match(r"([A-Z]+)([0-9]+)", coord)
            l, c = lista_letras.index(m.group(1)), int(m.group(2))
            
            for v in lista_vazios:
                m1 = re.match(r"([A-Z]+)([0-9]+)", v["p1"]); l1, c1 = lista_letras.index(m1.group(1)), int(m1.group(2))
                m2 = re.match(r"([A-Z]+)([0-9]+)", v["p2"]); l2, c2 = lista_letras.index(m2.group(1)), int(m2.group(2))
                if (min(l1, l2) <= l <= max(l1, l2)) and (min(c1, c2) <= c <= max(c1, c2)):
                    return True
            return False
        except: return False

    def toggle_modo_vazio(self):
        self.modo_vazio = self.btn_vazio.isChecked()
        if not self.modo_vazio:
            self.btn_vazio.setText("ISOLAR ÁREA VAZIA")
            with open(self.arquivo_atual, 'w', encoding='utf-8') as f: json.dump(self.dados, f, indent=4, ensure_ascii=False)
            self.atualizar_grid()
        else: 
            self.ponto_clicado_1 = None
            self.btn_vazio.setText("➜ SELECIONE O INÍCIO")

    def atualizar_grid(self):
        for i in reversed(range(self.grid_layout.count())):
            item = self.grid_layout.itemAt(i)
            if item and item.widget():
                if isinstance(item.widget(), BGAPad): item.widget().anim_piscar.stop()
                item.widget().deleteLater()
        
        self.pads_objetos = {}
        config = self.dados["chip_config"]; letras = config.get("letras", [])
        colunas = list(range(1, config.get("colunas", 26) + 1))
        if self.view_bottom: colunas.reverse()
        
        lista_vazios = config.get("vazio", [])
        if isinstance(lista_vazios, dict): lista_vazios = [lista_vazios]

        for r, letra in enumerate(letras):
            for vc, rc in enumerate(colunas):
                coord = f"{letra}{rc}"
                pad = BGAPad(coord, self.dados["pinagem"].get(coord))
                if lista_vazios and self.checar_vazio(coord, lista_vazios, letras):
                    pad.visivel = False; pad.atualizar_estilo()
                pad.clicked.connect(self.ao_clicar_pad)
                self.grid_layout.addWidget(pad, r, vc); self.pads_objetos[coord] = pad
        self.atualizar_lista_sinais()

    def salvar_anotacao(self):
        if not self.pad_selecionado: return
        conteudo = self.edit_sinal.toPlainText().strip()
        sinal = conteudo.split("\n")[0].upper() if conteudo else "NC"
        
        if any(x in sinal for x in ["VCC", "VDD"]): tipo = "VCC"
        elif any(x in sinal for x in ["GND", "VSS"]): tipo = "GND"
        else: tipo = "SIGNAL"
        
        self.dados["pinagem"][self.pad_selecionado.coord] = {"sinal": sinal, "tipo": tipo, "detalhes": conteudo}
        with open(self.arquivo_atual, 'w', encoding='utf-8') as f: json.dump(self.dados, f, indent=4, ensure_ascii=False)
        self.pad_selecionado.info = self.dados["pinagem"][self.pad_selecionado.coord]
        self.pad_selecionado.atualizar_estilo(selecionado=True); self.atualizar_lista_sinais()

    def abrir_projeto_json(self):
        nome = self.combo_json.currentText()
        if "Nenhum" in nome: return
        self.arquivo_atual = os.path.join(self.pasta_db, nome)
        self.dados = self.carregar_banco(self.arquivo_atual); self.atualizar_grid()

    def filtrar_lista(self, t):
        for i in range(self.lista_sinais.count()):
            item = self.lista_sinais.item(i); item.setHidden(t.upper() not in item.text().upper())

    def atualizar_lista_sinais(self):
        self.lista_sinais.clear()
        sinais = sorted(list(set(p.get("sinal", "NC") for p in self.dados["pinagem"].values() if p.get("sinal") != "NC")))
        self.lista_sinais.addItems(sinais)

    def executar_mapeamento_completo(self):
        nome = self.combo_excel.currentText()
        if "Nenhum" in nome: return
        try:
            path = os.path.join(self.pasta_excel, nome)
            df = pd.read_excel(path, header=None).dropna(subset=[0])
            pinagem, letras_det, maior_col = {}, set(), 0
            for _, row in df.iterrows():
                coord = str(row[0]).strip().upper()
                if not re.match(r"([A-Z]+)([0-9]+)", coord): continue
                infos = [str(val) for val in row[1:] if pd.notna(val)]
                sinal = infos[0].upper() if infos else "NC"
                
                if any(x in sinal for x in ["VCC", "VDD"]): tipo = "VCC"
                elif any(x in sinal for x in ["GND", "VSS"]): tipo = "GND"
                else: tipo = "SIGNAL"
                
                pinagem[coord] = {"sinal": sinal, "tipo": tipo, "detalhes": "\n".join(infos)}
                m = re.match(r"([A-Z]+)([0-9]+)", coord); letras_det.add(m.group(1)); maior_col = max(maior_col, int(m.group(2)))
            self.arquivo_atual = os.path.join(self.pasta_db, nome.lower().replace(".xlsm", ".json"))
            self.dados = {"chip_config": {"colunas": maior_col, "letras": sorted(list(letras_det), key=lambda x: (len(x), x)), "vazio": []}, "pinagem": pinagem}
            with open(self.arquivo_atual, 'w', encoding='utf-8') as f: json.dump(self.dados, f, indent=4, ensure_ascii=False)
            self.atualizar_grid(); self.atualizar_listas()
        except Exception as e: QMessageBox.critical(self, "Erro", str(e))

    def atualizar_listas(self):
        self.combo_json.clear(); self.combo_excel.clear()
        if os.path.exists(self.pasta_db):
            jsons = [f for f in os.listdir(self.pasta_db) if f.lower().endswith(".json")]
            self.combo_json.addItems(jsons) if jsons else self.combo_json.addItem("Nenhum JSON")
        if os.path.exists(self.pasta_excel):
            excels = [f for f in os.listdir(self.pasta_excel) if f.lower().endswith(".xlsm")]
            self.combo_excel.addItems(excels) if excels else self.combo_excel.addItem("Nenhum Excel")

    def trocar_vista(self, checked):
        self.view_bottom = checked; self.chk_view.setText("MODO BOTTOM VIEW" if checked else "MODO TOP VIEW"); self.atualizar_grid()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    splash = QSplashScreen()
    splash.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
    splash.setStyleSheet("background-color:#050505;")

    screen_geometry = QApplication.desktop().screenGeometry()
    splash.setFixedSize(screen_geometry.width(), screen_geometry.height())

    splash_layout = QVBoxLayout(splash)
    splash_layout.setAlignment(Qt.AlignCenter)
    
    # Logo Centralizado
    pulse_icon = PulseIcon("logo.png")
    splash_layout.addWidget(pulse_icon, 0, Qt.AlignCenter)

    # Titulo com estilo moderno
    label_title = QLabel("BGA CURVE MAPPER")
    label_title.setStyleSheet(f"color: {COLORS['ACCENT']}; font-size: 42px; font-weight: bold; font-family: 'Segoe UI', sans-serif; letter-spacing: 4px;")
    label_title.setAlignment(Qt.AlignCenter)
    splash_layout.addWidget(label_title)

    # Barra de Progresso Fina
    progress_container = QWidget()
    progress_container.setFixedWidth(400)
    prog_lay = QVBoxLayout(progress_container)
    progress = QProgressBar()
    progress.setStyleSheet(f"""
        QProgressBar {{ border: 1px solid #222; background-color: #111; height: 6px; border-radius: 3px; }}
        QProgressBar::chunk {{ background-color: {COLORS['ACCENT']}; border-radius: 3px; }}
    """)
    progress.setRange(0, 100)
    progress.setFormat("")
    prog_lay.addWidget(progress)
    splash_layout.addWidget(progress_container, 0, Qt.AlignCenter)

    label_status = QLabel("CARREGANDO INTERFACE...")
    label_status.setStyleSheet("color: #555; font-size: 10px; font-family: monospace;")
    label_status.setAlignment(Qt.AlignCenter)
    splash_layout.addWidget(label_status)

    splash.showFullScreen()
    pulse_icon.anim_flash.start() # NOME CORRIGIDO AQUI
    app.processEvents()

    steps = [
        (20, "Varrendo diretórios de sistema..."),
        (50, "Indexando mapeamentos BGA..."),
        (80, "Sincronizando banco de dados local..."),
        (100, "Inicialização completa.")
    ]

    for val, txt in steps:
        progress.setValue(val)
        label_status.setText(txt.upper())
        app.processEvents()
        time.sleep(0.5)

    win = BGAVisualizer()
    splash.finish(win)
    win.showMaximized()
    sys.exit(app.exec_())