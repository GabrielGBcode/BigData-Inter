import pandas as pd
import os
import time
import requests
from dotenv import load_dotenv
from pathlib import Path

# ======= CONFIGURAÇÕES =======
OLLAMA_URL = "http://localhost:11434/api/chat"
OLLAMA_MODEL = "gemma3:12b"
MAX_TENTATIVAS = 3
CAMINHO_DF = "processados/df_processado.pkl"
PASTA_SAIDA = 'resumos_clusters'
MAX_TEXTOS_CLUSTER = 20  # Limite de textos enviados por cluster

# ======= CARREGAR .env =======
dotenv_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path)

# Força uso de GPU ou CPU conforme variável de ambiente ou .env
OLLAMA_USE_GPU = os.getenv('OLLAMA_USE_GPU', '1')  # Padrão: usar GPU
os.environ['OLLAMA_USE_GPU'] = OLLAMA_USE_GPU

# ======= FUNÇÕES =======
def gerar_prompt(cluster_id: int, textos: list[str]) -> str:
    prompt_inicial = (
        "Analise o grupo de reclamações abaixo e gere um resumo OBRIGATORIAMENTE neste formato:\n\n"
        "**Título do Cluster**: ...\n"
        "**Palavras-Chave Frequentes**: ...\n"
        "**Tópicos Principais:**\n"
        "- ...\n"
        "- ...\n"
        "- ...\n\n"
        "Textos:\n"
    )
    # Limita o número de textos enviados para clusters grandes
    textos = textos[:MAX_TEXTOS_CLUSTER]
    return prompt_inicial + "\n".join(textos)

def resposta_esta_no_formato(resumo: str) -> bool:
    resumo = resumo.lower()
    return (
        "título do cluster" in resumo and
        ("palavras-chave" in resumo or "palavras chave" in resumo) and
        "tópicos principais" in resumo
    )

def reformatar_resposta(resumo: str) -> str:
    # Tenta reformatar respostas quase corretas para o padrão desejado
    linhas = resumo.splitlines()
    novo = []
    encontrou_titulo = False
    encontrou_palavras = False
    encontrou_topicos = False
    for linha in linhas:
        l = linha.strip().lower()
        if not encontrou_titulo and ("título do cluster" in l or "titulo do cluster" in l):
            novo.append("**Título do Cluster**: " + linha.split(":",1)[-1].strip())
            encontrou_titulo = True
        elif not encontrou_palavras and ("palavras-chave" in l or "palavras chave" in l):
            novo.append("**Palavras-Chave Frequentes**: " + linha.split(":",1)[-1].strip())
            encontrou_palavras = True
        elif not encontrou_topicos and ("tópicos principais" in l or "topicos principais" in l):
            novo.append("**Tópicos Principais:**")
            encontrou_topicos = True
        elif encontrou_topicos and linha.strip().startswith("-"):
            novo.append(linha)
        elif encontrou_topicos and linha.strip() and not linha.strip().startswith("-"):
            novo.append("- " + linha.strip())
    return "\n".join(novo)

def salvar_resumo(cluster: int, conteudo: str, qtd_reclamacoes: int):
    os.makedirs(PASTA_SAIDA, exist_ok=True)
    path = os.path.join(PASTA_SAIDA, f"cluster_{cluster}.txt")
    with open(path, "w", encoding="utf-8") as f:
        f.write(f"==============================\n")
        f.write(f"CLUSTER: {cluster}\n")
        f.write(f"QUANTIDADE DE RECLAMAÇÕES: {qtd_reclamacoes}\n")
        f.write(f"==============================\n\n")
        f.write("Resumo do cluster:\n")
        f.write(conteudo)
        f.write("\n")
    print(f"✅ Resumo do cluster {cluster} salvo em: {path}")

def chamar_ollama(prompt: str) -> str:
    payload = {
        "model": OLLAMA_MODEL,
        "messages": [
            {"role": "system", "content": "Você é um analista organizacional experiente. Responda em português."},
            {"role": "user", "content": prompt}
        ],
        "stream": False
    }
    response = requests.post(OLLAMA_URL, json=payload)
    response.raise_for_status()
    return response.json()["message"]["content"].strip()

# ======= EXECUÇÃO PRINCIPAL =======
if __name__ == "__main__":
    df = pd.read_pickle(CAMINHO_DF)

    for cluster in sorted(df["cluster"].unique()):
        textos = df[df["cluster"] == cluster]["avaliacao"].dropna().tolist()
        qtd_reclamacoes = len(textos)
        prompt = gerar_prompt(cluster, textos)

        for tentativa in range(1, MAX_TENTATIVAS + 1):
            try:
                resposta = chamar_ollama(prompt)
                if resposta_esta_no_formato(resposta):
                    salvar_resumo(cluster, resposta, qtd_reclamacoes)
                    break
                else:
                    # Tenta reformatar automaticamente
                    resposta_reformatada = reformatar_resposta(resposta)
                    if resposta_esta_no_formato(resposta_reformatada):
                        salvar_resumo(cluster, resposta_reformatada, qtd_reclamacoes)
                        break
                    print(f"⚠️ Tentativa {tentativa}: resposta fora do formato.")
                    prompt = (
                        "A resposta abaixo está fora do formato esperado. Reescreva no formato mostrado acima "
                        "(com os blocos '**Título do Cluster**', '**Palavras-Chave Frequentes**', '**Tópicos Principais**'), "
                        "e mantenha tudo em português do Brasil:\n\n" + resposta
                    )
            except Exception as e:
                print(f"❌ Erro inesperado na tentativa {tentativa} para cluster {cluster}: {e}")
                time.sleep(3)
        else:
            print(f"❌ Não foi possível gerar o resumo do cluster {cluster} após {MAX_TENTATIVAS} tentativas.")
