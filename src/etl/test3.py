# dashboard_kpis_analise.py

## .venv\Scripts\Activate.ps1 
import pandas as pd
import dash
from dash import dcc, html, Input, Output
import plotly.express as px
import plotly.graph_objects as go

# === 1. Cargar los datos ===
df = pd.read_excel("kpis_custos_unificad_2.xlsx")

# === 2. Normalizar columnas ===
df.columns = df.columns.str.lower().str.strip()

# === 3. Variables base ===
col_municipio = "municipio"
col_modal = "tipo_modal"

kpis_base = [
    "kpi_diversificacao_receitas",
    "kpi_pct_combustivel",
    "kpi_pct_mao_obra_op",
    "kpi_pct_mao_obra_adm",
    "kpi_pct_depreciacao",
    "kpi_pct_desp_adm",
]

# === 4. Métrica de calidad/completitud ===
# Cuenta cuántos KPIs faltan por fila
df["faltantes"] = df[kpis_base].isna().sum(axis=1)
df["completitud"] = 1 - (df["faltantes"] / len(kpis_base))

# Listas únicas
modais = sorted(df[col_modal].dropna().unique())
municipios = sorted(df[col_municipio].dropna().unique())

# =======================================================================
# Radar comparativo (modal vs municipio). Opción A: mostrar con datos parciales
# =======================================================================
def gerar_radar_modal(df_all, modal, municipio=None):
    df_modal = df_all[df_all[col_modal] == modal].copy()
    if df_modal.empty:
        fig = go.Figure()
        fig.update_layout(title=f"⚠️ No hay datos para el modal {modal.title()}")
        return fig, "⚠️ No hay datos para este modal."

    # medias del modal (promedio sobre municipios que tengan datos)
    modal_mean = df_modal[kpis_base].mean(skipna=True).fillna(0)

    municipio_mean = None
    municipio_tiene_datos = False
    if municipio:
        df_mun = df_modal[df_modal[col_municipio] == municipio]
        if not df_mun.empty:
            # si hay al menos una fila, promediamos y verificamos NaNs
            municipio_mean = df_mun[kpis_base].mean(skipna=True)
            municipio_tiene_datos = not municipio_mean.isna().all()

    # Etiquetas para radar (más legibles)
    etiquetas = [
        "Diversificación Rec.",
        "% Combustible",
        "% Mano Obra Op",
        "% Mano Obra Adm",
        "% Depreciación",
        "% Desp. Adm",
    ]

    # Convertir a porcentaje para visualización (0-100)
    modal_vals_pct = (modal_mean * 100).tolist()
    if municipio_mean is not None:
        municipio_vals_pct = (municipio_mean * 100).tolist()
    else:
        municipio_vals_pct = None

    # Si modal tiene valores NaN totales, rellenar 0 (para no romper gráfica)
    modal_vals_pct = [0 if pd.isna(x) else x for x in modal_vals_pct]
    if municipio_vals_pct is not None:
        municipio_vals_pct = [0 if pd.isna(x) else x for x in municipio_vals_pct]

    # Crear figura radar
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=modal_vals_pct + [modal_vals_pct[0]],
        theta=etiquetas + [etiquetas[0]],
        fill="toself",
        name="Media del Modal",
        line_color="#1f77b4",
        opacity=0.6
    ))

    if municipio_vals_pct is not None and municipio_tiene_datos:
        fig.add_trace(go.Scatterpolar(
            r=municipio_vals_pct + [municipio_vals_pct[0]],
            theta=etiquetas + [etiquetas[0]],
            fill="toself",
            name=f"{municipio}",
            line_color="#ff7f0e",
            opacity=0.6
        ))

    fig.update_layout(
        title=f"⚙️ Perfil Comparativo de Costos – {modal.title()}",
        title_x=0.5,
        polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
        height=520,
        showlegend=True
    )

    # Interpretación automática (más cautelosa si faltan datos)
    interpretacion = []
    if municipio is None:
        interpretacion.append("Se muestra la media del modal. Seleccione un municipio para comparar.")
    else:
        if not municipio_tiene_datos:
            interpretacion.append(f"⚠️ El municipio '{municipio}' no tiene datos válidos para este modal.")
        else:
            # Si hay algún KPI faltante en el municipio, avisar
            df_mun = df_modal[df_modal[col_municipio] == municipio]
            faltantes_mun = df_mun[kpis_base].isna().any(axis=1).any()
            if faltantes_mun:
                interpretacion.append("⚠️ Datos incompletos para este municipio — interpretación limitada.")
            # Reglas por KPI (usando porcentajes)
            # Diversificación: mayor es mejor
            div = (municipio_mean["kpi_diversificacao_receitas"] * 100) if municipio_mean is not None else None
            div_modal = (modal_mean["kpi_diversificacao_receitas"] * 100)
            if div is None or pd.isna(div):
                interpretacion.append("Diversificación: sin dato.")
            else:
                if div == 0:
                    interpretacion.append("⚫ Diversificación = 0% — crítico (sin fuentes extratarifarias).")
                elif div < div_modal:
                    interpretacion.append("🔴 Diversificación por debajo de la media del modal.")
                elif div < 15:
                    interpretacion.append("🟡 Diversificación baja (pero por encima de la media).")
                else:
                    interpretacion.append("🟢 Buena diversificación de ingresos.")
            # Combustible: menor es mejor
            comb = (municipio_mean["kpi_pct_combustivel"] * 100) if municipio_mean is not None else None
            comb_modal = (modal_mean["kpi_pct_combustivel"] * 100)
            if comb is None or pd.isna(comb):
                interpretacion.append("Combustible: sin dato.")
            else:
                if comb > comb_modal:
                    interpretacion.append("🔴 Costo de combustible por encima de la media.")
                elif comb > 25:
                    interpretacion.append("🟡 Costo de combustible moderado (por encima de 25%).")
                else:
                    interpretacion.append("🟢 Costo de combustible eficiente.")
            # Mano de obra y demás: comparar con la media del modal
            for kpi_name, label in [
                ("kpi_pct_mao_obra_op", "M. obra operativa"),
                ("kpi_pct_mao_obra_adm", "M. obra administrativa"),
                ("kpi_pct_depreciacao", "Depreciación"),
                ("kpi_pct_desp_adm", "Despesas adm")
            ]:
                val = (municipio_mean[kpi_name] * 100) if municipio_mean is not None else None
                val_modal = (modal_mean[kpi_name] * 100)
                if val is None or pd.isna(val):
                    interpretacion.append(f"{label}: sin dato.")
                else:
                    if val > val_modal:
                        interpretacion.append(f"🔴 {label} por encima de la media.")
                    else:
                        interpretacion.append(f"🟢 {label} por debajo de la media (mejor).")

    return fig, "\n".join(interpretacion)

# =======================================================================
# Colores y categorías para treemap según tu confirmación
# NA -> negro (Sin datos)
# 0 -> rojo (Baja)
# baja -> rojo (<=40)
# media -> naranja (40-70)
# alta -> verde (>70)
# =======================================================================
def categoria_por_eficiencia(ef_pct, tiene_datos):
    if not tiene_datos:
        return "Sin datos"
    # si e es exactamente 0 -> baja
    if pd.isna(ef_pct):
        return "Sin datos"
    if ef_pct == 0:
        return "Baja"
    if ef_pct <= 40:
        return "Baja"
    if ef_pct <= 70:
        return "Media"
    return "Alta"

color_map = {
    "Sin datos": "black",
    "Baja": "red",
    "Media": "orange",
    "Alta": "green"
}

# =======================================================================
# Layout
# =======================================================================
app = dash.Dash(__name__)
app.title = "Dashboard de KPIs - Análisis y Eficiencia"

app.layout = html.Div([
    html.H1("📊 Análisis de KPIs y Eficiencia Operacional", style={'textAlign': 'center'}),
    html.Div([
        html.Div([
            html.Label("Modal:"),
            dcc.Dropdown(
                id="filtro_modal",
                options=[{"label": m.title(), "value": m} for m in modais],
                value=modais[0] if modais else None,
                clearable=False
            ),
        ], style={"width": "48%", "display": "inline-block"}),
        html.Div([
            html.Label("Municipio (opcional):"),
            dcc.Dropdown(
                id="filtro_municipio",
                options=[{"label": m, "value": m} for m in municipios],
                clearable=True,
                placeholder="Selecciona un municipio (opcional)"
            ),
        ], style={"width": "48%", "display": "inline-block"}),
    ], style={'textAlign': 'center'}),
    html.Hr(),

    dcc.Graph(id="grafico_qualidade"),
    dcc.Graph(id="grafico_eficiencia"),
    html.Div(id="interpretacao_texto", style={"padding": "18px", "fontSize": "15px"}),

    html.Hr(),
    html.Div(id="formula_texto", style={"padding": "10px"}),

    dcc.Graph(id="grafico_treemap"),
    html.Div(id="leyenda_eficiencia", style={"padding": "12px"})
])

# =======================================================================
# Callback principal
# =======================================================================
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
    # --- Mapa de completitud (todas las combinaciones registradas) ---
    df_qual = (
        df.groupby([col_modal, col_municipio])["completitud"]
        .mean()
        .reset_index()
    )
    fig_qual = px.density_heatmap(
        df_qual,
        x=col_modal,
        y=col_municipio,
        z="completitud",
        title="🧱 Mapa de Completitud de Datos (1 = 100%)",
        color_continuous_scale="RdYlGn",
    )
    fig_qual.update_layout(title_x=0.5, height=420)

    # --- Radar (modal vs municipio) ---
    fig_radar, interpretacion = gerar_radar_modal(df, modal_sel, municipio_sel)
    fig_radar.update_layout(height=520)

    # --- Cálculo de eficiencia para TODOS los municipios ---
    # 1) Dataframe completo de municipios (lista de 71 municipios)
    df_mun_list = pd.DataFrame({col_municipio: municipios})

    # 2) Calcular promedios por municipio para el modal seleccionado (solo donde haya filas)
    df_eff_real = (
        df[df[col_modal] == modal_sel]
        .groupby(col_municipio)[kpis_base]
        .mean()
        .reset_index()
    )

    # 3) Merge left para que salgan todos los municipios de la lista
    df_eff = df_mun_list.merge(df_eff_real, on=col_municipio, how="left")

    # 4) Clasificación completa / parcial / sin datos
    df_eff["num_validos"] = df_eff_real[kpis_base].count(axis=1).reindex(df_eff.index, fill_value=0).values

    df_eff["estado_kpis"] = df_eff["num_validos"].apply(
        lambda x: "sin" if x == 0 else ("completo" if x == len(kpis_base) else "incompleto")
    )

    # 5) Para cálculo, reemplazar NaN por 0 pero solo temporalmente
    df_eff_calc = df_eff[kpis_base].copy().fillna(0)

    # 6) Asegurar escala 0–1
    for col in kpis_base:
        if df_eff_calc[col].max() > 1:
            df_eff_calc[col] = df_eff_calc[col] / 100.0

    # 7) Fórmula eficiencia usando solo KPIs presentes
    df_eff["eficiencia_bruta"] = (
        1
       - df_eff["kpi_pct_combustivel"] 
       - df_eff["kpi_diversificacao_receitas"] ## 1 -receita_tarifaria/receita_total
       - (df_eff["kpi_pct_mao_obra_adm"] / 2.0)
       - (df_eff["kpi_pct_mao_obra_op"] / 2.0)
    )

    # 8) Convertir a 0–100
    df_eff["eficiencia_pct"] = df_eff["eficiencia_bruta"] * 100

    # 9) Casos especiales según estado_kpis
    # (3) Sin KPIs → marcar NaN (se convertirá luego a "SD")
    df_eff.loc[df_eff["estado_kpis"] == "sin", "eficiencia_pct"] = pd.NA

    # 10) Categoría de color según eficiencia y estado
    def categoria_final(row):
        if row["estado_kpis"] == "sin":
            return "Sin datos"
        if pd.isna(row["eficiencia_pct"]):
            return "Sin datos"
        if row["eficiencia_pct"] == 0:
            return "Baja"
        if row["eficiencia_pct"] <= 40:
            return "Baja"
        if row["eficiencia_pct"] <= 70:
            return "Media"
        return "Alta"

    df_eff["categoria"] = df_eff.apply(categoria_final, axis=1)

    # 11) Texto mostrado en el treemap
    def texto_celda(row):
        if row["estado_kpis"] == "sin":
            return "SD"
        val = row["eficiencia_pct"]
        if pd.isna(val):
            return "SD"
        txt = f"{float(val):.1f}%"
        if row["estado_kpis"] == "incompleto":
            txt += "*"   # caso (2)
        return txt

    df_eff["valor_text"] = df_eff.apply(texto_celda, axis=1)

    # 12) Ordenamiento
    df_eff = df_eff.sort_values("eficiencia_pct", ascending=False, na_position="last").reset_index(drop=True)

    # --- TREEMAP ---
    fig_treemap = px.treemap(
        df_eff,
        path=[col_municipio],
        values="eficiencia_pct",
        color="categoria",
        color_discrete_map={
            "Sin datos": "black",
            "Baja": "red",
            "Media": "orange",
            "Alta": "green"
        },
        title=f"🏆 Ranking de Eficiencia – {modal_sel.title()}",
    )

    # mostrar label + valor_text (usa customdata para el valor)
    fig_treemap.update_traces(
        texttemplate="%{label}<br>%{customdata[0]}",
        textposition="middle center",
        marker=dict(line=dict(color="white", width=1)),
        customdata=df_eff[["valor_text"]].values
    )
    fig_treemap.update_layout(title_x=0.5, height=860, margin=dict(t=80, l=20, r=20, b=20))

    # --- Leyenda y fórmula ---
    leyenda = html.Div([
        html.B("📘 Leyenda de interpretación:"),
        html.Br(),
        html.Span("⚫ Sin datos → El municipio no tiene registros para este modal", style={"color": "black"}),
        html.Br(),
        html.Span("🔴 0–40% → Eficiencia baja", style={"color": "red"}),
        html.Br(),
        html.Span("🟠 40–70% → Eficiencia media", style={"color": "orange"}),
        html.Br(),
        html.Span("🟢 >70% → Eficiencia alta", style={"color": "green"}),
    ], style={"fontSize": "14px"})

    formula = html.Pre(
        "Fórmula de Eficiencia (E):\n"
        "E_bruta = 1 - Combustible + Diversificación - (MãoObraAdm/2) - (MãoObraOp/2)\n"
        "E_pct = E_bruta * 50  -> escala 0–100%\n\n"
        "Nota: 'Sin datos' (color negro) indica municipios sin registros para el modal seleccionado.\n"
        "Municipios con datos parciales muestran su eficiencia calculada con los valores presentes; "
        "la completitud penaliza la interpretación y el radar mostrará advertencias si faltan KPIs."
    )

    # --- Interpretación de radar (texto) ---
    texto_interpretacion = interpretacion

    return fig_qual, fig_radar, texto_interpretacion, formula, fig_treemap, leyenda


# === 8. Ejecutar ===
if __name__ == "__main__":
    # usa app.run para compatibilidad con tu versión (dash 3.x)
    app.run(debug=True)
