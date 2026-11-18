import re

from models.pad_model import PadModel

# Alfabeto JEDEC BGA sem as letras omitidas: I, O, Q, S, X, Z
LETRAS_JEDEC = "ABCDEFGHJKLMNPRTUVWY"  # 20 letras válidas por ciclo

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

    # Arquivos antigos gravavam "NC" como padrao de todo pad ainda nao mapeado.
    # Um NC marcado de proposito tem tipo "NC" e e preservado.
    for coord, pad in list(dados["pinagem"].items()):
        if (
            isinstance(pad, dict)
            and pad.get("sinal") == "NC"
            and pad.get("tipo") in ("DEFAULT", "SIGNAL")
            and pad.get("detalhes", "NC") in ("NC", "")
        ):
            dados["pinagem"][coord] = PadModel().to_dict()

    return dados


def criar_info_pad(conteudo):
    return PadModel.from_conteudo(conteudo).to_dict()


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
    return sorted(
        {
            pad.get("sinal", "")
            for pad in dados["pinagem"].values()
            if pad.get("sinal", "") not in ("", "NC")
        }
    )


def indice_para_letra(indice):
    """
    Gera as letras de linhas de BGA no padrão JEDEC.
    Exclui I, O, Q, S, X, Z.
    Suporta matrizes grandes com letras duplas (AA, AB, AC...).
    """
    base = len(LETRAS_JEDEC)  # 20 letras
    letras = ""
    while indice > 0:
        indice, resto = divmod(indice - 1, base)
        letras = LETRAS_JEDEC[resto] + letras
    return letras


def criar_banco_vazio(total_pinos, colunas):
    if total_pinos < 1:
        raise ValueError("Informe pelo menos 1 pino.")
    if colunas < 1:
        raise ValueError("Informe pelo menos 1 coluna.")

    linhas = (total_pinos + colunas - 1) // colunas
    letras = [indice_para_letra(indice) for indice in range(1, linhas + 1)]
    pinagem = {}

    for indice in range(total_pinos):
        linha = indice // colunas
        coluna = (indice % colunas) + 1
        pinagem[f"{letras[linha]}{coluna}"] = PadModel().to_dict()

    posicoes = linhas * colunas
    vazio = []
    if total_pinos < posicoes:
        primeira_sobra = total_pinos
        ultima_sobra = posicoes - 1
        vazio.append(
            {
                "p1": f"{letras[primeira_sobra // colunas]}{(primeira_sobra % colunas) + 1}",
                "p2": f"{letras[ultima_sobra // colunas]}{(ultima_sobra % colunas) + 1}",
            }
        )

    return {
        "chip_config": {"colunas": colunas, "letras": letras, "vazio": vazio},
        "pinagem": pinagem,
    }
