import os
import sys

APP_NAME = "BGA Mapper"
APP_VERSION = "1.1.1"

SUPPORT_EMAIL = "contato.mactecnology@gmail.com"


def _app_base_dir():
    if getattr(sys, "frozen", False):
        return getattr(sys, "_MEIPASS", os.path.dirname(sys.executable))
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _user_files_dir():
    documents_dir = os.path.join(os.path.expanduser("~"), "Documents")
    if not os.path.isdir(documents_dir):
        documents_dir = os.path.expanduser("~")
    return os.path.join(documents_dir, APP_NAME)


BASE_DIR = _app_base_dir()
USER_FILES_DIR = _user_files_dir() if getattr(sys, "frozen", False) else BASE_DIR

DATA_DIR = os.path.join(USER_FILES_DIR, "data")
EXCEL_DIR = os.path.join(USER_FILES_DIR, "excels")
ASSETS_DIR = os.path.join(BASE_DIR, "assets")

DEFAULT_DATABASE = "database.json"
LOGO_PATH = os.path.join(ASSETS_DIR, "logo.png")
ICON_PATH = os.path.join(ASSETS_DIR, "logo.ico")
LOG_FILE = os.path.join(USER_FILES_DIR, "bga_mapper.log")
