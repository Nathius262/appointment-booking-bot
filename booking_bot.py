import time
import schedule
from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager
import json
from captcha_solver import solve_captcha  # Import CAPTCHA-solving function

# Load configuration
with open("config.json", "r") as config_file:
    config = json.load(config_file)

def get_browser_driver(browser_name):
    """Return the appropriate WebDriver for the specified browser."""
    if browser_name.lower() == "chrome":
        from selenium.webdriver.chrome.service import Service
        return webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    elif browser_name.lower() == "firefox":
        from selenium.webdriver.firefox.service import Service
        return webdriver.Firefox(service=Service(GeckoDriverManager().install()))
    elif browser_name.lower() == "edge":
        from selenium.webdriver.edge.service import Service
        return webdriver.Edge(service=Service(EdgeChromiumDriverManager().install()))
    else:
        raise ValueError(f"Unsupported browser: {browser_name}")

def open_browser_and_fill_form(url, category_details):
    """Open browser, detect availability, solve CAPTCHA, and submit the form."""
    driver = get_browser_driver(config["browser"])

    try:
        driver.get(url)
        time.sleep(2)  # Wait for the page to load

        # Detect availability (customize based on actual availability indicator)
        slot_available = driver.find_elements(By.ID, config["availability_indicator"])
        if not slot_available:
            print(f"No slots available for {url}")
            driver.quit()
            return

        # Solve CAPTCHA
        captcha_value = solve_captcha(driver, config["captcha_solver_url"])
        if not captcha_value:
            print("Failed to solve CAPTCHA.")
            driver.quit()
            return

        # Fill out the form
        driver.find_element(By.ID, "appointment_captcha_day_lastname").send_keys(category_details["lastname"])
        driver.find_element(By.ID, "appointment_captcha_day_firstname").send_keys(category_details["firstname"])
        driver.find_element(By.ID, "appointment_captcha_day_email").send_keys(category_details["email"])
        driver.find_element(By.ID, "appointment_captcha_day_captchaText").send_keys(captcha_value)

        # Submit the form
        submit_button = driver.find_element(By.ID, "appointment_captcha_day_appointment_showDay")
        submit_button.click()

        print(f"Form submitted for {url}")
    except Exception as e:
        print(f"Error processing {url}: {e}")
    finally:
        driver.quit()

def run_bot():
    """Schedule and execute the bot for all URLs."""
    for url, details in config["links"].items():
        open_browser_and_fill_form(url, details)

# Schedule the bot
schedule.every().day.at(config["schedule_time"]).do(run_bot)

print(f"Bot scheduled to run at {config['schedule_time']} on {config['browser']}.")
while True:
    schedule.run_pending()
    time.sleep(1)
