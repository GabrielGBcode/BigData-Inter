import pandas as pd
from tqdm import tqdm
from unidecode import unidecode
import ollama
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import chromadb.utils.embedding_functions as embedding_functions
import ast
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
from sklearn.metrics import silhouette_score
from sklearn.manifold import TSNE
from sklearn.preprocessing import LabelEncoder
import matplotlib.pyplot as plt
from sklearn.manifold import TSNE
from sklearn.preprocessing import LabelEncoder  # <- esta linha corrige o erro


# Carregar o arquivo Excel com os relatos
df = pd.read_excel("data/avaliacoes_inter.xlsx")

# Instanciando o objeto de Embedding da API Ollama
ollama_ef = embedding_functions.OllamaEmbeddingFunction(
    url="http://127.0.0.1:11434/api/embeddings",
    model_name="bge-m3",
)

# Verificar se a string contém '| CONTRAS:'
df[['pros', 'contras']] = df['avaliacao'].apply(
    lambda x: pd.Series(x.split('| CONTRAS:')) if '| CONTRAS:' in x else pd.Series([x, None])
)

# Limpar os prefixos
df['pros'] = df['pros'].str.replace('PRÓS:', '', regex=False).str.strip()
df['contras'] = df['contras'].str.strip()

# Defina o tamanho do lote (número de textos a serem processados por vez)
batch_size = 1

# Inicialize uma lista para armazenar todos os embeddings
all_embeddings = []

# Itere sobre o DataFrame em lotes
for i in tqdm(range(0, len(df), batch_size)):
    # Extrai os textos da coluna 'descricao_justificativa' no DataFrame
    batch_texts = df['contras'][i:i+batch_size].to_list()
    
    # Tente chamar o objeto diretamente para gerar os embeddings
    try:
        embeddings = ollama_ef(batch_texts)  # Chama o objeto para gerar os embeddings
        all_embeddings.extend(embeddings)  # Adiciona os embeddings à lista
    except Exception as e:
        print(f"Erro ao processar o lote {i}: {e}")
        continue

# Adiciona os embeddings ao DataFrame
df['embeddings'] = all_embeddings

# Converter os embeddings da coluna 'embeddings' em uma matriz numpy
embeddings_matrix = np.vstack(df['embeddings'].values)
#########################



# Determinar o número ideal de clusters usando o método do cotovelo e a silhueta
inertia = []
silhouette_scores = []
k_range = range(2, 11)

for k in k_range:
    kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
    kmeans.fit(embeddings_matrix)
    inertia.append(kmeans.inertia_)
    silhouette_scores.append(silhouette_score(embeddings_matrix, kmeans.labels_))

# Encontrar o número ideal de clusters pelo método da silhueta
optimal_k = k_range[np.argmax(silhouette_scores)]

optimal_k=7
#######################################################


kmeans = KMeans(n_clusters=optimal_k, random_state=42, n_init=10)
df["cluster"] = kmeans.fit_predict(embeddings_matrix)

#######################################################


# Reduz dimensionalidade para 2D com t-SNE
tsne = TSNE(n_components=2, random_state=42)
reduced_embeddings = tsne.fit_transform(embeddings_matrix)

# Supondo que df["cluster"] contém strings como "Grupo A", "Grupo B", etc.
le = LabelEncoder()
df["cluster_encoded"] = le.fit_transform(df["cluster"])  # converte string para número

# Adiciona coordenadas t-SNE
df["tsne_1"] = reduced_embeddings[:, 0]
df["tsne_2"] = reduced_embeddings[:, 1]

# Cria o gráfico de dispersão
plt.figure(figsize=(10, 6))
scatter = plt.scatter(
    df["tsne_1"],
    df["tsne_2"],
    c=df["cluster_encoded"],
    cmap="tab10",
    alpha=0.7,
    edgecolors="k"
)

# Legenda com os nomes originais dos clusters
handles = []
for i, label in enumerate(le.classes_):
    handles.append(plt.Line2D([], [], marker='o', color='w',
                              markerfacecolor=plt.cm.tab10(i / len(le.classes_)),
                              markeredgecolor='k', label=label, markersize=10))

plt.legend(handles=handles, title="Clusters")
plt.title("Visualização dos Clusters com t-SNE")
plt.xlabel("t-SNE 1")
plt.ylabel("t-SNE 2")
plt.grid(True)
plt.tight_layout()
plt.show()
#######################


df_marrom=df[df['cluster']==5]
df_zero=df[df['cluster']==0]
df_um=df[df['cluster']==1]
df_dois=df[df['cluster']==2]
df_tres=df[df['cluster']==3]
df_quatro=df[df['cluster']==4]
df_seis=df[df['cluster']==6]


df['cluster'].value_counts()



import matplotlib.pyplot as plt
from wordcloud import WordCloud, STOPWORDS
import nltk
from nltk.corpus import stopwords
import string

# Certifique-se de baixar os stopwords
nltk.download('stopwords')

# Texto com as reclamações (cole aqui ou leia de um arquivo)

texto = df_marrom['contras'].str.cat(sep=' ')

texto = df_seis['contras'].str.cat(sep=' ')

texto = df_quatro['contras'].str.cat(sep=' ')

texto = df_tres['contras'].str.cat(sep=' ')

texto = df_dois['contras'].str.cat(sep=' ')

# Stopwords em português
stopwords_pt = set(stopwords.words('portuguese'))

# Adiciona palavras extras que você quiser ignorar
stopwords_extra = set([
    'empresa', 'funcionários', 'colaboradores', 'trabalho', 'banco',
    'inter', 'pode', 'mesmo', 'ainda', 'ser', 'pra', 'tem', 'nao', 'não'
])
stopwords_completas = STOPWORDS.union(stopwords_pt).union(stopwords_extra)

# Remove pontuação e transforma tudo em minúsculo
texto_limpo = texto.translate(str.maketrans('', '', string.punctuation)).lower()

# Gera a nuvem de palavras
wordcloud = WordCloud(
    stopwords=stopwords_completas,
    background_color='white',
    width=1200,
    height=800,
    colormap='inferno'
).generate(texto_limpo)

# Exibe
plt.figure(figsize=(15, 10))
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis('off')
plt.title('Nuvem de Palavras - Reclamações dos Funcionários', fontsize=20)
plt.show()

# Salva o DataFrame processado para uso futuro
print('Salvando DataFrame processado em processados/df_processado.pkl...')
df.to_pickle("processados/df_processado.pkl")
print('Arquivo processados/df_processado.pkl salvo com sucesso!')

