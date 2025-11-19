# 📊 Explicação do Script `dashboard_kpis_analise.py`

Este documento descreve o funcionamento completo do script responsável por gerar o **Dashboard Interativo de KPIs de Custos e Eficiência Operacional**, desenvolvido com **Dash + Plotly + Python**.

O dashboard permite analisar:

* Completude dos dados
* Perfil comparativo de custos por **modal** e **município**
* Nível de eficiência operacional
* Ranking de eficiência por **treemap**
* Interpretação automática dos indicadores

---

## 🧩 1. Importação das bibliotecas principais

O script utiliza:

* **Pandas** → carga e tratamento dos dados
* **Dash** e **Dash Core Components** → montagem do dashboard
* **Plotly Express** e **Graph Objects** → gráficos avançados (radar, treemap, heatmap)

```python
import pandas as pd
import dash
from dash import dcc, html, Input, Output
import plotly.express as px
import plotly.graph_objects as go
```

---

## 📂 2. Leitura e normalização dos dados

O arquivo base utilizado é:

```
kpis_custos_unificad_2.xlsx
```

O tratamento inicial:

```python
df = pd.read_excel("kpis_custos_unificad_2.xlsx")
df.columns = df.columns.str.lower().str.strip()
```

Todas as colunas são padronizadas para evitar erros de leitura ou inconsistências.

---

## 🏷️ 3. Colunas principais e KPIs utilizados

```python
col_municipio = "municipio"
col_modal = "tipo_modal"
```

KPIs analisados no dashboard:

* Diversificação de receitas
* % Combustível
* % Mão de Obra Operacional
* % Mão de Obra Administrativa
* % Depreciação
* % Despesas Administrativas

```python
kpis_base = [
    "kpi_diversificacao_receitas",
    "kpi_pct_combustivel",
    "kpi_pct_mao_obra_op",
    "kpi_pct_mao_obra_adm",
    "kpi_pct_depreciacao",
    "kpi_pct_desp_adm",
]
```

---

## 📏 4. Cálculo da Completude dos KPIs

Para cada linha é calculado quantos KPIs estão ausentes:

```python
df["faltantes"] = df[kpis_base].isna().sum(axis=1)
df["completitud"] = 1 - (df["faltantes"] / len(kpis_base))
```

Esse indicador é utilizado no **Mapa de Completude** (heatmap).

---

## 🎯 5. Função do Radar Comparativo

A função `gerar_radar_modal()` cria o radar que compara:

* Média do **modal** selecionado
* Média do **município** (quando disponível)

A função inclui:

✔ Tratamento de dados faltantes
✔ Avisos automáticos sobre KPIs incompletos
✔ Interpretação automática dos resultados

Exemplo:

```python
fig.add_trace(go.Scatterpolar(...))
interpretacion.append("🟢 Boa diversificação de receitas.")
```

---

## 🎨 6. Classificação e cores para o Treemap

Cores usadas no dashboard:

| Categoria | Cor      |
| --------- | -------- |
| Sem dados | Preto    |
| Baixa     | Vermelho |
| Média     | Laranja  |
| Alta      | Verde    |

Regra:

```python
if ef_pct <= 40: "Baja"
elif ef_pct <= 70: "Media"
else: "Alta"
```

---

## 🧱 7. Estrutura da Interface (Layout)

O layout é composto por:

* Filtro de Modal
* Filtro de Município (opcional)
* Gráfico de Completude
* Radar comparativo
* Gráfico de Eficiência
* Treemap com ranking por município
* Legenda e explicações

Exemplo:

```python
app.layout = html.Div([
    html.H1("📊 Análise de KPIs e Eficiência Operacional"),
    dcc.Dropdown(id="filtro_modal", ...),
    dcc.Graph(id="grafico_qualidade"),
    dcc.Graph(id="grafico_eficiencia"),
    dcc.Graph(id="grafico_treemap"),
])
```

---

## 🔄 8. Callback Principal do Dashboard

O callback atualiza **todos os gráficos e textos** com base nos filtros selecionados:

```python
@app.callback(
    [Output("grafico_qualidade", "figure"),
     Output("grafico_eficiencia", "figure"),
     Output("interpretacao_texto", "children"),
     Output("formula_texto", "children"),
     Output("grafico_treemap", "figure"),
     Output("leyenda_eficiencia", "children")],
    [Input("filtro_modal", "value"),
     Input("filtro_municipio", "value")]
)
def atualizar_dashboard(modal_sel, municipio_sel):
```

Dentro dele são gerados:

### ✔ Mapa de Completude

Mostra a qualidade dos dados por modal e município.

### ✔ Radar Modal × Município

Inclui alertas sobre dados incompletos.

### ✔ Cálculo de Eficiência

Com regras específicas para:

* Municípios sem dados
* Dados parciais
* Penalização automática

### ✔ Treemap com Ranking

Inclui:

* Cor por categoria
* Valor da eficiência
* Marca `*` para KPIs incompletos
* “SD” (sem dados) quando aplicável

---

## 🧮 9. Fórmula da Eficiência

Exibida no dashboard:

```
E_bruta = 1 
          - Combustível 
          + Diversificação 
          - (MãoObraAdm / 2) 
          - (MãoObraOp  / 2)

E_pct = E_bruta * 50   # escala 0–100%
```

Notas incluídas:

* Municípios sem dados → “SD”
* Municípios com dados parciais → resultado válido, mas interpretado com cautela

---

## ▶️ 10. Execução do Dashboard

```python
if __name__ == "__main__":
    app.run(debug=True)
```

O dashboard abre em:

```
http://127.0.0.1:8050/
```

---

## 🧪 11. Funcionalidades Principais

### ✔ Comparação entre modal e município

### ✔ Interpretação automática e textual

### ✔ Radar dinâmico

### ✔ Mapa de completude

### ✔ Ranking geral via treemap

### ✔ Tratamento robusto de dados faltantes

---
