import re

import pandas as pd

from utils.bga_utils import identificar_tipo_sinal


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
