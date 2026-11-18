import os

from PyQt5.QtCore import QEasingCurve, QEvent, QPoint, QVariantAnimation, Qt, QTimer
from PyQt5.QtGui import QIcon, QTransform
from PyQt5.QtWidgets import (
    QDialog,
    QGridLayout,
    QHBoxLayout,
    QAction,
    QApplication,
    QMainWindow,
    QMessageBox,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from services.excel_service import importar_excel
from services.file_service import (
    FileServiceError,
    carregar_json,
    garantir_pastas,
    listar_arquivos,
    resolver_caminho_seguro,
    salvar_json,
)
from ui import ajuda
from ui.criar_bga_dialog import CriarBgaDialog
from ui.mensagens import mostrar, perguntar
from ui.widgets import BGAPad, criar_legenda, criar_painel_lateral
from utils.bga_utils import (
    BANCO_PADRAO,
    checar_area_vazia,
    coordenada_para_indices,
    criar_banco_vazio,
    criar_info_pad,
    listar_sinais,
    normalizar_banco,
)
from models.pad_model import identificar_tipo_sinal
from utils.config import DATA_DIR, EXCEL_DIR, ICON_PATH
from utils.styles import COLORS


class BGAVisualizer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("BGA Mapper")
        self.setWindowIcon(QIcon(ICON_PATH))
        self.pasta_db, self.pasta_excel = DATA_DIR, EXCEL_DIR
        garantir_pastas(self.pasta_db, self.pasta_excel)

        self.arquivo_atual = None
        self.excel_atual = None
        self.alterado = False
        self.tipo_filtro = None
        self.grupo = set()
        self.pad_selecionado = None
        self.pads_objetos = {}
        self.view_bottom = False
        self.modo_vazio = False
        self.ponto_clicado_1 = None
        self.zoom = 1.0
        self._zoom_base_tamanho = 28

        self.dados = self.carregar_banco()
        self.init_ui()
        self.definir_alterado(False)
        self.atualizar_grid()
        self.atualizar_listas()
        self.limpar_campos()

    def carregar_banco(self, caminho=None):
        alvo = caminho or self.arquivo_atual
        if not alvo:
            return normalizar_banco(BANCO_PADRAO.copy())
        try:
            return normalizar_banco(carregar_json(alvo, BANCO_PADRAO.copy()))
        except FileServiceError as erro:
            mostrar(self, "Erro ao abrir JSON", str(erro), QMessageBox.Critical)
            return normalizar_banco(BANCO_PADRAO.copy())

    def init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(10, 10, 10, 10)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(False)
        self.scroll.setAlignment(Qt.AlignCenter)
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll.setStyleSheet("border: none; background: #000;")
        self.grid_widget = QWidget()
        self.grid_layout = QGridLayout(self.grid_widget)
        self.grid_layout.setAlignment(Qt.AlignCenter)
        self.scroll.setWidget(self.grid_widget)
        self.scroll.viewport().installEventFilter(self)
        self.scroll.viewport().setCursor(Qt.OpenHandCursor)
        self.grid_widget.installEventFilter(self)
        coluna_bga = QVBoxLayout()
        coluna_bga.setSpacing(4)
        coluna_bga.addWidget(self.scroll, 1)
        coluna_bga.addWidget(criar_legenda(self))
        main_layout.addLayout(coluna_bga, 4)

        side_widget = criar_painel_lateral(self)
        side_widget.setFixedWidth(296)
        main_layout.addWidget(side_widget)
        self.setStyleSheet(
            f"QMainWindow, QWidget {{ background: {COLORS['BG']}; }}"
            f"QMenuBar {{ background: {COLORS['BG']}; color: {COLORS['TEXT']}; }}"
            "QMenuBar::item:selected { background: #252525; }"
            f"QMenu {{ background: {COLORS['CARD']}; color: {COLORS['TEXT']}; border: 1px solid #333; }}"
            "QMenu::item:selected { background: #004488; }"
        )
        self._criar_menu_ajuda()

    def _criar_menu_ajuda(self):
        menu = self.menuBar().addMenu("&Ajuda")
        itens = (
            ("&Guia de uso", "F1", lambda: ajuda.mostrar_guia(self)),
            ("&Suporte", None, lambda: ajuda.mostrar_suporte(self)),
            (None, None, None),
            ("&Termos de uso", None, lambda: ajuda.mostrar_termos(self)),
            ("&Privacidade", None, lambda: ajuda.mostrar_privacidade(self)),
            (None, None, None),
            ("&Sobre o BGA Mapper", None, lambda: ajuda.mostrar_sobre(self)),
        )
        for rotulo, atalho, acao in itens:
            if rotulo is None:
                menu.addSeparator()
                continue
            item = QAction(rotulo, self)
            if atalho:
                item.setShortcut(atalho)
            item.triggered.connect(lambda _checked=False, f=acao: f())
            menu.addAction(item)

    def definir_alterado(self, alterado):
        self.alterado = alterado
        cor, hover, dica = (
            ("#B26A00", "#CC7A00", "Alteracoes nao salvas")
            if alterado
            else ("#1B6B2F", "#238A3D", "Tudo salvo")
        )
        self.btn_salvar.setToolTip(dica)
        self.btn_salvar.setStyleSheet(
            f"QPushButton {{ background: {cor}; color: white; font-weight: bold; border-radius: 4px; font-size: 11px; }}"
            f"QPushButton:hover {{ background: {hover}; }}"
        )

    def filtrar_por_tipo(self, tipo):
        self.tipo_filtro = None if self.tipo_filtro == tipo else tipo
        self._aplicar_filtro_tipo()

    def limpar_filtro_tipo(self):
        if self.tipo_filtro is not None:
            self.tipo_filtro = None
            self._aplicar_filtro_tipo()

    def _aplicar_filtro_tipo(self):
        for t, botao in getattr(self, "botoes_legenda", {}).items():
            botao.setChecked(t == self.tipo_filtro)
        for pad in self.pads_objetos.values():
            if self.tipo_filtro is None:
                pad.destacado = False
                pad.esmaecido = False
            else:
                casa = identificar_tipo_sinal(pad.info.get("sinal", "")) == self.tipo_filtro
                pad.destacado = casa
                pad.esmaecido = not casa
            if pad.visivel:
                pad.atualizar_estilo(selecionado=pad is self.pad_selecionado)

    def ao_editar_sinal(self):
        if self.pad_selecionado and self.edit_sinal.hasFocus():
            self.definir_alterado(True)

    def ao_clicar_pad(self):
        pad = self.sender()
        if self.modo_vazio:
            if not self.ponto_clicado_1:
                self.ponto_clicado_1 = pad.coord
                self.btn_vazio.setText("SELECIONE O FIM")
            else:
                self.dados["chip_config"].setdefault("vazio", [])
                self.dados["chip_config"]["vazio"].append({"p1": self.ponto_clicado_1, "p2": pad.coord})
                self.definir_alterado(True)
                self.ponto_clicado_1 = None
                self.btn_vazio.setText("PRONTO OU PROXIMA?")
                self.atualizar_grid()
            return

        self.limpar_filtro_tipo()
        mods = QApplication.keyboardModifiers()
        if mods & Qt.ControlModifier:
            self._alternar_no_grupo(pad)
        elif mods & Qt.ShiftModifier and self.pad_selecionado:
            self._selecionar_retangulo(self.pad_selecionado, pad)
        else:
            self._limpar_grupo()
            for pad_obj in self.pads_objetos.values():
                if pad_obj.destacado:
                    pad_obj.destacado = False
                    pad_obj.atualizar_estilo(selecionado=False)
            if self.pad_selecionado:
                self.pad_selecionado.atualizar_estilo(selecionado=False)
            self.lista_sinais.clearSelection()
            self.pad_selecionado = pad
            self.pad_selecionado.atualizar_estilo(selecionado=True)
            self.label_pad.setText(f"ID: {pad.coord}")
            self.edit_sinal.setText(pad.info.get("detalhes", pad.info.get("sinal", "")))

    def _limpar_grupo(self):
        for coord in list(self.grupo):
            pad = self.pads_objetos.get(coord)
            if pad is not None:
                pad.agrupado = False
                pad.atualizar_estilo(selecionado=False)
        self.grupo = set()

    def _atualizar_rotulo_grupo(self):
        total = len(self.grupo)
        if total > 1:
            self.label_pad.setText(f"{total} PADS SELECIONADOS")
        elif self.pad_selecionado:
            self.label_pad.setText(f"ID: {self.pad_selecionado.coord}")
        else:
            self.label_pad.setText("")

    def _definir_principal(self, pad):
        anterior = self.pad_selecionado
        self.pad_selecionado = pad
        if anterior is not None and anterior is not pad:
            anterior.atualizar_estilo(selecionado=False)
        if pad is not None:
            pad.atualizar_estilo(selecionado=True)

    def _alternar_no_grupo(self, pad):
        if self.pad_selecionado and not self.grupo:
            self.grupo.add(self.pad_selecionado.coord)
            self.pad_selecionado.agrupado = True
        self.lista_sinais.clearSelection()
        if pad.coord in self.grupo:
            self.grupo.discard(pad.coord)
            pad.agrupado = False
            pad.atualizar_estilo(selecionado=False)
            restante = next((self.pads_objetos[c] for c in sorted(self.grupo) if c in self.pads_objetos), None)
            if pad is self.pad_selecionado:
                self._definir_principal(restante)
        else:
            self.grupo.add(pad.coord)
            pad.agrupado = True
            self._definir_principal(pad)
        self._atualizar_rotulo_grupo()

    def _selecionar_retangulo(self, origem, destino):
        letras = self.dados["chip_config"].get("letras", [])
        a = coordenada_para_indices(origem.coord, letras)
        b = coordenada_para_indices(destino.coord, letras)
        if not a or not b:
            return
        l1, l2 = sorted((a[0], b[0]))
        c1, c2 = sorted((a[1], b[1]))
        for coord, pad in self.pads_objetos.items():
            if not pad.visivel:
                continue
            ind = coordenada_para_indices(coord, letras)
            if ind and l1 <= ind[0] <= l2 and c1 <= ind[1] <= c2:
                self.grupo.add(coord)
                pad.agrupado = True
                if pad is not destino:
                    pad.atualizar_estilo(selecionado=False)
        self.lista_sinais.clearSelection()
        self._definir_principal(destino)
        self._atualizar_rotulo_grupo()

    def destacar_sinal_lista(self, item):
        nome_sinal = item.text()
        primeiro_foco = None
        self.limpar_filtro_tipo()
        self._limpar_grupo()
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
            self.edit_sinal.setText(self.pad_selecionado.info.get("detalhes", ""))
            self.scroll.ensureWidgetVisible(self.pad_selecionado)

    def toggle_modo_vazio(self):
        self.modo_vazio = self.btn_vazio.isChecked()
        if not self.modo_vazio:
            self.btn_vazio.setText("ISOLAR AREA VAZIA")
            self.salvar_banco_atual()
            self.atualizar_grid()
        else:
            self.ponto_clicado_1 = None
            self.btn_vazio.setText("SELECIONE O INICIO")
        if hasattr(self, "btn_voltar"):
            self.btn_voltar.setEnabled(self.modo_vazio)

    def voltar_modo_vazio(self):
        if not self.modo_vazio:
            return
        if self.ponto_clicado_1:
            self.ponto_clicado_1 = None
            self.btn_vazio.setText("SELECIONE O INICIO")
            return

        vazios = self.dados["chip_config"].get("vazio", [])
        if isinstance(vazios, dict):
            vazios = [vazios]
            self.dados["chip_config"]["vazio"] = vazios
        if vazios:
            vazios.pop()
            self.salvar_banco_atual()
            self.atualizar_grid()
            self.btn_vazio.setText("PRONTO OU PROXIMA?")
            return

        self.modo_vazio = False
        self.btn_vazio.setChecked(False)
        self.btn_vazio.setText("ISOLAR AREA VAZIA")
        if hasattr(self, "btn_voltar"):
            self.btn_voltar.setEnabled(False)

    def atualizar_grid(self):
        for i in reversed(range(self.grid_layout.count())):
            item = self.grid_layout.itemAt(i)
            if item and item.widget():
                if isinstance(item.widget(), BGAPad):
                    item.widget().anim_piscar.stop()
                item.widget().deleteLater()

        coord_selecionada = getattr(self.pad_selecionado, "coord", None)
        self.pads_objetos = {}
        self.grupo = set()
        self.pad_selecionado = None
        config = self.dados["chip_config"]
        letras = config.get("letras", [])
        colunas = list(range(1, config.get("colunas", 26) + 1))
        if self.view_bottom:
            colunas.reverse()

        lista_vazios = config.get("vazio", [])
        if isinstance(lista_vazios, dict):
            lista_vazios = [lista_vazios]

        tamanho = self._calcular_tamanho_pad(len(colunas), len(letras))
        self._zoom_base_tamanho = tamanho
        self.zoom = 1.0
        self.grid_layout.setSpacing(1 if tamanho >= 5 else 0)
        self.grid_layout.setContentsMargins(2, 2, 2, 2)
        self.grid_layout.setAlignment(Qt.AlignCenter)

        for r, letra in enumerate(letras):
            for vc, rc in enumerate(colunas):
                coord = f"{letra}{rc}"
                pad = BGAPad(coord, self.dados["pinagem"].get(coord), tamanho)
                if lista_vazios and checar_area_vazia(coord, lista_vazios, letras):
                    pad.visivel = False
                    pad.atualizar_estilo()
                pad.clicked.connect(self.ao_clicar_pad)
                pad.installEventFilter(self)
                self.grid_layout.addWidget(pad, r, vc)
                self.pads_objetos[coord] = pad
        self._ajustar_tamanho_grid_widget()
        self.atualizar_lista_sinais()
        novo = self.pads_objetos.get(coord_selecionada)
        if novo is not None and novo.visivel:
            self.pad_selecionado = novo
            novo.atualizar_estilo(selecionado=True)
        else:
            self.label_pad.setText("")
        if self.tipo_filtro is not None:
            self._aplicar_filtro_tipo()

    def _calcular_tamanho_pad(self, total_colunas, total_linhas):
        viewport = self.scroll.viewport().size()
        largura = max(viewport.width() - 14, 120)
        altura = max(viewport.height() - 14, 120)
        colunas = max(1, total_colunas)
        linhas = max(1, total_linhas)
        por_largura = largura / colunas
        por_altura = altura / linhas
        return max(2, min(80, int(min(por_largura, por_altura)) - 1))

    def _ajustar_pads_ao_viewport(self):
        if not self.pads_objetos:
            return
        config = self.dados["chip_config"]
        tamanho = self._calcular_tamanho_pad(
            config.get("colunas", 26), len(config.get("letras", []))
        )
        self._zoom_base_tamanho = tamanho
        self.zoom = 1.0
        self.grid_layout.setSpacing(1 if tamanho >= 5 else 0)
        for pad in self.pads_objetos.values():
            if pad.tamanho != tamanho:
                pad.aplicar_tamanho(tamanho)
        self._ajustar_tamanho_grid_widget()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if getattr(self, "scroll", None) and self.zoom == 1.0:
            self._ajustar_pads_ao_viewport()

    def showEvent(self, event):
        super().showEvent(event)
        if not getattr(self, "_ja_exibida", False):
            self._ja_exibida = True
            QTimer.singleShot(0, self._ajustar_pads_ao_viewport)

    def _confirmar_descartar(self):
        """Pergunta o que fazer com alteracoes nao salvas. True = pode seguir."""
        if not self.alterado:
            return True
        if self.arquivo_atual:
            escolha = perguntar(
                self,
                "Alteracoes nao salvas",
                "Existem alteracoes nao salvas. Deseja salvar antes de continuar?",
                [("Salvar", QMessageBox.AcceptRole), ("Descartar", QMessageBox.DestructiveRole), ("Cancelar", QMessageBox.RejectRole)],
                padrao="Salvar",
            )
            if escolha == "Salvar":
                self.salvar_anotacao()
                return not self.alterado
            return escolha == "Descartar"
        escolha = perguntar(
            self,
            "Alteracoes nao salvas",
            "As alteracoes atuais serao perdidas. Continuar?",
            [("Continuar", QMessageBox.DestructiveRole), ("Cancelar", QMessageBox.RejectRole)],
            padrao="Cancelar",
        )
        return escolha == "Continuar"

    @staticmethod
    def _mesmo_arquivo(a, b):
        if not a or not b:
            return False
        return os.path.normcase(os.path.abspath(a)) == os.path.normcase(os.path.abspath(b))

    def closeEvent(self, event):
        if self._confirmar_descartar():
            event.accept()
        else:
            event.ignore()

    def eventFilter(self, obj, event):
        tipo = event.type()
        if tipo == QEvent.Wheel:
            if event.angleDelta().y() != 0:
                ponto = obj.mapTo(self.scroll.viewport(), event.pos())
                self.aplicar_zoom(1.1 if event.angleDelta().y() > 0 else 0.9, ponto)
            return True
        if tipo == QEvent.MouseButtonPress and event.button() == Qt.LeftButton:
            self._pan_inicio = event.globalPos()
            self._pan_scroll = (
                self.scroll.horizontalScrollBar().value(),
                self.scroll.verticalScrollBar().value(),
            )
            self._pan_ativo = False
        elif tipo == QEvent.MouseMove and event.buttons() & Qt.LeftButton:
            inicio = getattr(self, "_pan_inicio", None)
            if inicio is not None:
                delta = event.globalPos() - inicio
                if not self._pan_ativo and delta.manhattanLength() > 6:
                    self._pan_ativo = True
                    self._parar_animacao_zoom()
                    self.scroll.viewport().setCursor(Qt.ClosedHandCursor)
                    if hasattr(obj, "setDown"):
                        obj.setDown(False)
                if self._pan_ativo:
                    self.scroll.horizontalScrollBar().setValue(self._pan_scroll[0] - delta.x())
                    self.scroll.verticalScrollBar().setValue(self._pan_scroll[1] - delta.y())
                    return True
        elif tipo == QEvent.MouseButtonRelease and event.button() == Qt.LeftButton:
            arrastou = getattr(self, "_pan_ativo", False)
            self._pan_inicio = None
            self._pan_ativo = False
            self.scroll.viewport().setCursor(Qt.OpenHandCursor)
            if arrastou:
                if hasattr(obj, "setDown"):
                    obj.setDown(False)
                return True
        return super().eventFilter(obj, event)

    def _pad_no_ponto(self, ponto):
        view = self.scroll.viewport()
        pos = self.grid_widget.mapFrom(view, ponto)
        alvo = self.grid_widget.childAt(pos)
        while alvo is not None and not isinstance(alvo, BGAPad):
            alvo = alvo.parentWidget()
        if alvo is not None:
            return alvo
        melhor, menor = None, None
        for pad in self.pads_objetos.values():
            centro = pad.geometry().center()
            dist = (centro.x() - pos.x()) ** 2 + (centro.y() - pos.y()) ** 2
            if menor is None or dist < menor:
                melhor, menor = pad, dist
        return melhor

    def _parar_animacao_zoom(self):
        anim = getattr(self, "_anim_zoom", None)
        if anim is not None:
            anim.stop()

    def _animar_scroll(self, inicio, fim):
        self._parar_animacao_zoom()
        sb_h = self.scroll.horizontalScrollBar()
        sb_v = self.scroll.verticalScrollBar()
        sb_h.setValue(int(inicio[0]))
        sb_v.setValue(int(inicio[1]))
        anim = QVariantAnimation(self)
        anim.setDuration(160)
        anim.setStartValue(0.0)
        anim.setEndValue(1.0)
        anim.setEasingCurve(QEasingCurve.OutCubic)

        def passo(t):
            sb_h.setValue(int(inicio[0] + (fim[0] - inicio[0]) * t))
            sb_v.setValue(int(inicio[1] + (fim[1] - inicio[1]) * t))

        anim.valueChanged.connect(passo)
        anim.finished.connect(lambda: passo(1.0))
        self._anim_zoom = anim
        anim.start()

    def aplicar_zoom(self, fator, ponto=None):
        if not self.pads_objetos:
            return
        view = self.scroll.viewport()
        if ponto is None:
            ponto = view.rect().center()
        self._parar_animacao_zoom()

        selecionado = self.pads_objetos.get(getattr(self.pad_selecionado, "coord", None))
        ponto_sel = None
        if selecionado is not None:
            ponto_sel = selecionado.mapTo(view, selecionado.rect().center())
            if not view.rect().contains(ponto_sel):
                selecionado = None

        if selecionado is not None:
            coord, frac = selecionado.coord, None
        else:
            pad_ref = self._pad_no_ponto(ponto)
            coord = pad_ref.coord
            pos = self.grid_widget.mapFrom(view, ponto)
            frac = (
                (pos.x() - pad_ref.x()) / max(1, pad_ref.tamanho),
                (pos.y() - pad_ref.y()) / max(1, pad_ref.tamanho),
            )

        self.zoom = max(0.25, min(8.0, self.zoom * fator))
        tamanho_base = getattr(self, "_zoom_base_tamanho", 28)
        tamanho = max(2, int(tamanho_base * self.zoom))
        for pad in self.pads_objetos.values():
            if pad.tamanho != tamanho:
                pad.aplicar_tamanho(tamanho)
        self.grid_layout.setSpacing(1 if tamanho >= 5 else 0)
        self._ajustar_tamanho_grid_widget()
        self.grid_layout.activate()
        pad = self.pads_objetos[coord]

        if frac is None:
            # o pad selecionado nao salta: segue onde estava e desliza ate o centro
            centro = pad.mapTo(self.grid_widget, pad.rect().center())
            inicio = (centro.x() - ponto_sel.x(), centro.y() - ponto_sel.y())
            fim = (centro.x() - view.width() / 2, centro.y() - view.height() / 2)
            self._animar_scroll(inicio, fim)
            return
        alvo_x = pad.x() + frac[0] * pad.tamanho
        alvo_y = pad.y() + frac[1] * pad.tamanho
        self.scroll.horizontalScrollBar().setValue(int(alvo_x - ponto.x()))
        self.scroll.verticalScrollBar().setValue(int(alvo_y - ponto.y()))

    def _ajustar_tamanho_grid_widget(self):
        if not self.pads_objetos:
            return
        config = self.dados["chip_config"]
        letras = config.get("letras", [])
        colunas = config.get("colunas", 26)
        tamanho = self.pads_objetos[next(iter(self.pads_objetos))].tamanho
        espa = max(0, self.grid_layout.spacing())
        conteudo_l = colunas * (tamanho + espa)
        conteudo_a = len(letras) * (tamanho + espa)
        self._conteudo = (conteudo_l, conteudo_a)
        if self.zoom > 1.0001:
            view = self.scroll.viewport()
            largura = conteudo_l + view.width()
            altura = conteudo_a + view.height()
        else:
            largura = conteudo_l + 10
            altura = conteudo_a + 10
        self.grid_widget.setMinimumSize(largura, altura)
        self.grid_widget.resize(largura, altura)
    def salvar_banco_atual(self):
        if not self.arquivo_atual:
            return
        salvar_json(self.arquivo_atual, self.dados)
        self.definir_alterado(False)
        self.atualizar_listas(json_selecionado=os.path.basename(self.arquivo_atual), excel_selecionado=self.excel_atual)

    def salvar_anotacao(self):
        if not self.arquivo_atual:
            mostrar(self, "Salvar", "Abra um projeto, importe uma planilha ou crie um BGA vazio antes de salvar.")
            return
        if not self.pad_selecionado:
            self.salvar_banco_atual()
            return
        conteudo = self.edit_sinal.toPlainText().strip()
        coords = set(self.grupo) | {self.pad_selecionado.coord}
        for coord in coords:
            self.dados["pinagem"][coord] = criar_info_pad(conteudo)
        self.salvar_banco_atual()
        for coord in coords:
            pad = self.pads_objetos.get(coord)
            if pad is not None:
                pad.info = self.dados["pinagem"][coord]
                pad.atualizar_estilo(selecionado=pad is self.pad_selecionado)
        self.atualizar_lista_sinais()

    def abrir_projeto_json(self):
        item = self.lista_json.currentItem()
        if not item or item.isHidden():
            mostrar(self, "Carregar JSON", "Selecione um JSON na lista.")
            return
        nome = item.text()
        try:
            caminho = resolver_caminho_seguro(self.pasta_db, nome, ".json")
            dados = normalizar_banco(carregar_json(caminho, None))
        except FileServiceError as erro:
            mostrar(self, "Erro ao abrir JSON", str(erro), QMessageBox.Critical)
            return
        if not self._confirmar_descartar():
            return
        self.edit_busca_json.blockSignals(True)
        self.edit_busca_json.setText(os.path.splitext(nome)[0])
        self.edit_busca_json.blockSignals(False)
        self.lista_json.setVisible(False)
        self.arquivo_atual = caminho
        self.dados = dados
        self.definir_alterado(False)
        self.atualizar_grid()
        self.limpar_campos()
        QTimer.singleShot(0, self._ajustar_pads_ao_viewport)

    @staticmethod
    def _filtrar_lista_arquivos(lista, texto):
        def normalizar(valor):
            return "".join(c for c in valor.lower() if c.isalnum())

        termos = [normalizar(t) for t in texto.split() if normalizar(t)]
        lista.clearSelection()
        lista.setCurrentItem(None)
        for i in range(lista.count()):
            item = lista.item(i)
            nome = normalizar(item.text())
            item.setHidden(not termos or not all(t in nome for t in termos))
        lista.setVisible(any(not lista.item(i).isHidden() for i in range(lista.count())))

    def filtrar_json(self, texto):
        self._filtrar_lista_arquivos(self.lista_json, texto)

    def filtrar_excel(self, texto):
        self.excel_atual = None
        self._filtrar_lista_arquivos(self.lista_excel, texto)

    def escolher_excel(self, item):
        self.excel_atual = item.text()
        self.edit_busca_excel.blockSignals(True)
        self.edit_busca_excel.setText(os.path.splitext(self.excel_atual)[0])
        self.edit_busca_excel.blockSignals(False)
        self.lista_excel.setVisible(False)
        self.executar_mapeamento_completo()

    def selecionar_unico_excel_filtrado(self):
        visiveis = [
            self.lista_excel.item(i)
            for i in range(self.lista_excel.count())
            if not self.lista_excel.item(i).isHidden()
        ]
        if len(visiveis) == 1:
            self.escolher_excel(visiveis[0])

    def abrir_primeiro_json_filtrado(self):
        visiveis = [
            self.lista_json.item(i)
            for i in range(self.lista_json.count())
            if not self.lista_json.item(i).isHidden()
        ]
        if len(visiveis) == 1:
            self.lista_json.setCurrentItem(visiveis[0])
            self.abrir_projeto_json()

    def selecionar_json(self, nome):
        for i in range(self.lista_json.count()):
            item = self.lista_json.item(i)
            if item.text() == nome:
                item.setHidden(False)
                self.lista_json.setCurrentItem(item)
                self.lista_json.scrollToItem(item)
                return

    def filtrar_lista(self, texto):
        for i in range(self.lista_sinais.count()):
            item = self.lista_sinais.item(i)
            item.setHidden(texto.upper() not in item.text().upper())

    def atualizar_lista_sinais(self):
        self.lista_sinais.clear()
        self.lista_sinais.addItems(listar_sinais(self.dados))

    def limpar_campos(self):
        self.grupo = set()
        self.pad_selecionado = None
        self.label_pad.setText("")
        self.edit_sinal.clear()
        self.lista_sinais.clearSelection()

    def criar_bga_vazio(self):
        if not self._confirmar_descartar():
            return
        dialog = CriarBgaDialog(self)
        if dialog.exec_() != QDialog.Accepted:
            return

        total_pinos, colunas, nome_base = dialog.get_values()
        if not total_pinos or not nome_base:
            return

        self.dados = criar_banco_vazio(total_pinos, colunas)

        nome = f"{nome_base}.json"
        caminho = os.path.join(self.pasta_db, nome)
        contador = 2
        while os.path.exists(caminho):
            nome = f"{nome_base}_{contador}.json"
            caminho = os.path.join(self.pasta_db, nome)
            contador += 1

        self.arquivo_atual = caminho
        salvar_json(caminho, self.dados)
        self.definir_alterado(False)
        self.atualizar_grid()
        self.atualizar_listas(json_selecionado=nome)
        self.selecionar_json(nome)
        self.limpar_campos()
        mostrar(self, "BGA vazio", f"Projeto criado: {nome}")

    def executar_mapeamento_completo(self):
        nome = self.excel_atual
        if not nome:
            mostrar(self, "Importar planilha", "Busque e clique em uma planilha na lista.")
            return
        try:
            caminho = resolver_caminho_seguro(self.pasta_excel, nome, ".xlsm")
            destino = resolver_caminho_seguro(
                self.pasta_db,
                nome.lower().replace(".xlsm", ".json"),
                ".json",
            )
            novos_dados = importar_excel(caminho)
        except Exception as erro:
            mostrar(self, "Erro ao importar planilha", str(erro), QMessageBox.Critical)
            return
        if not self._confirmar_descartar():
            return
        if os.path.exists(destino) and not self._mesmo_arquivo(destino, self.arquivo_atual):
            escolha = perguntar(
                self,
                "Projeto ja existe",
                f"Ja existe o projeto {os.path.basename(destino)}.\n"
                "Ao salvar, ele sera substituido pelo conteudo da planilha. Continuar?",
                [("Importar", QMessageBox.AcceptRole), ("Cancelar", QMessageBox.RejectRole)],
                padrao="Cancelar",
            )
            if escolha != "Importar":
                return
        try:
            self.arquivo_atual = destino
            self.dados = novos_dados
            self.definir_alterado(True)
            self.atualizar_grid()
            self.atualizar_listas(excel_selecionado=nome)
            self.lista_json.clearSelection()
            self.lista_json.setCurrentItem(None)
            self.limpar_campos()
        except Exception as erro:
            mostrar(self, "Erro", str(erro), QMessageBox.Critical)

    def atualizar_listas(self, json_selecionado=None, excel_selecionado=None):
        self.lista_json.clear()
        self.lista_excel.clear()

        jsons = listar_arquivos(self.pasta_db, ".json")
        self.lista_json.addItems(jsons)
        self.edit_busca_json.blockSignals(True)
        self.edit_busca_json.clear()
        self.edit_busca_json.blockSignals(False)
        for i in range(self.lista_json.count()):
            self.lista_json.item(i).setHidden(True)
        if json_selecionado in jsons:
            self.edit_busca_json.setText(os.path.splitext(json_selecionado)[0])
            self.selecionar_json(json_selecionado)
        self.lista_json.setVisible(False)

        excels = listar_arquivos(self.pasta_excel, ".xlsm")
        self.lista_excel.addItems(excels)
        self.edit_busca_excel.blockSignals(True)
        self.edit_busca_excel.clear()
        self.edit_busca_excel.blockSignals(False)
        self.excel_atual = None
        if excel_selecionado in excels:
            self.excel_atual = excel_selecionado
            self.edit_busca_excel.blockSignals(True)
            self.edit_busca_excel.setText(os.path.splitext(excel_selecionado)[0])
            self.edit_busca_excel.blockSignals(False)
        self.lista_excel.setVisible(False)

    def trocar_vista(self, checked):
        self.view_bottom = checked
        self.chk_view.setText("MODO BOTTOM VIEW" if checked else "MODO TOP VIEW")
        self.atualizar_grid()
