import sys

from PyQt5.QtWidgets import QApplication

from ui.main_window import BGAVisualizer
from ui.splash import mostrar_splash


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    splash = mostrar_splash(app)
    win = BGAVisualizer()
    splash.finish(win)
    win.showMaximized()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
