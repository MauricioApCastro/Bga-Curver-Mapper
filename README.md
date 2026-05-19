# BGA Curve Mapper

Aplicativo em PyQt5 para visualizar, importar e editar mapeamentos de pinagem BGA a partir de arquivos JSON e Excel.


<img src="assets/screenshoots/main_screen.png" alt="Tela principal do BGA Curve Mapper">

# BGA Curve Mapper

Sistema desktop profissional desenvolvido em Python e PyQt5 para análise visual de componentes BGA, mapeamento eletrônico, organização de sinais e integração com datasheets PDF.

![Screenshot](assets/screenshots/main_screen.png)

---

# Sobre o Projeto

O BGA Curve Mapper foi criado para auxiliar na análise técnica de placas eletrônicas e componentes BGA, permitindo visualizar pads, organizar sinais, importar planilhas Excel e acessar rapidamente datasheets em PDF.

O sistema foi desenvolvido com foco em:
- produtividade técnica
- análise visual
- engenharia reversa
- organização eletrônica
- velocidade de diagnóstico

---

# Funcionalidades

## Visualização BGA
- Renderização gráfica dos pads
- Identificação visual por cores
- Destaque de sinais
- Top View / Bottom View

## Importação Excel
- Importação automática de pinagem
- Conversão para banco JSON
- Organização dinâmica dos sinais

## Integração PDF
- Visualizador de datasheet integrado
- Busca automática de componentes
- Destaque visual do termo encontrado
- Zoom e navegação inteligente

## Ferramentas Visuais
- Zoom
- Pan
- Seleção dinâmica
- Highlight de pads
- Isolamento de áreas vazias

## Arquitetura Modular
- UI separada
- Services
- Organização escalável
- Estrutura preparada para evolução futura

---

# Tecnologias Utilizadas

- Python
- PyQt5
- Pandas
- PyMuPDF
- JSON
- Excel
- QSS Styling

---

# Estrutura do Projeto

```bash
src/
 ├── ui/
 ├── services/
 ├── assets/
 ├── data/
```

---

# Objetivos do Projeto

- Criar uma ferramenta técnica profissional
- Melhorar fluxo de análise eletrônica
- Integrar software + eletrônica
- Evoluir arquitetura desktop moderna em Python

---

# Como Executar

## Clone o projeto

```bash
git clone https://github.com/MauricioApCastro/Bga-Curver-Mapper.git
```

## Entre na pasta

```bash
cd Bga-Curver-Mapper
```

## Instale as dependências

```bash
pip install -r requirements.txt
```

## Execute

```bash
python main.py
```

---

# Futuras Melhorias

- Banco de dados SQLite
- Sistema de projetos
- Exportação avançada
- Busca inteligente de sinais
- Integração IA
- Melhorias visuais
- Refatoração completa em arquitetura modular

---

# Autor

Mauricio Castro

Técnico eletrônico e desenvolvedor Python focado em:
- software técnico
- automação
- eletrônica
- interfaces desktop
- integração hardware/software

GitHub:
https://github.com/MauricioApCastro
