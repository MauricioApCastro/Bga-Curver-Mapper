from dataclasses import asdict, dataclass


@dataclass
class PadModel:
    sinal: str = "NC"
    tipo: str = "DEFAULT"
    detalhes: str = "NC"

    @classmethod
    def from_conteudo(cls, conteudo):
        sinal = conteudo.split("\n")[0].upper() if conteudo else "NC"
        return cls(
            sinal=sinal,
            tipo=identificar_tipo_sinal(sinal),
            detalhes=conteudo,
        )

    @classmethod
    def from_infos(cls, infos):
        sinal = infos[0].upper() if infos else "NC"
        return cls(
            sinal=sinal,
            tipo=identificar_tipo_sinal(sinal),
            detalhes="\n".join(infos),
        )

    def to_dict(self):
        return asdict(self)


def identificar_tipo_sinal(sinal):
    if any(x in sinal for x in ["VCC", "VDD"]):
        return "VCC"
    if any(x in sinal for x in ["GND", "VSS"]):
        return "GND"
    return "SIGNAL"
