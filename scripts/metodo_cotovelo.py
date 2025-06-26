import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
import warnings
warnings.filterwarnings('ignore')

# Configurar matplotlib para português
plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['axes.unicode_minus'] = False

def gerar_grafico_cotovelo():
    """
    Gera o gráfico do método do cotovelo para determinar o número ideal de clusters
    """
    print("Carregando DataFrame processado...")
    
    # Carregar o DataFrame processado
    df = pd.read_pickle("processados/df_processado.pkl")
    
    # Converter os embeddings em matriz numpy
    embeddings_matrix = np.vstack(df['embeddings'].values)
    
    print(f"Shape dos embeddings: {embeddings_matrix.shape}")
    print(f"Número de comentários: {len(df)}")
    
    # Definir range de valores de k para testar
    k_range = range(1, 11)
    
    # Listas para armazenar métricas
    inertia = []
    silhouette_scores = []
    
    print("Calculando métricas para diferentes valores de k...")
    
    # Calcular inércia e silhueta para cada valor de k
    for k in k_range:
        print(f"Processando k = {k}...")
        
        # K-Means
        kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
        kmeans.fit(embeddings_matrix)
        
        # Inércia (soma das distâncias intra-cluster)
        inertia.append(kmeans.inertia_)
        
        # Silhueta (apenas para k >= 2)
        if k >= 2:
            silhouette_scores.append(silhouette_score(embeddings_matrix, kmeans.labels_))
        else:
            silhouette_scores.append(0)
    
    # Criar figura com dois subplots
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    
    # Gráfico 1: Método do Cotovelo (Inércia)
    ax1.plot(k_range, inertia, 'bo-', linewidth=2, markersize=8)
    ax1.set_xlabel('Número de Clusters (k)', fontsize=12)
    ax1.set_ylabel('Inércia', fontsize=12)
    ax1.set_title('Método do Cotovelo', fontsize=14, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    ax1.set_xticks(k_range)
    
    # Adicionar valores nos pontos
    for i, (k, iner) in enumerate(zip(k_range, inertia)):
        ax1.annotate(f'{iner:.0f}', (k, iner), textcoords="offset points", 
                    xytext=(0,10), ha='center', fontsize=9)
    
    # Gráfico 2: Método da Silhueta
    ax2.plot(k_range, silhouette_scores, 'ro-', linewidth=2, markersize=8)
    ax2.set_xlabel('Número de Clusters (k)', fontsize=12)
    ax2.set_ylabel('Score da Silhueta', fontsize=12)
    ax2.set_title('Método da Silhueta', fontsize=14, fontweight='bold')
    ax2.grid(True, alpha=0.3)
    ax2.set_xticks(k_range)
    
    # Adicionar valores nos pontos
    for i, (k, sil) in enumerate(zip(k_range, silhouette_scores)):
        if k >= 2:  # Apenas para valores válidos de silhueta
            ax2.annotate(f'{sil:.3f}', (k, sil), textcoords="offset points", 
                        xytext=(0,10), ha='center', fontsize=9)
    
    # Encontrar o melhor k pelo método da silhueta
    best_k_silhouette = k_range[np.argmax(silhouette_scores)]
    
    # Encontrar o cotovelo (ponto onde a redução da inércia diminui significativamente)
    # Calcular a segunda derivada da inércia
    inertia_diff = np.diff(inertia)
    inertia_diff2 = np.diff(inertia_diff)
    elbow_k = k_range[np.argmin(inertia_diff2) + 2]  # +2 porque perdemos 2 pontos nas diferenças
    
    # Destacar os pontos ótimos
    ax1.axvline(x=elbow_k, color='red', linestyle='--', alpha=0.7, 
                label=f'Cotovelo sugerido: k={elbow_k}')
    ax2.axvline(x=best_k_silhouette, color='blue', linestyle='--', alpha=0.7,
                label=f'Melhor silhueta: k={best_k_silhouette}')
    
    ax1.legend()
    ax2.legend()
    
    plt.tight_layout()
    
    # Salvar o gráfico
    plt.savefig('imagens/grafico_cotovelo.png', dpi=300, bbox_inches='tight')
    print("Gráfico salvo como 'imagens/grafico_cotovelo.png'")
    
    # Mostrar o gráfico
    plt.show()
    
    # Imprimir resultados
    print("\n" + "="*50)
    print("RESULTADOS DO MÉTODO DO COTOVELO")
    print("="*50)
    print(f"Número de comentários analisados: {len(df)}")
    print(f"Dimensão dos embeddings: {embeddings_matrix.shape[1]}")
    print("\nMétricas por valor de k:")
    print("-" * 40)
    print("k\tInércia\t\tSilhueta")
    print("-" * 40)
    
    for k, iner, sil in zip(k_range, inertia, silhouette_scores):
        if k == 1:
            print(f"{k}\t{iner:.0f}\t\t-")
        else:
            print(f"{k}\t{iner:.0f}\t\t{sil:.3f}")
    
    print("\n" + "="*50)
    print(f"Melhor k pelo método da silhueta: {best_k_silhouette}")
    print(f"K sugerido pelo método do cotovelo: {elbow_k}")
    print("="*50)
    
    return {
        'k_range': list(k_range),
        'inertia': inertia,
        'silhouette_scores': silhouette_scores,
        'best_k_silhouette': best_k_silhouette,
        'elbow_k': elbow_k
    }

if __name__ == "__main__":
    # Verificar se o diretório de imagens existe
    import os
    if not os.path.exists('imagens'):
        os.makedirs('imagens')
        print("Diretório 'imagens' criado.")
    
    # Gerar o gráfico
    resultados = gerar_grafico_cotovelo() 