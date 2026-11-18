# BGA Curve Mapper

[![CI](https://github.com/MauricioApCastro/Bga-Curver-Mapper/actions/workflows/ci.yml/badge.svg)](https://github.com/MauricioApCastro/Bga-Curver-Mapper/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![PyQt5](https://img.shields.io/badge/GUI-PyQt5-41cd52)

Aplicativo desktop para **visualizar, importar e editar mapeamentos de pinagem BGA** (Ball Grid Array), feito para técnicos de eletrônica que fazem diagnóstico, reparo e engenharia reversa de placas.

Um projeto [MAC Tecnology](https://mactecnology.com.br).

<img src="assets/screenshoots/main_screen.png" alt="Tela principal do BGA Curve Mapper" width="800">

## Funcionalidades

- **Grade BGA interativa:** cada pad tem cor por tipo de sinal (Power, GND, Clock, Reset, Addr, Dados, Ctrl, NC e Não definido), com legenda clicável que mostra só os pads do tipo escolhido.
- **Zoom e navegação:** roda do mouse para zoom (centraliza o pad selecionado) e arrastar para mover o mapa.
- **Seleção em grupo:** Ctrl + clique e Shift + clique para aplicar a mesma função a vários pads de uma vez.
- **Vista superior e inferior** (top / bottom view).
- **Projetos:** busca pelo nome do arquivo, criação de BGA vazio por linhas × colunas e botão Salvar que indica alterações pendentes.
- **Importação do Excel:** lê planilhas de pinagem (`.xlsm`) e converte para um banco JSON.
- **Áreas vazias:** marque regiões sem esferas para que a grade fique igual ao chip real.
- **Busca e filtro de sinais**, com lista dos sinais existentes no componente.
- **Ajuda integrada:** guia de uso (F1), suporte, termos e privacidade no menu Ajuda.
- **Bancos prontos** em `data/` para chips como ICH6 (82801), GX1, FW82439HX, EPF10K100 e flashes TE28F.

## Requisitos

- Python 3.10 ou superior
- Windows, Linux ou macOS

## Como executar

```bash
git clone https://github.com/MauricioApCastro/Bga-Curver-Mapper.git
cd Bga-Curver-Mapper

python -m venv .venv
# Windows: .venv\Scripts\activate   |   Linux/macOS: source .venv/bin/activate

pip install -r requirements.txt
python visualizador.py
```

## Gerar o executável (Windows)

```bash
pip install -r requirements-dev.txt pyinstaller
pyinstaller --noconfirm --clean BGA_Mapper.spec
```

O aplicativo empacotado fica em `dist/BGA Mapper/`. Para gerar o instalador, compile `installer/BGA_Mapper.iss` com o [Inno Setup](https://jrsoftware.org/isinfo.php) (ou rode `installer/build_release.ps1`). Para distribuir, anexe o instalador a uma **Release** do GitHub em vez de colocá-lo no repositório.

## Estrutura

```
├── visualizador.py      # ponto de entrada
├── ui/                  # janelas e widgets (PyQt5)
│   └── widgets/         # pad BGA, painel lateral, ícone animado
├── services/            # leitura de Excel e arquivos
├── models/              # modelo de dados do pad e classificação por tipo
├── utils/               # configurações, estilos e funções da grade
├── data/                # bancos de pinagem em JSON
├── excels/              # planilhas de origem
├── docs/                # guia de uso, termos e privacidade
├── installer/           # script do instalador (Inno Setup)
├── tests/               # testes da interface
└── assets/              # ícones, logo e capturas de tela
```

## Desenvolvimento

```bash
pip install -r requirements-dev.txt
ruff check .          # análise de código
ruff format .         # formatação automática
```

O GitHub Actions roda essas verificações a cada envio para a branch `main`.

## Próximos passos

- Visualizador de datasheets em PDF integrado
- Banco de dados SQLite e sistema de projetos
- Exportação avançada e busca inteligente de sinais

## Contato

contato.mactecnology@gmail.com
