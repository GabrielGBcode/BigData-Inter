import pandas as pd
import matplotlib.pyplot as plt
from wordcloud import WordCloud, STOPWORDS
import nltk
from nltk.corpus import stopwords
import string
import os

# Baixar stopwords se necessário
nltk.download('stopwords')

# Carregar o DataFrame já processado
try:
    df = pd.read_pickle("processados/df_processado.pkl")
except FileNotFoundError:
    print("Arquivo processados/df_processado.pkl não encontrado. Execute o processamento completo primeiro.")
    exit(1)

# Stopwords em português
stopwords_pt = set(stopwords.words('portuguese'))
stopwords_extra = set([
    'empresa', 'funcionários', 'colaboradores', 'trabalho', 'banco',
    'inter', 'pode', 'mesmo', 'ainda', 'ser', 'pra', 'tem', 'nao', 'não'
])
stopwords_completas = STOPWORDS.union(stopwords_pt).union(stopwords_extra)

# Gera e salva a nuvem de palavras para cada cluster
clusters_unicos = sorted(df['cluster'].unique())

for cluster in clusters_unicos:
    txt_cluster = df[df['cluster'] == cluster]['contras'].dropna().str.cat(sep=' ')
    texto_limpo = txt_cluster.translate(str.maketrans('', '', string.punctuation)).lower()
    wordcloud = WordCloud(
        stopwords=stopwords_completas,
        background_color='white',
        width=1200,
        height=800,
        colormap='inferno'
    ).generate(texto_limpo)
    plt.figure(figsize=(15, 10))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.title(f'Nuvem de Palavras - Reclamações dos Funcionários (Cluster {cluster})', fontsize=20)
    # Garante que a pasta 'nuvens' existe
    os.makedirs('nuvens', exist_ok=True)
    nome_arquivo = f'nuvens/nuvem_cluster_{cluster}.png'
    plt.savefig(nome_arquivo, bbox_inches='tight')
    plt.close()
    print(f'Nuvem de palavras do cluster {cluster} salva como {nome_arquivo}') 