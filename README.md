# Análise de Reclamações e Clusters de Funcionários do Banco Inter

Este projeto realiza a análise de relatos/reclamações de funcionários do Banco Inter, utilizando técnicas de processamento de linguagem natural, clustering, análise temporal e geração automática de resumos temáticos.

## Objetivo

- Extrair, agrupar e visualizar padrões de reclamações dos funcionários.
- Gerar clusters automáticos a partir de embeddings de texto.
- Visualizar os clusters com t-SNE.
- Gerar nuvens de palavras para cada cluster identificado.
- Analisar a evolução temporal das reclamações por cluster.
- Gerar resumos automáticos temáticos para cada cluster usando IA (OpenAI ou Ollama/OpenChat).

## Estrutura do Projeto

```
BD_trabalho/
│
├── clusters/         # Arquivos de clusters gerados (cluster_0.xlsx, ...)
├── imagens/          # Imagens de visualização (ex: tsne_clusters.png, grafico_cotovelo.png)
├── imagens_temporais_clusters/ # Gráficos temporais de cada cluster
├── nuvens/           # Nuvens de palavras por cluster (nuvem_cluster_0.png, ...)
├── resumos_clusters/ # Resumos automáticos dos clusters (OpenAI ou Ollama)
├── data/             # Dados brutos/originais (avaliacoes_inter.parquet, avaliacoes_inter.xlsx)
├── processados/      # Dados processados (df_processado.pkl)
├── scripts/          # Scripts Python (ver abaixo)
├── requirements.txt  # Dependências do projeto
└── README.md         # Este arquivo
```

## Principais Scripts

- `app.py`: Orquestra todo o pipeline automaticamente.
- `scripts/glassdoor_scraper.py`: Coleta avaliações do Glassdoor (com data de publicação).
- `scripts/parquet_para_xlsx.py`: Converte dados Parquet para Excel.
- `scripts/processamento_clusters.py`: Processa, gera embeddings, faz clustering e salva clusters.
- `scripts/nuvem_palavras.py`: Gera nuvens de palavras para cada cluster.
- `scripts/metodo_cotovelo.py`: Gera gráfico do método do cotovelo para escolha de k.
- `scripts/analise_temporal_clusters.py`: Gera gráficos de evolução temporal de cada cluster (um gráfico por cluster, salvos em `imagens_temporais_clusters/`).
- `scripts/resumo_clusters.py`: Gera resumos automáticos para cada cluster usando OpenAI (ou adapte para Ollama/OpenChat).

## Como usar

### 1. Instale as dependências

```bash
pip install -r requirements.txt
```

### 2. Configure o arquivo `.env`

Crie um arquivo `.env` dentro da pasta `scripts/` com:

```
EMAIL=seu@email.com
SENHA=suaSenhaAqui
```

Se algum dos campos estiver vazio, o sistema irá solicitar manualmente o email e senha na interface gráfica.

> **Importante:** Nunca versionar o `.env`! Adicione `scripts/.env` ao `.gitignore` se necessário.

### 3. Coleta de localização e análise regional

- O scraper coleta automaticamente a localização (cidade, UF) de cada avaliação, ignorando avaliações sem localização válida.
- A análise regional por cluster é feita automaticamente, gerando gráficos de incidência por cidade/estado para cada cluster.
- Os gráficos são salvos em `imagens/` com o nome `reclamacoes_cluster_X_por_regiao.png`.

### 3. Execute o pipeline completo

```bash
python app.py
```

Isso irá:

- Garantir os modelos do Ollama necessários (bge-m3, llama3, openchat, etc)
- Coletar dados do Glassdoor
- Processar e clusterizar os dados
- Gerar nuvens de palavras
- Gerar gráfico do cotovelo
- Gerar análise temporal dos clusters (um gráfico por cluster)
- Gerar resumos automáticos dos clusters

### 4. Rodar scripts individuais

Você pode rodar qualquer script separadamente, por exemplo:

```bash
python scripts/analise_temporal_clusters.py
python scripts/resumo_clusters.py
```

## Dependências e requisitos

- Python 3.10+
- [Ollama](https://ollama.com/) (para embeddings e modelos locais, se desejar)
- Conta OpenAI (para resumos automáticos via GPT-4/3.5, se desejar)
- Modelos necessários no Ollama: `bge-m3`, `llama3` ou `openchat` (dependendo do fluxo)
- Pacotes Python: ver `requirements.txt`

## Observações importantes

- O arquivo `.env**não deve ser versionado**. Adicione `\*\*/.env`ao`.gitignore`.
- O script de scraping pode exigir login manual e resolução de reCAPTCHA.
- O pipeline foi testado em Windows, mas funciona em Linux/macOS (ajuste caminhos se necessário).
- Os gráficos e resumos são salvos automaticamente nas pastas correspondentes.
- O script de resumo pode ser adaptado para usar OpenAI, Ollama ou outro modelo local.
- O número de textos enviados para o modelo é limitado por tokens (ver configuração no script de resumo).

## Como contribuir

- Sinta-se à vontade para abrir issues ou PRs para melhorias!

---

Se tiver dúvidas ou quiser adaptar para outro fluxo/modelo, basta pedir!
