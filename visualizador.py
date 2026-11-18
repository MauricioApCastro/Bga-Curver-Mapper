import ctypes
import logging
import sys

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QMessageBox

from ui.main_window import BGAVisualizer
from ui.splash import mostrar_splash
from utils.config import APP_NAME, ICON_PATH, LOGO_PATH
from utils.logging_config import install_exception_hook, setup_logging


def configurar_icone_windows():
    if sys.platform != "win32":
        return
    try:
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("mactecnology.bgamapper.app")
    except Exception:
        pass


def main():
    setup_logging()
    install_exception_hook()
    configurar_icone_windows()

    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setWindowIcon(QIcon(ICON_PATH if sys.platform == "win32" else LOGO_PATH))
    app.setStyle("Fusion")

    try:
        splash = mostrar_splash(app)
        win = BGAVisualizer()
        splash.finish(win)
        win.showMaximized()
    except Exception as exc:
        logging.exception("Falha ao iniciar o aplicativo")
        QMessageBox.critical(None, "Erro ao iniciar", str(exc))
        sys.exit(1)

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
