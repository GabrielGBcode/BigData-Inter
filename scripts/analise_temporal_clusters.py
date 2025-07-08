import pandas as pd
import matplotlib.pyplot as plt
import os
from sklearn.preprocessing import LabelEncoder

# Carregue o DataFrame processado
df = pd.read_pickle("processados/df_processado.pkl")

# Converta a coluna de data para datetime
# Exemplo: '3 de jul. de 2025' -> '%d de %b. de %Y'
df['data'] = pd.to_datetime(df['data'], errors='coerce', format='%d de %b. de %Y')

# Crie uma coluna de trimestre
# Exemplo: '2025Q3' para o terceiro trimestre de 2025
# Agrupa de 3 em 3 meses

df['trimestre'] = df['data'].dt.to_period('Q')

# Conta o total de reclamações por trimestre (para porcentagem)
total_tri = df.groupby(['trimestre']).size().reset_index(name='total')

# Descobre o maior total de reclamações em qualquer trimestre
max_total = total_tri['total'].max()

# Junta as duas tabelas para calcular a porcentagem
# Agora a porcentagem é em relação ao maior total de qualquer trimestre
freq_tri = df.groupby(['cluster', 'trimestre']).size().reset_index(name='frequencia')
df_merged = pd.merge(freq_tri, total_tri, on='trimestre')
df_merged['porcentagem'] = 100 * df_merged['frequencia'] / max_total

# Crie a pasta para salvar os gráficos, se não existir
dir_out = 'imagens_temporais_clusters'
os.makedirs(dir_out, exist_ok=True)

# Definir o mapa de cores igual ao t-SNE
cmap = plt.get_cmap('tab10')
le = LabelEncoder()
le.fit(df['cluster'])
n = len(le.classes_)

# Gere e salve um gráfico de linha temporal para cada cluster
for cluster in sorted(df['cluster'].unique()):
    dados = df_merged[df_merged['cluster'] == cluster]
    plt.figure(figsize=(10, 5))
    cor = cmap(le.transform([cluster])[0] / n)
    plt.plot(dados['trimestre'].astype(str), dados['porcentagem'], marker='o', label=f'Cluster {cluster}', color=cor)
    plt.xlabel('Trimestre')
    plt.ylabel('% de Reclamações no Trimestre')
    plt.title(f'Incidência Percentual Trimestral - Cluster {cluster}')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.legend()
    nome_arquivo = os.path.join(dir_out, f'cluster_{cluster}.png')
    plt.savefig(nome_arquivo, bbox_inches='tight')
    plt.close()
    print(f'Gráfico percentual trimestral do cluster {cluster} salvo em {nome_arquivo}') 