import logging
import os
import sys

from utils.config import LOG_FILE, USER_FILES_DIR


def setup_logging():
    os.makedirs(USER_FILES_DIR, exist_ok=True)
    logging.basicConfig(
        filename=LOG_FILE,
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        encoding="utf-8",
    )


def install_exception_hook():
    def handle_exception(exc_type, exc_value, exc_traceback):
        logging.critical("Erro nao tratado", exc_info=(exc_type, exc_value, exc_traceback))
        sys.__excepthook__(exc_type, exc_value, exc_traceback)

    sys.excepthook = handle_exception
