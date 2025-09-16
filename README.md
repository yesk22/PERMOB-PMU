# PERMOB → PMU — Estratégia Digital (Starter)

Projeto para transformar a planilha **PERMOB 2024** em **KPIs e diagnósticos** nas dimensões **infraestrutura, qualidade, custos e planejamento**, com entregas organizadas em 3 sprints e apresentação final na **Feira de Soluções (04/12/2025)**.

## Sprints e marcos
- **Sprint 1** — Review & Demo: **02/10/2025**
- **Sprint 2** — Review & Demo: **25/10/2025**
- **Sprint 3** — Review & Demo: **20/11/2025**
- **Hardening/Go‑Live**: 21/11 → 03/12/2025
- **Feira de Soluções**: **04/12/2025**

## Como rodar (ETL mínimo)
```bash
# Requisitos: Python 3.10+
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux/macOS
# source .venv/bin/activate

pip install -r requirements.txt
python src/etl/load_permob.py --input data/raw/pemob_municipal_2024.xlsx --summary reports/permob_resumo.md
```

## Estrutura
```
.
├─ src/
│  ├─ etl/                 # scripts de ingestão/limpeza
│  └─ dashboard/           # código do dashboard/app (futuro)
├─ data/
│  ├─ raw/                 # planilhas originais (não versionar dados sensíveis)
│  └─ processed/           # dados tratados/derivados
├─ notebooks/              # análises exploratórias
├─ reports/                # relatórios exportados (PDF/MD)
├─ docs/                   # documentação
├─ configs/                # YAML/JSON de parâmetros e mapeamentos
├─ tests/                  # testes automatizados
└─ .github/                # templates, CI, etc.
```

## Convenções
- **Branching**: `main` protegido; feature branches em `feat/<slug>`, `fix/<slug>`, `data/<slug>`.
- **Commits** (sugestão): `type(scope): mensagem` — ex.: `feat(qualidade): calcular velocidade média`.
- **Tags**: `v0.1` (S1), `v0.2` (S2), `v1.0` (S3), `v1.1` (Feira).
- **KPIs**: manter o **dicionário** em `docs/kpis.md` e referenciar fonte/colunas da PERMOB 2024.

## Licença
MIT — ver `LICENSE`.
