#!/usr/bin/env python3
import argparse
import pandas as pd
from pathlib import Path

def main():
    p = argparse.ArgumentParser(description='Carrega e resume a planilha PERMOB 2024.')
    p.add_argument('--input', required=True, help='Caminho do arquivo .xlsx (PERMOB 2024)')
    p.add_argument('--summary', required=False, default='reports/permob_resumo.md', help='Arquivo de saída (MD)')
    args = p.parse_args()

    xlsx = Path(args.input)
    if not xlsx.exists():
        raise SystemExit(f'Arquivo não encontrado: {xlsx}')

    xl = pd.ExcelFile(xlsx)
    sheets = xl.sheet_names

    lines = [f'# Resumo PERMOB 2024\n', f'- Arquivo: {xlsx.name}', f'- Abas: {", ".join(sheets)}\n']
    for sh in sheets:
        try:
            df = xl.parse(sh)
            lines.append(f'## Aba: {sh}')
            lines.append(f'- Linhas: {len(df):,}  Colunas: {len(df.columns):,}')
            head = df.head(5).to_markdown(index=False)
            lines.append('### Amostra (5 linhas)')
            lines.append(head + '\n')
        except Exception as e:
            lines.append(f'## Aba: {sh} — erro ao ler: {e}\n')

    out = Path(args.summary)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines), encoding='utf-8')
    print(f'✅ Resumo gerado em {out}')

if __name__ == '__main__':
    main()
