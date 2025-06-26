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

if __name__ == "__main__":
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