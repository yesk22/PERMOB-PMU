import pandas as pd
import re

# === 1. Leer archivo ===
arquivo = r"..\..\..\data\raw\pemob_municipal_2024.xlsx"
df = pd.read_excel(arquivo, sheet_name="pemob24")
df.columns = df.columns.str.strip()
df.columns = df.columns.str.replace('\n', ' ', regex=True)
df.columns = df.columns.str.replace('\xa0', ' ', regex=True)
df.columns = df.columns.str.lower()

col_identificacao = ["código", "uf", "município"]
col_identificacao = [c for c in col_identificacao if c in df.columns]  # solo las que existan

# === 2. Normalización de nombres ===
mapa_modais = {
    "bicicletas compartilhadas": "Bicicletas compartilhadas",
    "metrô": "Metrô",
    "nenhum": "Nenhum",
    "ônibus": "Ônibus",
    "táxi": "Táxi",
    "trem": "Trem",
    "vlt": "VLT",
    "vans/microônibus": "Vans/Microônibus"
}

# === 3. Definición de columnas base (modelo ÔNIBUS) ===
col_receita_tarifaria_base = "qual o valor da receita tarifária anual por ônibus arrecadado em 2023?"
col_receitas_extratarifarias_base = [
    "se houver receita extratarifária, qual o valor de subsídio associado a passageiros com benefícios tarifários utilizado no sistema por ônibus em 2023?",
    "se houver receita extratarifária, qual o valor arrecadado com subsídio direto ao sistema (subvenção) no sistema por ônibus em 2023?",
    "se houver receita extratarifária, qual o valor arrecadado com publicidade em abrigos, terminais e veículos no sistema por ônibus em 2023?",
    "se houver receita extratarifária, qual o valor arrecadado com outras fontes de recursos no sistema por ônibus em 2023?"
]
col_custos_base = {
    "combustivel": "combustíveis dizem respeito a qual percentual da planilha de custos do serviço por ônibus?",
    "mao_obra_op": "mão de obra 1 (operação) diz respeito a qual percentual da planilha de custos do serviço por ônibus?",
    "mao_obra_adm": "mão de obra 2 (administrativo) diz respeito a qual percentual da planilha de custos do serviço por ônibus?",
    "depreciacao": "depreciação de veículos diz respeito a qual percentual da planilha de custos do serviço por ônibus?",
    "desp_adm": "despesas administrativas dizem respeito a qual percentual da planilha de custos do serviço por ônibus?"
}

# === 4. Función para construir nombres de columnas según modal ===
def construir_cols_para_modal(modal_nome: str):
    termo = modal_nome.lower()
    receita_tarifaria = re.sub("ônibus", termo, col_receita_tarifaria_base)
    receitas_extratarifarias = [re.sub("ônibus", termo, c) for c in col_receitas_extratarifarias_base]
    custos = {k: re.sub("ônibus", termo, c) for k, c in col_custos_base.items()}
    return receita_tarifaria, receitas_extratarifarias, custos

# === 5. Calcular KPIs por modal ===
resultados = []

for modal in mapa_modais.keys():
    print(f"\n=== Calculando KPIs para: {modal.upper()} ===")

    col_receita_tarifaria, col_receitas_extratarifarias, col_custos = construir_cols_para_modal(modal)

    # Verificar si existen las columnas en el archivo
    cols_existentes = [c for c in [col_receita_tarifaria] + col_receitas_extratarifarias + list(col_custos.values()) if c in df.columns]
    if not cols_existentes:
        print(f"⚠️  No se encontraron columnas para {modal}, se omite.")
        continue

    # Filtrar solo columnas existentes
    todas_cols = cols_existentes
    df_temp = df.copy()
    df_temp[todas_cols] = df_temp[todas_cols].apply(pd.to_numeric, errors="coerce")

    # === KPIs ===
    df_temp["receita_extratarifaria_total"] = df_temp.reindex(columns=[c for c in col_receitas_extratarifarias if c in df_temp.columns]).sum(axis=1, skipna=True)
    #df_temp["receita_total"] = df_temp.get(col_receita_tarifaria, 0).fillna(0) + df_temp["receita_extratarifaria_total"].fillna(0)

    df_temp["receita_total"] = (
        df_temp[col_receita_tarifaria].fillna(0) if col_receita_tarifaria in df_temp.columns
        else 0
    ) + df_temp["receita_extratarifaria_total"].fillna(0)




    df_temp[f"kpi_diversificacao_receitas_{modal}"] = df_temp.apply(
        lambda x: 1 - (x.get(col_receita_tarifaria, 0) / x["receita_total"]) if x["receita_total"] > 0 else None, axis=1
    )

    for nome, col in col_custos.items():
        if col in df_temp.columns:
            df_temp[f"kpi_pct_{nome}_{modal}"] = df_temp[col] / 100

    # Guardar solo columnas KPI
    cols_saida = [c for c in df_temp.columns if f"_{modal}" in c]
    # resultados.append(df_temp[cols_saida])

    df_modal_saida = pd.concat([df_temp[col_identificacao], df_temp[cols_saida]], axis=1)

    # Exportar cada modal
    #df_temp[cols_saida].to_excel(f"kpis_custos_{modal}.xlsx", index=False)
    #print(f"✅ KPIs exportados: kpis_custos_{modal}.xlsx")

    modal_safe = re.sub(r'[^a-zA-Z0-9_-]', '_', modal.lower())
    df_modal_saida.to_excel(f"kpis_custos_{modal_safe}.xlsx", index=False)
    print(f"✅ KPIs exportados: kpis_custos_{modal_safe}.xlsx")

    resultados.append(df_modal_saida)

# === 6. Consolidar todos los modales (opcional) ===
if resultados:
    df_consolidado = pd.concat(resultados, axis=0)
    df_consolidado.to_excel("kpis_custos_todos_modais.xlsx", index=False)
    print("📊 Archivo consolidado generado: kpis_custos_todos_modais.xlsx")
