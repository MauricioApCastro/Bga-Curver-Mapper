import os
import sys
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
os.environ.setdefault("PYTHONIOENCODING", "utf-8")

PROJ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJ)
os.chdir(PROJ)

from PyQt5.QtWidgets import QApplication, QDialog, QLabel, QPushButton

app = QApplication.instance()
if app is None:
    app = QApplication(sys.argv)

import ui.criar_bga_dialog as cbd
import ui.main_window as mw


class TestRegressaoBugsCorrigidos(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.w = mw.BGAVisualizer()
        cls.w.resize(1200, 800)
        cls.w.show()
        QApplication.processEvents()

    def test_reg01_dialog_com_rotulos_visiveis(self):
        """Garante que o diálogo de criação não use mais QInputDialog sem rótulos."""
        d = cbd.CriarBgaDialog()
        textos = [lbl.text() for lbl in d.findChildren(QLabel)]
        self.assertIn("Linhas:", textos)
        self.assertIn("Colunas:", textos)
        self.assertIn("Nome do BGA:", textos)

    def test_reg02_nome_automatico_e_sanitizacao(self):
        """Garante sugestão automática e sanitização de nomes inválidos."""
        self.assertEqual(cbd.nome_padrao(676, 26), "bga_vazio_676p_26x26")
        self.assertEqual(cbd.sanitizar_nome("Meu BGA / teste.json"), "Meu BGA _ teste")
        self.assertEqual(cbd.sanitizar_nome("chip<>teste"), "chip__teste")

    def test_reg03_mensagem_projeto_criado_legivel(self):
        """Garante que 'Projeto criado' use ui.mensagens.mostrar (texto visível)."""
        exibidas = []

        def fake_mostrar(parent, titulo, texto, icone=None):
            exibidas.append((titulo, texto))

        original = mw.mostrar
        mw.mostrar = fake_mostrar
        try:

            class FakeDialog:
                def __init__(self, parent=None):
                    pass

                def exec_(self):
                    return QDialog.Accepted

                def get_values(self):
                    return (25, 5, "regressao_teste")

            orig_dlg = mw.CriarBgaDialog
            mw.CriarBgaDialog = FakeDialog
            try:
                self.w.criar_bga_vazio()
            finally:
                mw.CriarBgaDialog = orig_dlg
        finally:
            mw.mostrar = original

        self.assertTrue(exibidas, "A mensagem de criação deveria ser exibida.")
        self.assertEqual(exibidas[0][0], "BGA vazio")
        self.assertIn("Projeto criado", exibidas[0][1])

        caminho = os.path.join(self.w.pasta_db, "regressao_teste.json")
        if os.path.exists(caminho):
            os.remove(caminho)

    def test_reg04_botao_desfazer_criacao_removido(self):
        """Garante que o botão 'DESFAZER CRIACAO' foi removido."""
        botoes = [b.text() for b in self.w.findChildren(QPushButton)]
        self.assertNotIn("DESFAZER CRIACAO", botoes)
        self.assertFalse(hasattr(self.w, "btn_desfazer"))

    def test_reg05_botao_salvar_presente(self):
        """Garante que o botão 'SALVAR' continua presente."""
        botoes = [b.text() for b in self.w.findChildren(QPushButton)]
        self.assertIn("SALVAR", botoes)
        self.assertTrue(hasattr(self.w, "btn_salvar"))

    def test_reg06_espacamento_entre_importar_e_criar(self):
        """Garante maior espaçamento entre 'IMPORTAR EXCEL' e 'CRIAR BGA VAZIO'."""
        btn_importar = self.w.edit_busca_excel
        btn_criar = [b for b in self.w.findChildren(QPushButton) if b.text() == "CRIAR BGA VAZIO"][
            0
        ]
        gap = (
            btn_criar.mapTo(self.w, btn_criar.rect().topLeft()).y()
            - btn_importar.mapTo(self.w, btn_importar.rect().bottomLeft()).y()
        )
        self.assertGreaterEqual(gap, 8, f"Espaçamento insuficiente: {gap}px")

    def test_reg07_botao_voltar_ao_lado_pronto_proxima(self):
        """Garante botão VOLTAR ao lado do botão de isolar área."""
        botoes = [b.text() for b in self.w.findChildren(QPushButton)]
        self.assertIn("VOLTAR", botoes)
        self.assertIn("ISOLAR AREA VAZIA", botoes)
        self.assertTrue(hasattr(self.w, "btn_voltar"))
        self.assertTrue(hasattr(self.w, "btn_vazio"))
        self.assertFalse(self.w.btn_voltar.isEnabled())

    def test_reg08_voltar_em_etapas(self):
        """Garante que VOLTAR desfaz ponto pendente, remove área e sai do modo."""
        if self.w.modo_vazio:
            self.w.btn_vazio.click()
            QApplication.processEvents()

        self.w.btn_vazio.click()
        QApplication.processEvents()
        self.assertTrue(self.w.modo_vazio)
        self.assertTrue(self.w.btn_voltar.isEnabled())
        self.assertEqual(self.w.btn_vazio.text(), "SELECIONE O INICIO")

        pads = list(self.w.pads_objetos.values())
        if len(pads) >= 2:
            pads[0].clicked.emit()
            QApplication.processEvents()
            self.assertIsNotNone(self.w.ponto_clicado_1)
            self.assertEqual(self.w.btn_vazio.text(), "SELECIONE O FIM")
            self.w.btn_voltar.click()
            QApplication.processEvents()
            self.assertIsNone(self.w.ponto_clicado_1)
            self.assertEqual(self.w.btn_vazio.text(), "SELECIONE O INICIO")

            pads[0].clicked.emit()
            pads[1].clicked.emit()
            QApplication.processEvents()
            vazios = self.w.dados["chip_config"].get("vazio", [])
            if isinstance(vazios, dict):
                vazios = [vazios]
            qtd = len(vazios)
            self.w.btn_voltar.click()
            QApplication.processEvents()
            vazios2 = self.w.dados["chip_config"].get("vazio", [])
            if isinstance(vazios2, dict):
                vazios2 = [vazios2]
            self.assertEqual(len(vazios2), max(0, qtd - 1))

        self.w.btn_vazio.click()
        QApplication.processEvents()
        self.w.btn_vazio.click()
        QApplication.processEvents()
        self.w.btn_voltar.click()
        QApplication.processEvents()
        self.assertFalse(self.w.modo_vazio)
        self.assertFalse(self.w.btn_voltar.isEnabled())
        self.assertEqual(self.w.btn_vazio.text(), "ISOLAR AREA VAZIA")


if __name__ == "__main__":
    unittest.main(verbosity=2)
