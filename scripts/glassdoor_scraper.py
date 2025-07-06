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
from selenium.webdriver.chrome.service import Service
import tkinter as tk
from tkinter import simpledialog, messagebox
from webdriver_manager.chrome import ChromeDriverManager
import sys
import re

# Defina a URL das avaliações do Inter no Glassdoor antes de usá-la
reviews_url = "https://www.glassdoor.com.br/Avalia%C3%A7%C3%B5es/Inter-Avalia%C3%A7%C3%B5es-E2483031.htm"
login_url = "https://www.glassdoor.com.br/profile/login_input.htm"

# Função para fechar popups
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

# Função para tentar login no Glassdoor
def try_login(driver, wait, login_url, login_email, login_password):
    try:
        driver.get(login_url)
        time.sleep(2)
        fechar_popups()
        email_field = wait.until(
            EC.presence_of_element_located((By.ID, "inlineUserEmail"))
        )
        email_field.clear()
        email_field.click()
        email_field.send_keys(login_email)
        time.sleep(1)
        continue_button = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//button[@type='submit']"))
        )
        driver.execute_script("arguments[0].click();", continue_button)
        time.sleep(2)
        password_field = wait.until(
            EC.presence_of_element_located((By.ID, "inlineUserPassword"))
        )
        password_field.clear()
        password_field.click()
        password_field.send_keys(login_password)
        time.sleep(1)
        login_button = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//button[@type='submit']"))
        )
        driver.execute_script("arguments[0].click();", login_button)
        # Espera até 5 segundos por mensagem de erro ou reCAPTCHA
        erro_login = False
        recaptcha_detectado = False
        for _ in range(10):
            time.sleep(0.5)
            # Se saiu da tela de login, login foi bem-sucedido
            if '/login' not in driver.current_url and driver.current_url != login_url:
                return True
            # Só busca erro de login se ainda estiver na tela de login
            if '/login' in driver.current_url or driver.current_url == login_url:
                # Busca por textos de erro de login
                error_elements = driver.find_elements(By.XPATH, "//*[contains(text(), 'incorreto') or contains(text(), 'incorretos') or contains(text(), 'errado') or contains(text(), 'inválido') or contains(text(), 'invalid') or contains(text(), 'senha errada') or contains(text(), 'senha incorreta') or contains(text(), 'email incorreto') or contains(text(), 'email ou senha estão errados') or contains(text(), 'A senha especificada é inválida')]")
                error_classes = driver.find_elements(By.XPATH, "//*[contains(@class, 'error') or contains(@class, 'alert') or contains(@class, 'invalid') or contains(@class, 'ErrorMessage')]")
                if error_elements or error_classes:
                    erro_login = True
                    break
            # Busca por iframe do reCAPTCHA visível
            recaptcha_iframes = driver.find_elements(By.XPATH, "//iframe[contains(@src, 'recaptcha')]")
            for iframe in recaptcha_iframes:
                try:
                    if iframe.is_displayed():
                        recaptcha_detectado = True
                        break
                except Exception:
                    continue
            if recaptcha_detectado:
                break
        if recaptcha_detectado:
            # Pausa e pede para o usuário resolver manualmente
            root = tk.Tk()
            root.withdraw()
            root.attributes('-topmost', True)
            messagebox.showinfo("Atenção: reCAPTCHA detectado", "Foi detectado um reCAPTCHA. Por favor, resolva o desafio manualmente no navegador e clique em OK para continuar.", parent=root)
            root.destroy()
            # Aguarda até que o login seja bem-sucedido ou o navegador seja fechado
            while True:
                time.sleep(2)
                if not driver.service.is_connectable():
                    print("Navegador fechado pelo usuário. Encerrando o script.")
                    sys.exit(0)
                # Verifica se o botão 'Entrar' ainda está presente
                try:
                    entrar_btn = driver.find_elements(By.XPATH, "//button[contains(., 'Entrar')] | //a[contains(., 'Entrar')]")
                except Exception:
                    entrar_btn = []
                if not entrar_btn:
                    # Não há mais botão 'Entrar', provavelmente logado
                    return True
                # Se ainda estiver na tela de login ou reCAPTCHA, continua aguardando
        if erro_login:
            return False
        # Verifica se login foi bem-sucedido pela URL
        if "profile" in driver.current_url or "reviews" in driver.current_url:
            return True
        else:
            return False
    except Exception as e:
        # Se o navegador foi fechado manualmente
        if not driver.service.is_connectable():
            print("Navegador fechado pelo usuário. Encerrando o script.")
            sys.exit(0)
        return False

# Função para obter email e senha com validação local
def get_credentials():
    def on_submit():
        nonlocal email, senha
        entered_email = email_var.get()
        entered_senha = senha_var.get()
        if not entered_email or not entered_senha:
            # Alerta em primeiro plano
            alert = tk.Tk()
            alert.withdraw()
            alert.attributes('-topmost', True)
            messagebox.showerror("Campos obrigatórios", "Preencha o email e a senha.", parent=alert)
            alert.destroy()
            return
        if not is_valid_email(entered_email):
            alert = tk.Tk()
            alert.withdraw()
            alert.attributes('-topmost', True)
            messagebox.showerror("Email inválido", "Por favor, insira um email válido.", parent=alert)
            alert.destroy()
            return
        email = entered_email
        senha = entered_senha
        root.destroy()

    def is_valid_email(email):
        # Regex robusta para validar e-mails (sem ponto antes do @, sem duplo ponto, etc)
        return re.match(r'^(?!.*\.\.)[a-zA-Z0-9](?:[a-zA-Z0-9._%+-]{0,62}[a-zA-Z0-9])?@[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)*\.[a-zA-Z]{2,}$', email)

    while True:
        email = ''
        senha = ''
        root = tk.Tk()
        root.title("Login Glassdoor")
        root.geometry("400x220")
        root.configure(bg="#f0f4f8")
        root.resizable(False, False)
        root.attributes('-topmost', True)

        # Fonte personalizada
        font_label = ("Segoe UI", 12, "bold")
        font_entry = ("Segoe UI", 12)
        font_button = ("Segoe UI", 12, "bold")

        # Frame centralizado
        frame = tk.Frame(root, bg="#f0f4f8")
        frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        tk.Label(frame, text="Email:", bg="#f0f4f8", fg="#333", font=font_label).grid(row=0, column=0, sticky="w", pady=(0,8))
        email_var = tk.StringVar()
        email_entry = tk.Entry(frame, textvariable=email_var, width=32, font=font_entry, bd=2, relief=tk.GROOVE)
        email_entry.grid(row=1, column=0, pady=(0,16))
        email_entry.focus()

        tk.Label(frame, text="Senha:", bg="#f0f4f8", fg="#333", font=font_label).grid(row=2, column=0, sticky="w", pady=(0,8))
        senha_var = tk.StringVar()
        senha_entry = tk.Entry(frame, textvariable=senha_var, show='*', width=32, font=font_entry, bd=2, relief=tk.GROOVE)
        senha_entry.grid(row=3, column=0, pady=(0,16))

        btn = tk.Button(frame, text="Entrar", command=on_submit, bg="#1976d2", fg="white", font=font_button, bd=0, padx=10, pady=6, activebackground="#1565c0", activeforeground="white")
        btn.grid(row=4, column=0, pady=(0,8))

        # Permite pressionar Enter para submeter
        root.bind('<Return>', lambda event: on_submit())

        root.mainloop()

        # Se o usuário fechar a janela ou não digitar nada, encerrar o script
        if not email or not senha:
            print("Login cancelado pelo usuário.")
            sys.exit(0)
        return email, senha

# --- 1. Configuração do Selenium ---
chrome_options = Options()
# chrome_options.add_argument("--disable-gpu")
# chrome_options.add_argument("--no-sandbox")
# chrome_options.add_argument("--disable-dev-shm-usage")
# chrome_options.add_argument("--disable-notifications")
# chrome_options.add_argument("--disable-popup-blocking")
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
chrome_options.add_argument("--window-size=1920,1080")

# Inicializa o driver automaticamente com webdriver-manager
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)
wait = WebDriverWait(driver, 15)

# --- Loop de login ---
while True:
    login_email, login_password = get_credentials()
    login_ok = try_login(driver, wait, login_url, login_email, login_password)
    if login_ok:
        print("Login realizado com sucesso!")
        break
    else:
        # Se o navegador foi fechado manualmente
        if not driver.service.is_connectable():
            print("Navegador fechado pelo usuário. Encerrando o script.")
            sys.exit(0)
        # Pergunta se deseja tentar novamente
        root = tk.Tk()
        root.withdraw()
        root.attributes('-topmost', True)
        retry = messagebox.askretrycancel("Erro de Login", "Email ou senha incorretos. Deseja tentar novamente?", parent=root)
        root.destroy()
        if not retry:
            print("Login cancelado pelo usuário.")
            driver.quit()
            sys.exit(0)
        # Se o usuário quiser tentar novamente, o loop volta ao início e chama get_credentials() novamente

# Só depois do login bem-sucedido, acessar a página de avaliações
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