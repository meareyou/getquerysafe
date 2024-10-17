from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
import os
import time
import urllib.parse


if not os.path.exists("sesilog"):
    os.makedirs("sesilog")

def get_session_name():
    sessions = [d for d in os.listdir("sesilog") if os.path.isdir(os.path.join("sesilog", d))]
    if not sessions:
        return create_new_session()

    print("Available sessions:")
    for i, session in enumerate(sessions, 1):
        print(f"{i}. {session}")
    print(f"{len(sessions) + 1}. Create new session")

    while True:
        try:
            choice = int(input("Choose a session number or create a new one: "))
            if 1 <= choice <= len(sessions):
                return sessions[choice - 1]
            elif choice == len(sessions) + 1:
                return create_new_session()
            else:
                print("Invalid choice. Please try again.")
        except ValueError:
            print("Please enter a valid number.")

def create_new_session():
    while True:
        session_name = input("Enter a name for the new session: ")
        if session_name and not os.path.exists(os.path.join("sesilog", session_name)):
            return session_name
        else:
            print("Session name already exists or is invalid. Please choose a different name.")

def take_screenshot(driver, filename):
    driver.save_screenshot(f"{filename}.png")
    print(f"Screenshot saved as {filename}.png")


session_name = get_session_name()
session_dir = os.path.join("sesilog", session_name)

chrome_options = Options()
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--remote-debugging-port=9222")
chrome_options.add_argument(f"user-data-dir={session_dir}")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--ignore-certificate-errors")
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 GLS/100.10.9989.100")

try:
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    print("Chrome WebDriver initialized successfully")
except Exception as e:
    print(f"Error initializing Chrome WebDriver: {e}")
    print("Attempting to use Firefox WebDriver...")
    from selenium.webdriver.firefox.options import Options as FirefoxOptions
    from webdriver_manager.firefox import GeckoDriverManager
    
    firefox_options = FirefoxOptions()
    firefox_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 GLS/100.10.9989.100")
    driver = webdriver.Firefox(executable_path=GeckoDriverManager().install(), options=firefox_options)
    print("Firefox WebDriver initialized successfully")

def is_logged_in():
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'chat-list')]"))
        )
        return True
    except:
        return False

def save_local_storage(session_name):
    local_storage = driver.execute_script("return window.localStorage;")
    with open(f'sesilog/{session_name}/local_storage.json', 'w') as f:
        json.dump(local_storage, f)

def load_local_storage(session_name):
    if os.path.exists(f'sesilog/{session_name}/local_storage.json'):
        with open(f'sesilog/{session_name}/local_storage.json', 'r') as f:
            local_storage = json.load(f)
            for key, value in local_storage.items():
                driver.execute_script(f"window.localStorage.setItem('{key}', '{value}');")

if os.path.exists(f'sesilog/{session_name}/local_storage.json'):
    load_local_storage(session_name)
#goofyasssknl
driver.get("https://web.telegram.org/a/")
time.sleep(10)

if not is_logged_in():
    print(f"Logging in to session: {session_name}")
    
    phone_login_button = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Log in by phone Number')]"))
    )
    phone_login_button.click()
    
    phone_input = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.ID, "sign-in-phone-number"))
    )
    
    phone_input.clear()
    
    phone_number = input("Enter your phone number (with country code): ")
    phone_input.send_keys(phone_number)
    
    keep_signed_in_checkbox = driver.find_element(By.ID, "sign-in-keep-session")
    if not keep_signed_in_checkbox.is_selected():
        keep_signed_in_checkbox.click()

    next_button = driver.find_element(By.XPATH, "//button[contains(@class, 'primary')]")
    next_button.click()
    
    otp_input = WebDriverWait(driver, 60).until(
        EC.presence_of_element_located((By.ID, "sign-in-code"))
    )
    otp = input("Enter the OTP you received: ")
    otp_input.send_keys(otp)
    
    try:
        password_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "sign-in-password"))
        )
        password = input("Enter your 2FA password: ")
        password_input.send_keys(password)
        driver.find_element(By.XPATH, "//button[contains(@class, 'primary')]").click()
    except:
        print("2FA not required or already logged in")
    
    WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'chat-list')]"))
    )
    
    save_local_storage(session_name)
else:
    print(f"Already logged in to session: {session_name}")


driver.quit()
print("Driver quit successfully")
