import os
import sys
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
os.environ.setdefault("PYTHONIOENCODING", "utf-8")

PROJ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJ)
os.chdir(PROJ)

from PyQt5.QtWidgets import QApplication, QPushButton, QDialog

app = QApplication.instance()
if app is None:
    app = QApplication(sys.argv)

import ui.main_window as mw
import ui.criar_bga_dialog as cbd



class TestCriarBgaDialog(unittest.TestCase):
    def test_labels_visiveis(self):
        d = cbd.CriarBgaDialog()
        textos = [l.text() for l in d.findChildren(__import__('PyQt5.QtWidgets', fromlist=['QLabel']).QLabel)]
        self.assertIn("Linhas:", textos)
        self.assertIn("Colunas:", textos)
        self.assertIn("Nome do BGA:", textos)

    def test_nome_comeca_vazio_e_total_calculado(self):
        d = cbd.CriarBgaDialog()
        d.spin_linhas.setValue(26)
        d.spin_colunas.setValue(26)
        self.assertEqual(d.edit_nome.text(), "")
        self.assertTrue(d.label_total.text().startswith("676"))

    def test_sanitizar(self):
        self.assertEqual(cbd.sanitizar_nome("Meu BGA / teste.json"), "Meu BGA _ teste")
        self.assertEqual(cbd.sanitizar_nome('a<>b'), "a__b")

    def test_validacao_nome_vazio(self):
        import ui.criar_bga_dialog as cbd_mod
        orig = cbd_mod.mostrar
        cbd_mod.mostrar = lambda *a, **k: None
        try:
            d = cbd.CriarBgaDialog()
            d.edit_nome.clear()
            d._validar()
            self.assertIsNone(d.total_pinos)
        finally:
            cbd_mod.mostrar = orig



class TestPainelLateral(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.w = mw.BGAVisualizer()
        cls.w.resize(1200, 800)
        cls.w.show()
        QApplication.processEvents()

    def test_botoes_esperados(self):
        textos = [b.text() for b in self.w.findChildren(QPushButton)]
        self.assertNotIn("CARREGAR ARQUIVO", textos)
        self.assertNotIn("IMPORTAR EXCEL", textos)
        self.assertIn("CRIAR BGA VAZIO", textos)
        self.assertIn("ISOLAR AREA VAZIA", textos)
        self.assertIn("VOLTAR", textos)
        self.assertIn("SALVAR", textos)
        self.assertNotIn("DESFAZER CRIACAO", textos)

    def test_espacamento_importar_criar(self):
        btn_import = self.w.edit_busca_excel
        btn_criar = [b for b in self.w.findChildren(QPushButton) if b.text() == "CRIAR BGA VAZIO"][0]
        gap = btn_criar.mapTo(self.w, btn_criar.rect().topLeft()).y() - btn_import.mapTo(self.w, btn_import.rect().bottomLeft()).y()
        self.assertGreaterEqual(gap, 8)

    def test_voltar_habilitado_modo_vazio(self):
        self.w.btn_vazio.click()
        QApplication.processEvents()
        self.assertTrue(self.w.modo_vazio)
        self.assertTrue(self.w.btn_voltar.isEnabled())
        self.w.btn_voltar.click()
        QApplication.processEvents()
        self.assertFalse(self.w.modo_vazio)
        self.assertFalse(self.w.btn_voltar.isEnabled())

    def test_voltar_remove_area(self):
        self.w.btn_vazio.click()
        QApplication.processEvents()
        pads = list(self.w.pads_objetos.values())
        if len(pads) < 2:
            self.skipTest("poucos pads")
        pads[0].clicked.emit()
        pads[1].clicked.emit()
        QApplication.processEvents()
        vazios = self.w.dados["chip_config"].get("vazio", [])
        if isinstance(vazios, dict):
            vazios = [vazios]
        self.assertGreaterEqual(len(vazios), 1)
        self.w.btn_voltar.click()
        QApplication.processEvents()
        vazios2 = self.w.dados["chip_config"].get("vazio", [])
        if isinstance(vazios2, dict):
            vazios2 = [vazios2]
        self.assertEqual(len(vazios2), 0)

    def test_criar_bga_usa_mensagem_legivel(self):
        mostrados = []

        def fake_mostrar(parent, titulo, texto, icone=None):
            mostrados.append((titulo, texto))

        original = mw.mostrar
        mw.mostrar = fake_mostrar
        try:
            class FakeDialog:
                def __init__(self, parent=None):
                    pass
                def exec_(self):
                    return QDialog.Accepted
                def get_values(self):
                    return (16, 4, "teste_auto_bga")

            orig_dlg = mw.CriarBgaDialog
            mw.CriarBgaDialog = FakeDialog
            try:
                self.w.criar_bga_vazio()
            finally:
                mw.CriarBgaDialog = orig_dlg
        finally:
            mw.mostrar = original

        self.assertTrue(mostrados)
        self.assertEqual(mostrados[0][0], "BGA vazio")
        self.assertIn("Projeto criado", mostrados[0][1])
        json_path = os.path.join(self.w.pasta_db, "teste_auto_bga.json")
        if os.path.exists(json_path):
            os.remove(json_path)


if __name__ == "__main__":
    unittest.main(verbosity=2)
