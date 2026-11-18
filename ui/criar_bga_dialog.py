import re

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QSpinBox,
    QVBoxLayout,
)

from ui.mensagens import mostrar
from utils.styles import BTN_STYLE, COLORS

LABEL_STYLE = f"color: {COLORS['TEXT']}; font-size: 12px;"
INPUT_STYLE = (
    f"QLineEdit {{ background: #111; color: {COLORS['TEXT']}; "
    "border: 1px solid #444; padding: 6px; border-radius: 3px; font-size: 12px; }}"
)
SPIN_STYLE = (
    f"QSpinBox {{ background: #111; color: {COLORS['TEXT']}; "
    "border: 1px solid #444; padding: 6px; border-radius: 3px; font-size: 12px; }}"
    "QSpinBox::up-button, QSpinBox::down-button { background: #252525; "
    "border: 1px solid #333; width: 16px; }"
)


LIMITE_PADS = 10000


def nome_padrao(total_pinos, colunas):
    linhas = (total_pinos + colunas - 1) // colunas
    return f"bga_vazio_{total_pinos}p_{linhas}x{colunas}"


def sanitizar_nome(texto):
    nome = re.sub(r'[<>:"/\\|?*]', "_", texto or "").strip().strip(".")
    if nome.lower().endswith(".json"):
        nome = nome[:-5].strip().strip(".")
    return nome


class CriarBgaDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Criar BGA vazio")
        self.setModal(True)
        self.setMinimumWidth(460)
        self.setStyleSheet(f"QDialog {{ background: {COLORS['BG']}; }}")
        self._nome_manual = False
        self.total_pinos = None
        self.colunas = None
        self.nome = ""
        self._build_ui()
        self._atualizar_nome()

    def _label(self, texto):
        label = QLabel(texto)
        label.setStyleSheet(LABEL_STYLE)
        return label

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(22, 22, 22, 18)
        layout.setSpacing(14)

        titulo = QLabel("Criar BGA vazio")
        titulo.setStyleSheet(f"color: {COLORS['ACCENT']}; font-size: 16px; font-weight: bold;")
        layout.addWidget(titulo)

        form = QFormLayout()
        form.setSpacing(10)
        form.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)

        self.spin_linhas = QSpinBox()
        self.spin_linhas.setRange(1, 1000)
        self.spin_linhas.setValue(10)
        self.spin_linhas.setStyleSheet(SPIN_STYLE)
        self.spin_linhas.valueChanged.connect(self._atualizar_nome)
        form.addRow(self._label("Linhas:"), self.spin_linhas)

        self.spin_colunas = QSpinBox()
        self.spin_colunas.setRange(1, 1000)
        self.spin_colunas.setValue(10)
        self.spin_colunas.setStyleSheet(SPIN_STYLE)
        self.spin_colunas.valueChanged.connect(self._atualizar_nome)
        form.addRow(self._label("Colunas:"), self.spin_colunas)

        self.label_total = QLabel()
        self.label_total.setStyleSheet(
            f"color: {COLORS['ACCENT']}; font-size: 13px; font-weight: bold;"
        )
        form.addRow(self._label("Total de pads:"), self.label_total)

        self.edit_nome = QLineEdit()
        self.edit_nome.setStyleSheet(INPUT_STYLE)
        self.edit_nome.setPlaceholderText("Ex: U12_BGA")
        self.edit_nome.textEdited.connect(self._marcar_nome_manual)
        form.addRow(self._label("Nome do BGA:"), self.edit_nome)

        layout.addLayout(form)

        dica = QLabel("Sera salvo como <nome>.json na pasta de projetos.")
        dica.setStyleSheet("color: #666; font-size: 10px;")
        layout.addWidget(dica)

        botoes = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        botoes.button(QDialogButtonBox.Ok).setText("CRIAR")
        botoes.button(QDialogButtonBox.Cancel).setText("CANCELAR")
        for botao in (
            botoes.button(QDialogButtonBox.Ok),
            botoes.button(QDialogButtonBox.Cancel),
        ):
            botao.setStyleSheet(BTN_STYLE)
        botoes.accepted.connect(self._validar)
        botoes.rejected.connect(self.reject)
        layout.addWidget(botoes)

    def _marcar_nome_manual(self):
        self._nome_manual = True

    def _total_pads(self):
        return self.spin_linhas.value() * self.spin_colunas.value()

    def _atualizar_nome(self):
        self.label_total.setText(
            f"{self._total_pads()}  ({self.spin_linhas.value()} x {self.spin_colunas.value()})"
        )

    def _validar(self):
        nome = sanitizar_nome(self.edit_nome.text())
        if not nome:
            mostrar(self, "Nome invalido", "Informe um nome para o BGA.", QMessageBox.Warning)
            return
        if self._total_pads() > LIMITE_PADS:
            mostrar(
                self,
                "BGA muito grande",
                f"O BGA teria {self._total_pads()} pads. O limite e {LIMITE_PADS}.",
                QMessageBox.Warning,
            )
            return
        self.total_pinos = self._total_pads()
        self.colunas = self.spin_colunas.value()
        self.nome = nome
        self.accept()

    def get_values(self):
        return self.total_pinos, self.colunas, self.nome
