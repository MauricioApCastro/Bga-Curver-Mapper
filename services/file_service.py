import json
import os
import tempfile


class FileServiceError(Exception):
    pass


def resolver_caminho_seguro(pasta_base, nome_arquivo, extensao=None):
    base = os.path.abspath(pasta_base)
    caminho = os.path.abspath(os.path.join(base, nome_arquivo))
    if os.path.commonpath([base, caminho]) != base:
        raise FileServiceError("Caminho de arquivo fora da pasta permitida.")
    if extensao and not caminho.lower().endswith(extensao.lower()):
        raise FileServiceError(f"Extensao invalida. Use arquivos {extensao}.")
    return caminho


def garantir_pastas(*pastas):
    for pasta in pastas:
        if not os.path.exists(pasta):
            os.makedirs(pasta)


def listar_arquivos(pasta, extensao):
    if not os.path.exists(pasta):
        return []
    arquivos = [
        nome for nome in os.listdir(pasta)
        if os.path.isfile(os.path.join(pasta, nome)) and nome.lower().endswith(extensao.lower())
    ]
    return sorted(arquivos, key=str.lower)


def carregar_json(caminho, padrao=None):
    if not os.path.exists(caminho):
        return padrao
    try:
        with open(caminho, "r", encoding="utf-8") as arquivo:
            return json.load(arquivo)
    except json.JSONDecodeError as exc:
        raise FileServiceError(f"JSON invalido: {os.path.basename(caminho)}") from exc
    except OSError as exc:
        raise FileServiceError(f"Nao foi possivel abrir: {os.path.basename(caminho)}") from exc


def salvar_json(caminho, dados):
    pasta = os.path.dirname(os.path.abspath(caminho))
    garantir_pastas(pasta)
    fd, temporario = tempfile.mkstemp(prefix=".bga_", suffix=".json", dir=pasta, text=True)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as arquivo:
            json.dump(dados, arquivo, indent=4, ensure_ascii=False)
        os.replace(temporario, caminho)
    except Exception:
        try:
            os.remove(temporario)
        except OSError:
            pass
        raise
