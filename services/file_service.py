import json
import os


def garantir_pastas(*pastas):
    for pasta in pastas:
        if not os.path.exists(pasta):
            os.makedirs(pasta)


def listar_arquivos(pasta, extensao):
    if not os.path.exists(pasta):
        return []
    return [
        nome for nome in os.listdir(pasta)
        if nome.lower().endswith(extensao.lower())
    ]


def carregar_json(caminho, padrao=None):
    if os.path.exists(caminho):
        try:
            with open(caminho, "r", encoding="utf-8") as arquivo:
                return json.load(arquivo)
        except Exception:
            pass
    return padrao


def salvar_json(caminho, dados):
    with open(caminho, "w", encoding="utf-8") as arquivo:
        json.dump(dados, arquivo, indent=4, ensure_ascii=False)
