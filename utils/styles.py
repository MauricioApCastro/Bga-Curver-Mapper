COLORS = {
    "VCC": "#E53935",
    "GND": "#303F9F",
    "CLOCK": "#00BFA5",
    "RESET": "#D81B60",
    "ADDR": "#FFB300",
    "DATA": "#00A2FF",
    "CONTROL": "#8E24AA",
    "SIGNAL": "#78909C",
    "NC": "#2E2E2E",
    "DEFAULT": "#757575",
    "BG": "#0F0F0F",
    "CARD": "#1A1A1A",
    "TEXT": "#CCCCCC",
    "ACCENT": "#00FF41",
    "HIGHLIGHT": "#FFFF00",
}

BTN_STYLE = (
    "QPushButton { background: #252525; color: #EEE; border: 1px solid #333; "
    "padding: 6px; border-radius: 3px; font-size: 11px; } "
    "QPushButton:hover { background: #353535; border-color: #555; }"
)

COMBO_STYLE = (
    "QComboBox { background: #111; color: #ACC; border: 1px solid #333; "
    "padding: 4px; } QComboBox::drop-down { border: none; }"
)

LEGENDA_TIPOS = (
    ("VCC", "Power"),
    ("GND", "GND"),
    ("CLOCK", "Clock"),
    ("RESET", "Reset"),
    ("ADDR", "Addr"),
    ("DATA", "Dados"),
    ("CONTROL", "Ctrl"),
    ("SIGNAL", "Nao definido"),
    ("NC", "NC"),
)
