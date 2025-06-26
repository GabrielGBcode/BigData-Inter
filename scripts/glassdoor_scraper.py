import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from unidecode import unidecode
import time
import hashlib
import os

# --- 1. Configuração do Selenium ---
chrome_options = Options()
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--disable-notifications")
chrome_options.add_argument("--disable-popup-blocking")
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
chrome_options.add_argument("--window-size=1920,1080")

# Crie o driver
driver = webdriver.Chrome(options=chrome_options)
wait = WebDriverWait(driver, 15)

login_email = "gabrielgb.user@gmail.com"
login_password = "ga91929394"
reviews_url = "https://www.glassdoor.com.br/Avalia%C3%A7%C3%B5es/Inter-Avalia%C3%A7%C3%B5es-E2483031.htm"
login_url = "https://www.glassdoor.com.br/profile/login_input.htm"

def fechar_popups():
    try:
        close_selectors = [
            'button[alt="Fechar"]',
            'button[aria-label="Fechar"]',
            'button.close-button',
            'button.modal_closeIcon',
            'button[data-test="modal-close"]',
            'button[class*="close"]',
            'button[class*="Close"]'
        ]
        for selector in close_selectors:
            buttons = driver.find_elements(By.CSS_SELECTOR, selector)
            for button in buttons:
                if button.is_displayed():
                    driver.execute_script("arguments[0].click();", button)
                    time.sleep(0.5)
    except:
        pass

# --- 2. Login no Glassdoor ---
print("Tentando fazer login no Glassdoor...")
driver.get(login_url)
time.sleep(2)

try:
    fechar_popups()
    print("Procurando campo de e-mail...")
    email_field = wait.until(
        EC.presence_of_element_located((By.ID, "inlineUserEmail"))
    )
    email_field.clear()
    email_field.click()
    email_field.send_keys(login_email)
    print("E-mail preenchido.")
    time.sleep(1)

    print("Procurando botão de continuar...")
    continue_button = wait.until(
        EC.element_to_be_clickable((By.XPATH, "//button[@type='submit']"))
    )
    driver.execute_script("arguments[0].click();", continue_button)
    print("Botão de continuar clicado.")
    time.sleep(2)

    print("Procurando campo de senha...")
    password_field = wait.until(
        EC.presence_of_element_located((By.ID, "inlineUserPassword"))
    )
    password_field.clear()
    password_field.click()
    password_field.send_keys(login_password)
    print("Senha preenchida.")
    time.sleep(1)

    print("Procurando botão de login...")
    login_button = wait.until(
        EC.element_to_be_clickable((By.XPATH, "//button[@type='submit']"))
    )
    driver.execute_script("arguments[0].click();", login_button)
    print("Botão de login clicado.")
    time.sleep(4)

    if "profile" in driver.current_url:
        print("Login realizado com sucesso!")
    else:
        print("Possível falha no login. Verificando...")
        time.sleep(3)

except Exception as e:
    print(f"Erro durante o processo de login: {e}")
    print("Tentando continuar mesmo sem login...")

# --- 3. Navegar para a Página de Avaliações ---
print(f"Navegando para: {reviews_url}")
driver.get(reviews_url)
time.sleep(3)

# --- 4. Coleta de Dados ---
reviews_data = []
seen_review_hashes = set()
print("Iniciando coleta das avaliações...")
current_page = 1
while True:
    try:
        fechar_popups()
        total_height = driver.execute_script("return document.body.scrollHeight")
        for i in range(0, total_height, 500):
            driver.execute_script(f"window.scrollTo(0, {i});")
            time.sleep(0.1)
        time.sleep(0.5)
        review_elements = driver.find_elements(By.XPATH, "//span[@data-test='review-avatar-label']/ancestor::li | //span[@data-test='review-avatar-label']/ancestor::div[@data-test='review-container']")
        print(f"Encontradas {len(review_elements)} avaliações nesta página.")
        new_reviews_this_iteration = 0
        for review_el in review_elements:
            try:
                try:
                    funcao_el = review_el.find_element(By.XPATH, ".//span[@data-test='review-avatar-label']")
                    funcao = funcao_el.text.strip()
                except:
                    funcao = "Não informado"
                try:
                    pros_el = review_el.find_element(By.XPATH, ".//span[@data-test='review-text-PROS']")
                    pros_text = "PRÓS: " + pros_el.text.strip()
                except:
                    pros_text = ""
                try:
                    cons_el = review_el.find_element(By.XPATH, ".//span[@data-test='review-text-CONS']")
                    cons_text = "CONTRAS: " + cons_el.text.strip()
                except:
                    cons_text = ""
                avaliacao_final = f"{pros_text} | {cons_text}" if pros_text and cons_text else pros_text or cons_text or "Avaliação vazia"
                current_review_hash = hashlib.md5(f"{funcao}-{avaliacao_final}".encode('utf-8')).hexdigest()
                if current_review_hash not in seen_review_hashes:
                    reviews_data.append({"funcao": funcao, "avaliacao": avaliacao_final})
                    seen_review_hashes.add(current_review_hash)
                    new_reviews_this_iteration += 1
            except Exception as e:
                print(f"Erro ao processar uma avaliação: {e}")
                continue
        print(f"Total de avaliações coletadas: {len(reviews_data)}")
        print(f"Novas avaliações nesta iteração: {new_reviews_this_iteration}")
        try:
            next_page_number = current_page + 1
            next_page_selector = f"a[data-test='page-number-{next_page_number}']"
            next_page_button = driver.find_elements(By.CSS_SELECTOR, next_page_selector)
            if next_page_button and next_page_button[0].is_displayed() and next_page_button[0].is_enabled():
                driver.execute_script("arguments[0].click();", next_page_button[0])
                time.sleep(1.2)
                current_page += 1
                print(f"Avançando para a página {current_page}")
            else:
                print("Fim das avaliações ou não há próxima página.")
                break
        except Exception as e:
            print(f"Não foi possível encontrar o botão de próxima página: {e}")
            break
        if new_reviews_this_iteration == 0:
            print("Nenhuma nova avaliação encontrada nesta iteração.")
            break
    except Exception as e:
        print(f"Erro durante a coleta: {e}")
        break
driver.quit()
print("Navegador fechado.")

# --- 5. Processamento e Tratamento dos Dados ---
if reviews_data:
    df_reviews = pd.DataFrame(reviews_data)
    print("\nIniciando tratamento dos dados...")
    df_reviews['funcao'] = df_reviews['funcao'].astype(str)
    df_reviews['avaliacao'] = df_reviews['avaliacao'].astype(str)
    df_reviews['funcao'] = df_reviews['funcao'].apply(lambda x: unidecode(x).upper())
    df_reviews['avaliacao'] = df_reviews['avaliacao'].apply(lambda x: unidecode(x).upper())
    print("Exemplo de dados tratados:")
    print(df_reviews.head())
    # Garante que a pasta 'data' existe
    os.makedirs('data', exist_ok=True)
    output_parquet_file = os.path.join('data', 'avaliacoes_inter.parquet')
    df_reviews.to_parquet(output_parquet_file, index=False)
    print(f"\nDados salvos em '{output_parquet_file}' com sucesso!")
else:
    print("Nenhuma avaliação foi coletada.")