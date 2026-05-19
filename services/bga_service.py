import re

import pandas as pd


BANCO_PADRAO = {
    "chip_config": {"colunas": 26, "letras": [], "vazio": []},
    "pinagem": {},
}


def normalizar_banco(dados):
    dados = dados or {
        "chip_config": {"colunas": 26, "letras": [], "vazio": []},
        "pinagem": {},
    }
    dados.setdefault("chip_config", {})
    dados.setdefault("pinagem", {})
    dados["chip_config"].setdefault("colunas", 26)
    dados["chip_config"].setdefault("letras", [])
    dados["chip_config"].setdefault("vazio", [])

    if isinstance(dados["chip_config"]["vazio"], dict):
        dados["chip_config"]["vazio"] = [dados["chip_config"]["vazio"]]

    return dados


def identificar_tipo_sinal(sinal):
    if any(x in sinal for x in ["VCC", "VDD"]):
        return "VCC"
    if any(x in sinal for x in ["GND", "VSS"]):
        return "GND"
    return "SIGNAL"


def criar_info_pad(conteudo):
    sinal = conteudo.split("\n")[0].upper() if conteudo else "NC"
    return {
        "sinal": sinal,
        "tipo": identificar_tipo_sinal(sinal),
        "detalhes": conteudo,
    }


def coordenada_para_indices(coord, letras):
    match = re.match(r"([A-Z]+)([0-9]+)", coord)
    if not match:
        return None
    return letras.index(match.group(1)), int(match.group(2))


def checar_area_vazia(coord, lista_vazios, lista_letras):
    try:
        indices = coordenada_para_indices(coord, lista_letras)
        if not indices:
            return False
        linha, coluna = indices

        for area in lista_vazios:
            linha_1, coluna_1 = coordenada_para_indices(area["p1"], lista_letras)
            linha_2, coluna_2 = coordenada_para_indices(area["p2"], lista_letras)
            dentro_linhas = min(linha_1, linha_2) <= linha <= max(linha_1, linha_2)
            dentro_colunas = min(coluna_1, coluna_2) <= coluna <= max(coluna_1, coluna_2)
            if dentro_linhas and dentro_colunas:
                return True
        return False
    except Exception:
        return False


def listar_sinais(dados):
    return sorted({
        pad.get("sinal", "NC")
        for pad in dados["pinagem"].values()
        if pad.get("sinal") != "NC"
    })


def importar_excel(caminho):
    df = pd.read_excel(caminho, header=None).dropna(subset=[0])
    pinagem, letras_detectadas, maior_coluna = {}, set(), 0

    for _, row in df.iterrows():
        coord = str(row[0]).strip().upper()
        match = re.match(r"([A-Z]+)([0-9]+)", coord)
        if not match:
            continue

        infos = [str(valor) for valor in row[1:] if pd.notna(valor)]
        sinal = infos[0].upper() if infos else "NC"
        pinagem[coord] = {
            "sinal": sinal,
            "tipo": identificar_tipo_sinal(sinal),
            "detalhes": "\n".join(infos),
        }
        letras_detectadas.add(match.group(1))
        maior_coluna = max(maior_coluna, int(match.group(2)))

    return {
        "chip_config": {
            "colunas": maior_coluna,
            "letras": sorted(letras_detectadas, key=lambda x: (len(x), x)),
            "vazio": [],
        },
        "pinagem": pinagem,
    }
