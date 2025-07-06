import pandas as pd
import matplotlib.pyplot as plt
import os

# Carregue o DataFrame processado
df = pd.read_pickle("processados/df_processado.pkl")

# Converta a coluna de data para datetime
# Exemplo: '3 de jul. de 2025' -> '%d de %b. de %Y'
df['data'] = pd.to_datetime(df['data'], errors='coerce', format='%d de %b. de %Y')

# Crie uma coluna de período (ex: mês)
df['mes'] = df['data'].dt.to_period('M')

# Conte a frequência de reclamações por cluster e mês
freq = df.groupby(['cluster', 'mes']).size().reset_index(name='frequencia')

# Crie a pasta para salvar os gráficos, se não existir
dir_out = 'imagens_temporais_clusters'
os.makedirs(dir_out, exist_ok=True)

# Gere e salve um gráfico para cada cluster
for cluster in sorted(df['cluster'].unique()):
    dados = freq[freq['cluster'] == cluster]
    plt.figure(figsize=(10, 5))
    plt.plot(dados['mes'].astype(str), dados['frequencia'], marker='o', label=f'Cluster {cluster}')
    plt.xlabel('Mês')
    plt.ylabel('Nº de Reclamações')
    plt.title(f'Evolução das Reclamações - Cluster {cluster}')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.legend()
    nome_arquivo = os.path.join(dir_out, f'cluster_{cluster}.png')
    plt.savefig(nome_arquivo, bbox_inches='tight')
    plt.close()
    print(f'Gráfico temporal do cluster {cluster} salvo em {nome_arquivo}') 