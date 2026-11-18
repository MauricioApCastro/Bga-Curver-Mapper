import re

import pandas as pd

from models.pad_model import PadModel


def importar_excel(caminho):
    df = pd.read_excel(caminho, header=None)
    if df.empty:
        raise ValueError("A planilha esta vazia.")
    df = df.dropna(subset=[0])
    pinagem, letras_detectadas, maior_coluna = {}, set(), 0

    for _, row in df.iterrows():
        coord = str(row[0]).strip().upper()
        match = re.match(r"([A-Z]+)([0-9]+)", coord)
        if not match:
            continue

        infos = [str(valor) for valor in row[1:] if pd.notna(valor)]
        pinagem[coord] = PadModel.from_infos(infos).to_dict()
        letras_detectadas.add(match.group(1))
        maior_coluna = max(maior_coluna, int(match.group(2)))

    if not pinagem:
        raise ValueError(
            "Nenhuma coordenada BGA valida (ex: A1) encontrada na primeira coluna da planilha."
        )

    return {
        "chip_config": {
            "colunas": maior_coluna,
            "letras": sorted(letras_detectadas, key=lambda x: (len(x), x)),
            "vazio": [],
        },
        "pinagem": pinagem,
    }
