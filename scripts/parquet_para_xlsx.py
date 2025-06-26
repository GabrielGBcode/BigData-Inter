import pandas as pd
import os

# Caminhos dos arquivos
parquet_path = os.path.join('data', 'avaliacoes_inter.parquet')
xlsx_path = os.path.join('data', 'avaliacoes_inter.xlsx')

# Ler o arquivo Parquet
print(f"Lendo arquivo Parquet: {parquet_path}")
df = pd.read_parquet(parquet_path)

# Salvar como Excel
print(f"Salvando como Excel: {xlsx_path}")
df.to_excel(xlsx_path, index=False)
print("Conversão concluída com sucesso!") 