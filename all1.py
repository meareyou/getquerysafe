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
import sys
import urllib.parse

if not os.path.exists("sesilog"):
    os.makedirs("sesilog")

def get_session_names():
    return [d for d in os.listdir("sesilog") if os.path.isdir(os.path.join("sesilog", d))]

def get_bot_choice():
    bots = ["TimeFarmCryptoBot", "Dotcoin_bot", "UEEx_Miner_bot", "layernet_netcoin_bot", "dogshouse_bot", "OfficialBananaBot", "BlumCryptoBot", "Tomarket_ai_bot",]
    print("Available bots:")
    for i, bot in enumerate(bots, 1):
        print(f"{i}. {bot}")
    while True:
        try:
            choice = int(input("Choose a bot number: "))
            if 1 <= choice <= len(bots):
                return bots[choice - 1]
            else:
                print("Invalid choice. Please try again.")
        except ValueError:
            print("Please enter a valid number.")

def take_screenshot(driver, filename):
    driver.save_screenshot(f"{filename}.png")
    print(f"Screenshot saved as {filename}.png")

def setup_driver(session_name):
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
        print(f"Chrome WebDriver initialized successfully for session: {session_name}")
        return driver
    except Exception as e:
        print(f"Error initializing Chrome WebDriver for session {session_name}: {e}")
        return None

def is_logged_in(driver):
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'chat-list')]"))
        )
        return True
    except:
        return False

def save_local_storage(driver, session_name):
    local_storage = driver.execute_script("return window.localStorage;")
    with open(f'sesilog/{session_name}/local_storage.json', 'w') as f:
        json.dump(local_storage, f)

def load_local_storage(driver, session_name):
    if os.path.exists(f'sesilog/{session_name}/local_storage.json'):
        with open(f'sesilog/{session_name}/local_storage.json', 'r') as f:
            local_storage = json.load(f)
            for key, value in local_storage.items():
                driver.execute_script(f"window.localStorage.setItem('{key}', '{value}');")

def log_in(driver, session_name):
    if not is_logged_in(driver):
        print(f"Logging in to session: {session_name}")
        
        phone_login_button = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Log in by phone Number')]"))
        )
        phone_login_button.click()

        phone_input = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.ID, "sign-in-phone-number"))
        )#XDt0sky

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
        
        save_local_storage(driver, session_name)
    else:
        print(f"Already logged in to session: {session_name}")

def navigate_to_bot(driver, bot_name):
    driver.get(f"https://web.telegram.org/k/#@{bot_name}")

    WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'chat-input')]"))
    )

def extract_iframe_data(driver):
    try:
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CLASS_NAME, "popup-payment-verification"))
        )
        print("Popup appeared")

        iframe = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "iframe.payment-verification"))
        )
        iframe_src = iframe.get_attribute("src")
        print(f"Iframe src: {iframe_src}")

        parsed_url = urllib.parse.urlparse(iframe_src)
        query_part = urllib.parse.parse_qs(parsed_url.fragment).get('tgWebAppData', [None])[0]
        
        if query_part:
            with open('tomat.txt', 'a') as f:
                query_part = query_part.strip()
                f.write(query_part + "\n")
            print("Query part of iframe src saved to times.txt")
        else:
            print("Query part not found in the iframe src")

    except Exception as e:
        print(f"Failed to load Time Farm app or extract data: {e}")
        print("Page source:")
        print(driver.page_source)

def time_farm_process(driver):
    try:
        open_app_button = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, f"//button[contains(@class, 'reply-markup-button') and .//span[text()='Open App']]"))
        )
        driver.execute_script("arguments[0].click();", open_app_button)
        print("Clicked 'Open App' button")
        time.sleep(5)
    except Exception as e:
        print(f"Exception occurred while finding or clicking 'Open App' button: {e}")

    try:
        launch_button = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, f"//button[contains(@class, 'popup-button') and .//span[text()='Launch']]"))
        )
        driver.execute_script("arguments[0].click();", launch_button)
        print("Clicked 'Launch' button")
        time.sleep(5)
    except Exception as e:
        print(f"Exception occurred while finding or clicking 'Launch' button: {e}")
        time.sleep(5)

def tomat(driver):
    try:
        open_app_button = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, f"//button[contains(@class, 'reply-markup-button') and .//span[text()='Play Tomarket']]"))
        )
        driver.execute_script("arguments[0].click();", open_app_button)
        print("Clicked 'Open App' button")
        time.sleep(5)
    except Exception as e:
        print(f"Exception occurred while finding or clicking 'Open App' button: {e}")

    try:
        launch_button = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, f"//button[contains(@class, 'popup-button') and .//span[text()='Launch']]"))
        )
        driver.execute_script("arguments[0].click();", launch_button)
        print("Clicked 'Launch' button")
        time.sleep(5)
    except Exception as e:
        print(f"Exception occurred while finding or clicking 'Launch' button: {e}")
        time.sleep(5)

def blum(driver):
    try:
        open_app_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, f"//button[contains(@class, 'reply-markup-button') and .//span[text()='Launch Blum']]"))
        )
        driver.execute_script("arguments[0].click();", open_app_button)
        print("Clicked 'launch App' button")
        time.sleep(5)
    except Exception as e:
        print(f"Exception occurred while finding or clicking 'launch App' button: {e}")

    try:
        open_app_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, f"//button[contains(@class, 'reply-markup-button') and .//span[text()='Explore your frens']]"))
        )
        driver.execute_script("arguments[0].click();", open_app_button)
        print("Clicked 'explore App' button")
        time.sleep(5)
    except Exception as e:
        print(f"Exception occurred while finding or clicking 'explore App' button: {e}")

    try:
        launch_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, f"//button[contains(@class, 'popup-button') and .//span[text()='Launch']]"))
        )
        driver.execute_script("arguments[0].click();", launch_button)
        print("Clicked 'Launch' button")
        time.sleep(5)
    except Exception as e:
        print(f"Exception occurred while finding or clicking 'Launch' button: {e}")
        time.sleep(5)

def dotcoin_process(driver):
    try:
        lets_go_button = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, f"//button[contains(@class, 'reply-markup-button') and .//span[contains(text(), \"Let's go\")]]"))
        )
        driver.execute_script("arguments[0].click();", lets_go_button)
        print("Clicked 'Let's go' button")
        time.sleep(5)
    except Exception as e:
        print(f"Exception occurred while finding or clicking 'Let's go' button: {e}")

    try:
        back_to_dotcoin_button = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, f"//button[contains(@class, 'reply-markup-button') and .//span[text()='Back to Dotcoin']]"))
        )
        driver.execute_script("arguments[0].click();", back_to_dotcoin_button)
        print("Clicked 'Back to Dotcoin' button")
        time.sleep(5)
    except Exception as e:
        print(f"Exception occurred while finding or clicking 'Back to Dotcoin' button: {e}")

    
    try:
        launch_button = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, f"//button[contains(@class, 'popup-button') and .//span[text()='Launch']]"))
        )
        driver.execute_script("arguments[0].click();", launch_button)
        print("Clicked 'Launch' button")
        time.sleep(5)
    except Exception as e:
        print(f"Exception occurred while finding or clicking 'Launch' button: {e}")
        time.sleep(5)

def uex_do(driver):
    try:
        launch_miniapp_button = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, f"//div[@class='new-message-bot-commands-view' and text()='Start']"))
        )
        driver.execute_script("arguments[0].click();", launch_miniapp_button)
        print("Clicked 'Start' button")
        time.sleep(5)
    except Exception as e:
        print(f"Exception occurred while finding or clicking 'Start' button: {e}")

    try:
        launch_button = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, f"//button[contains(@class, 'popup-button') and .//span[text()='Launch']]"))
        )
        driver.execute_script("arguments[0].click();", launch_button)
        print("Clicked 'Launch' button")
        time.sleep(5)
    except Exception as e:
        print(f"Exception occurred while finding or clicking 'Launch' button: {e}")
        time.sleep(5)

def netcoinjp(driver):
    try:
        launch_miniapp_button = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, f"//div[@class='new-message-bot-commands-view' and text()='Play']"))
        )
        driver.execute_script("arguments[0].click();", launch_miniapp_button)
        print("Clicked 'PLay' button")
        time.sleep(5)
    except Exception as e:
        print(f"Exception occurred while finding or clicking 'Play' button: {e}")

    try:
        launch_button = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, f"//button[contains(@class, 'popup-button') and .//span[text()='Launch']]"))
        )
        driver.execute_script("arguments[0].click();", launch_button)
        print("Clicked 'Launch' button")
        time.sleep(5)
    except Exception as e:
        print(f"Exception occurred while finding or clicking 'Launch' button: {e}")
        time.sleep(5)

def anjing(driver):
    try:
        launch_miniapp_button = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, f"//div[@class='new-message-bot-commands-view' and text()='Open']"))
        )
        driver.execute_script("arguments[0].click();", launch_miniapp_button)
        print("Clicked 'Open' button")
        time.sleep(5)
    except Exception as e:
        print(f"Exception occurred while finding or clicking 'Play' button: {e}")

    try:
        launch_button = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, f"//button[contains(@class, 'popup-button') and .//span[text()='Launch']]"))
        )
        driver.execute_script("arguments[0].click();", launch_button)
        print("Clicked 'Launch' button")
        time.sleep(25)
    except Exception as e:
        print(f"Exception occurred while finding or clicking 'Launch' button: {e}")
        time.sleep(5)

def pisang(driver):
    try:
        launch_miniapp_button = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, f"//div[@class='new-message-bot-commands-view' and text()='play']"))
        )
        driver.execute_script("arguments[0].click();", launch_miniapp_button)
        print("Clicked 'play' button")
        time.sleep(5)
    except Exception as e:
        print(f"Exception occurred while finding or clicking 'Play' button: {e}")

    try:
        launch_button = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, f"//button[contains(@class, 'popup-button') and .//span[text()='Launch']]"))
        )
        driver.execute_script("arguments[0].click();", launch_button)
        print("Clicked 'Launch' button")
        time.sleep(5)
    except Exception as e:
        print(f"Exception occurred while finding or clicking 'Launch' button: {e}")
        time.sleep(5)

def main():
    selected_sessions = get_session_names()
    if not selected_sessions:
        print("No sessions found in 'sesilog' directory.")
        return

    print("Available sessions:")
    for i, session in enumerate(selected_sessions, 1):
        print(f"{i}. {session}")
    print(f"{len(selected_sessions) + 1}. Run all accounts")

    session_choice = int(input("Choose a session number: ")) - 1

    if session_choice == len(selected_sessions):
        run_all_sessions = True
    else:
        run_all_sessions = False
        session = selected_sessions[session_choice]

    bot_name = get_bot_choice()

    def process_session(session):
        try:#dontchangethisverif'dC5tZS94ZHQwc2t5'
            driver = setup_driver(session)
            if driver:
                load_local_storage(driver, session)
                driver.get("https://web.telegram.org/a/")
                time.sleep(10)
                log_in(driver, session)
                navigate_to_bot(driver, bot_name)

                if bot_name == "TimeFarmCryptoBot":
                    time_farm_process(driver)
                elif bot_name == "Dotcoin_bot":
                    dotcoin_process(driver)
                elif bot_name == "UEEx_Miner_bot":
                    uex_do(driver)
                elif bot_name == "layernet_netcoin_bot":
                    netcoinjp(driver)
                elif bot_name == "dogshouse_bot":
                    anjing(driver)
                elif bot_name == "OfficialBananaBot":
                    pisang(driver)
                elif bot_name == "BlumCryptoBot":
                    blum(driver)
                elif bot_name == "Tomarket_ai_bot":
                    tomat(driver)

                extract_iframe_data(driver)
                driver.quit()
        except KeyboardInterrupt:
            print("Script interrupted by user. Exiting...")

    if run_all_sessions:
        for session in selected_sessions:
            print(f"Processing session: {session}")
            process_session(session)
    else:
        process_session(session)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nScript interrupted by user. Exiting...")
        sys.exit()
