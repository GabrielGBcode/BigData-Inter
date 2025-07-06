import openai
import pandas as pd
import os
import time
from dotenv import load_dotenv
from pathlib import Path
import tiktoken
from openai import OpenAIError, RateLimitError

# ======= CONFIGURAÇÕES =======
MODEL_NAME = 'gpt-4-turbo'
MAX_TOKENS = 16000
MAX_TOKENS_RESPOSTA = 2000  # reserva para resposta
MAX_TOKENS_PROMPT = MAX_TOKENS - MAX_TOKENS_RESPOSTA
CAMINHO_DF = "processados/df_processado.pkl"
PASTA_SAIDA = 'resumos_clusters'
MAX_TENTATIVAS = 3

# ======= CARREGAR .env =======
dotenv_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path)
openai.api_key = os.getenv("OPENAI_API_KEY")

# ======= FUNÇÕES =======

# Inicializa o codificador de tokens
tokenizer = tiktoken.encoding_for_model(MODEL_NAME)

def contar_tokens(texto: str) -> int:
    return len(tokenizer.encode(texto))

def gerar_prompt(cluster_id: int, textos: list[str]) -> str:
    exemplo = (
        "**Título do Cluster**: Falta de plano de carreira\n"
        "**Palavras-Chave Frequentes**: plano, carreira, crescimento, promoção, metas, oportunidades, liderança, desenvolvimento, valorização, salário\n"
        "**Tópicos Principais:**\n"
        "- Falta de plano de carreira estruturado\n"
        "- Ausência de critérios claros para promoções\n"
        "- Sentimento de estagnação profissional\n"
        "- Pouca transparência nos processos internos\n"
        "- Falta de valorização do desempenho individual\n"
        "- Dificuldade em identificar caminhos de crescimento\n"
        "- Desmotivação por falta de reconhecimento\n"
        "- Baixa mobilidade interna\n"
        "- Falta de feedback constante\n"
        "- Contratações externas em vez de promoções internas\n"
    )

    prompt_inicial = (
        "Você é um analista organizacional. Analise o seguinte grupo de reclamações de funcionários do mesmo cluster.\n"
        "IMPORTANTE: Responda EXCLUSIVAMENTE em **português do Brasil** e siga ESTRITAMENTE o modelo abaixo.\n"
        "Se você responder em outro idioma ou fora do formato, a resposta será descartada.\n\n"
        "=== MODELO DE RESPOSTA QUE VOCÊ DEVE IMITAR ===\n\n"
        + exemplo +
        "\n=== FIM DO MODELO ===\n\n"
        "Agora, gere a resposta para o seguinte conjunto de reclamações:\n\n"
        "Textos:\n"
    )

    # Adiciona textos até atingir o limite de tokens
    prompt_tokens = contar_tokens(prompt_inicial)
    textos_selecionados = []
    tokens_atuais = prompt_tokens

    for texto in textos:
        tokens_texto = contar_tokens(texto) + 1  # inclui quebra de linha
        if tokens_atuais + tokens_texto > MAX_TOKENS_PROMPT:
            break
        textos_selecionados.append(texto)
        tokens_atuais += tokens_texto

    return prompt_inicial + "\n".join(textos_selecionados)

def resposta_esta_no_formato(resumo: str) -> bool:
    return all(bloco in resumo for bloco in [
        "**Título do Cluster**:",
        "**Palavras-Chave Frequentes**:",
        "**Tópicos Principais:**"
    ])

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

def chamar_chatgpt(prompt: str) -> str:
    response = openai.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": "Você é um analista organizacional experiente. Responda em português."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3
    )
    return response.choices[0].message.content.strip()

# ======= EXECUÇÃO PRINCIPAL =======
if __name__ == "__main__":
    df = pd.read_pickle(CAMINHO_DF)

    for cluster in sorted(df["cluster"].unique()):
        textos = df[df["cluster"] == cluster]["avaliacao"].dropna().tolist()
        qtd_reclamacoes = len(textos)
        prompt = gerar_prompt(cluster, textos)

        for tentativa in range(1, MAX_TENTATIVAS + 1):
            try:
                resposta = chamar_chatgpt(prompt)
                if resposta_esta_no_formato(resposta):
                    salvar_resumo(cluster, resposta, qtd_reclamacoes)
                    break
                else:
                    print(f"⚠️ Tentativa {tentativa}: resposta fora do formato.")
                    prompt = (
                        "A resposta abaixo está fora do formato esperado. Reescreva no formato mostrado acima "
                        "(com os blocos '**Título do Cluster**', '**Palavras-Chave Frequentes**', '**Tópicos Principais**'), "
                        "e mantenha tudo em português do Brasil:\n\n" + resposta
                    )
            except RateLimitError:
                print("⏳ Limite de requisições atingido. Aguardando 60 segundos...")
                time.sleep(60)
            except OpenAIError as e:
                print(f"❌ Erro da OpenAI na tentativa {tentativa} para cluster {cluster}: {e}")
                time.sleep(3)
            except Exception as e:
                print(f"❌ Erro inesperado na tentativa {tentativa} para cluster {cluster}: {e}")
                time.sleep(3)
        else:
            print(f"❌ Não foi possível gerar o resumo do cluster {cluster} após {MAX_TENTATIVAS} tentativas.")
