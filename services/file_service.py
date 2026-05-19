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
