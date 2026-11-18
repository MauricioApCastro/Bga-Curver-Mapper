import re
from dataclasses import asdict, dataclass


@dataclass
class PadModel:
    sinal: str = ""
    tipo: str = "SIGNAL"
    detalhes: str = ""

    @classmethod
    def from_conteudo(cls, conteudo):
        sinal = conteudo.split("\n")[0].strip().upper() if conteudo else ""
        return cls(
            sinal=sinal,
            tipo=identificar_tipo_sinal(sinal),
            detalhes=conteudo,
        )

    @classmethod
    def from_infos(cls, infos):
        sinal = infos[0].strip().upper() if infos else ""
        return cls(
            sinal=sinal,
            tipo=identificar_tipo_sinal(sinal),
            detalhes="\n".join(infos),
        )

    def to_dict(self):
        return asdict(self)


_REGRAS_TIPO = (
    ("NC", r"NC\d*|NOCONNECT|DNU|DNP"),
    ("GND", r"[ADP]?GND\w*|VSS\w*|VSSQ|EGND|GROUND"),
    ("VCC", r"[AD]?VCC\w*|[AD]?VDD\w*|VDDQ|VIN\d*|VBAT|VBUS|VREF\w*|PWR\w*|VCORE|\d+V\d*"),
    ("RESET", r"N?RST\w*|RESET\w*|POR|PORST\w*"),
    ("CLOCK", r"N?S?CLK\w*|CK\d*|XTAL\w*|XI|XO|OSC\w*|CLOCK\w*|REFCLK\w*"),
    ("ADDR", r"ADDR\w*|ADR\w*|A\d+|BA\d+|RAS|CAS|AD\d+"),
    ("DATA", r"DATA\w*|D\d+|DQ\w*|DQS\w*|SDA|MOSI|MISO|TX\w*|RX\w*|DM\d*"),
    ("CONTROL", r"N?CS\d*|N?WE|N?OE|N?CE\d*|EN\w*|ENABLE|N?RD|N?WR|CKE|ODT|INT\w*|IRQ\w*"),
)


def identificar_tipo_sinal(sinal):
    sinal = (sinal or "").strip().upper()
    if not sinal:
        return "SIGNAL"
    if sinal == "NC":
        return "NC"
    tokens = [t for t in re.split(r"[^A-Z0-9]+", sinal) if t]
    for tipo, padrao in _REGRAS_TIPO:
        if any(re.fullmatch(padrao, token) for token in tokens):
            return tipo
    return "SIGNAL"
