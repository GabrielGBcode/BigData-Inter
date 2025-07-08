import pandas as pd
import matplotlib.pyplot as plt
import os
import unidecode

# Carrega o DataFrame processado
caminho_df = os.path.join('processados', 'df_processado.pkl')
df = pd.read_pickle(caminho_df)

# Padroniza o formato da localização para 'Cidade - UF'
df['localizacao'] = df['localizacao'].astype(str).str.strip().str.title().str.replace(',', ' -')

# Garante que a coluna de localização existe
def check_colunas(df):
    if 'localizacao' not in df.columns:
        raise ValueError('Coluna "localizacao" não encontrada no DataFrame!')
    if 'cluster' not in df.columns:
        raise ValueError('Coluna "cluster" não encontrada no DataFrame!')
check_colunas(df)

# Cria pasta para os gráficos
os.makedirs('imagens', exist_ok=True)

# Para cada cluster, faz a análise regional
todos_clusters = sorted(df['cluster'].unique())
for cluster in todos_clusters:
    df_cluster = df[df['cluster'] == cluster]
    incidencias = df_cluster.groupby('localizacao').size().sort_values(ascending=False)
    print(f"\nRegiões com mais reclamações no cluster {cluster}:")
    print(incidencias.head(10))
    # Gera gráfico
    plt.figure(figsize=(10,6))
    incidencias.plot(kind='bar', color='orange')
    plt.title(f"Reclamações do Cluster {cluster} por Região")
    plt.xlabel('Região')
    plt.ylabel('Quantidade de Reclamações')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    nome_arquivo = os.path.join('imagens', f'reclamacoes_cluster_{cluster}_por_regiao.png')
    plt.savefig(nome_arquivo, bbox_inches='tight')
    plt.close()
    print(f"Gráfico salvo em: {nome_arquivo}") 