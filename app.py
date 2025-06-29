import subprocess
import sys
import os

# Função para rodar um script Python e checar sucesso
def run_script(script_path):
    print(f"\nExecutando: {script_path}")
    result = subprocess.run([sys.executable, script_path])
    if result.returncode != 0:
        print(f"Erro ao executar {script_path}. Abortando fluxo.")
        sys.exit(result.returncode)
    print(f"Concluído: {script_path}")

# Função para garantir o modelo bge-m3 do Ollama
def ensure_ollama_bge_m3():
    print("\nVerificando modelo bge-m3 do Ollama...")
    try:
        result = subprocess.run(["ollama", "pull", "bge-m3"], check=True)
        print("Modelo bge-m3 do Ollama pronto para uso.")
    except FileNotFoundError:
        print("[ERRO] Ollama não está instalado ou não está no PATH. Instale o Ollama antes de rodar o pipeline.")
        sys.exit(1)
    except subprocess.CalledProcessError:
        print("[ERRO] Não foi possível baixar o modelo bge-m3 do Ollama. Verifique sua instalação do Ollama.")
        sys.exit(1)

if __name__ == "__main__":
    # 0. Garantir modelo do Ollama
    ensure_ollama_bge_m3()

    # 1. Coleta dos dados do Glassdoor
    run_script(os.path.join('scripts', 'glassdoor_scraper.py'))

    # 2. Converte Parquet para Excel
    run_script(os.path.join('scripts', 'parquet_para_xlsx.py'))

    # 3. Processamento e clustering
    run_script(os.path.join('scripts', 'processamento_clusters.py'))

    # 4. Gera nuvens de palavras
    run_script(os.path.join('scripts', 'nuvem_palavras.py'))

    # 5. Gera gráfico do método do cotovelo
    run_script(os.path.join('scripts', 'metodo_cotovelo.py'))

    print("\nFluxo completo finalizado com sucesso!")