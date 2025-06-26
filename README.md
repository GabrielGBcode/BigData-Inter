# Análise de Reclamações e Clusters de Funcionários do Banco Inter

Este projeto realiza a análise de relatos/reclamações de funcionários do Banco Inter, utilizando técnicas de processamento de linguagem natural, clustering e visualização de dados.

## Objetivo

- Extrair, agrupar e visualizar padrões de reclamações dos funcionários.
- Gerar clusters automáticos a partir de embeddings de texto.
- Visualizar os clusters com t-SNE.
- Gerar nuvens de palavras para cada cluster identificado.

## Estrutura do Projeto

```
BD_trabalho/
│
├── clusters/         # Arquivos de clusters gerados (cluster_0.xlsx, ...)
├── imagens/          # Imagens de visualização (ex: tsne_clusters.png)
├── nuvens/           # Nuvens de palavras por cluster (nuvem_cluster_0.png, ...)
├── data/             # Dados brutos/originais (avaliacoes_inter.parquet, avaliacoes_inter.xlsx)
├── processados/      # Dados processados (df_processado.pkl)
├── scripts/          # Scripts Python (processamento_clusters.py, nuvem_palavras.py)
├── requirements.txt  # Dependências do projeto
└── README.md         # Este arquivo
```

## Como usar

1. **Instale as dependências:**

   ```bash
   pip install -r requirements.txt
   ```

2. **Execute o processamento completo:**

   ```bash
   cd scripts
   python processamento_clusters.py
   ```

   Isso irá gerar os clusters, embeddings, visualizações e salvar o DataFrame processado em `../processados/df_processado.pkl`.

3. **Gere as nuvens de palavras:**
   ```bash
   python nuvem_palavras.py
   ```
   As imagens serão salvas em `../nuvens/`.

## Descrição dos principais arquivos

- **data/avaliacoes_inter.xlsx**: Fonte principal dos relatos dos funcionários.
- **data/relatos.csv**: (Opcional) Outra fonte de relatos, não utilizada diretamente.
- **processados/df_processado.pkl**: DataFrame processado, pronto para análises rápidas.
- **clusters/**: Arquivos Excel com os relatos agrupados por cluster.
- **imagens/tsne_clusters.png**: Visualização dos clusters em 2D usando t-SNE.
- **nuvens/**: Nuvens de palavras para cada cluster.
- **scripts/processamento_clusters.py**: Script principal de processamento e clustering.
- **scripts/nuvem_palavras.py**: Gera as nuvens de palavras a partir do DataFrame processado.

## Observações

- Para alterar o cluster exibido na nuvem de palavras, edite o script ou rode para todos (já configurado).
- O arquivo `df_processado.pkl` pode ser recriado a qualquer momento rodando o processamento completo.

---

**Dúvidas ou sugestões?** Sinta-se à vontade para adaptar este projeto conforme sua necessidade!
