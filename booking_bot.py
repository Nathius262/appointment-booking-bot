import os
import time
import json
import threading
import datetime
import schedule
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from captcha_solver import solve_captcha


def load_config():
    """Load configuration settings from the config.json file."""
    try:
        with open("config.json", "r") as config_file:
            return json.load(config_file)
    except Exception as e:
        print(f"Error loading configuration file: {e}")
        return None


def setup_driver():
    """Set up the Selenium WebDriver with custom headers to avoid 403 errors."""
    service = webdriver.chrome.service.Service(ChromeDriverManager().install())
    options = webdriver.ChromeOptions()

    # Add a custom User-Agent header to make the request look like it's from a real browser
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    
    # Disable automation flag and make the browser run in headless mode
    #options.add_argument("--headless")  # Optional: run in headless mode for performance
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")  # Disables webdriver detection

    driver = webdriver.Chrome(service=service, options=options)
    return driver

def create_screenshot_dir():
    """Create a directory to save screenshots if it doesn't exist."""
    screenshot_dir = "screenshots"
    if not os.path.exists(screenshot_dir):
        os.makedirs(screenshot_dir)
    return screenshot_dir

def save_screenshot(driver, url, category):
    """Save a screenshot with a unique name based on the URL or category."""
    screenshot_dir = create_screenshot_dir()
    # Use the URL or category name for the screenshot filename
    filename = f"{category}_{url.split('/')[-1]}.png"
    screenshot_path = os.path.join(screenshot_dir, filename)
    driver.save_screenshot(screenshot_path)
    print(f"Screenshot saved: {screenshot_path}")

def login_and_navigate(driver, url):
    """Navigate to the specified URL."""
    driver.get(url)
    time.sleep(2)  # Allow the page to load

def fill_form(driver, form_data, scope):
    """Fill out the form fields using the provided data."""
    try:
        driver.find_element(By.ID, f"appointment_captcha_{scope}_lastname").send_keys(form_data["lastname"])
        driver.find_element(By.ID, f"appointment_captcha_{scope}_firstname").send_keys(form_data["firstname"])
        driver.find_element(By.ID, f"appointment_captcha_{scope}_email").send_keys(form_data["email"])
        driver.find_element(By.ID, f"appointment_captcha_{scope}_locationCode").send_keys(form_data["locationCode"])
        print("Form filled successfully.")
    except Exception as e:
        print(f"Error filling the form: {e}")

def find_slots(driver, category):
    """Check if appointment slots are available."""
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "slot"))
        )
        slot_elements = driver.find_elements(By.CLASS_NAME, "slot")
        if slot_elements:
            print(f"Found {len(slot_elements)} slots for category {category}.")
            return True
        else:
            print("No slots found.")
            return False
    except Exception as e:
        print(f"Error finding slots: {e}")
        return False

def handle_captcha(driver, captcha_solver_url, scope):
    """Solve the CAPTCHA and enter the value."""
    try:
        # Wait for CAPTCHA input field to load
        captcha_input = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.ID, f"appointment_captcha_{scope}_captchaText"))
        )
        
        # Solve CAPTCHA using the provided solver
        captcha_value = solve_captcha(driver, captcha_solver_url)
        if not captcha_value:
            print("CAPTCHA solving failed. Skipping this URL.")
            return False
        
        # Enter CAPTCHA and submit
        captcha_input.send_keys(captcha_value)
        captcha_input.send_keys(Keys.RETURN)
        return True

    except Exception as e:
        print(f"Error entering CAPTCHA value: {e}")
        save_screenshot(driver, driver.current_url, "captcha_error")  # Save screenshot for debugging
        return False

def determine_scope(url):
    """Determine if the scope is 'day' or 'month' based on the URL."""
    if "appointment_showDay" in url:
        return "day"
    elif "appointment_showMonth" in url:
        return "month"
    else:
        raise ValueError("URL does not contain a valid scope identifier ('day' or 'month').")

def process_url(url_info, config):
    """Process a single URL for checking slots."""
    category = url_info["category"]
    url = url_info["url"]
    form_data = config["form_data"]
    captcha_solver_url = config["captcha_solver_url"]

    driver = setup_driver()
    try:
        print(f"Checking for slots at: {url}")
        login_and_navigate(driver, url)

        # Determine scope (day or month) based on URL
        scope = determine_scope(url)

        # Handle CAPTCHA
        if not handle_captcha(driver, captcha_solver_url, scope):
            return

        # Check for available slots
        if find_slots(driver, category):
            print(f"Slots found for category {category}. Filling the form.")
            fill_form(driver, form_data, scope)
            save_screenshot(driver, url, category)  # Save screenshot for error
            
        else:
            print(f"No slots available for {url}")

    except Exception as e:
        print(f"An error occurred while processing {url}: {e}")
        save_screenshot(driver, url, category)  # Save screenshot for error
    finally:
        driver.quit()

def check_slots():
    """Check slots for all URLs."""
    config = load_config()
    if not config:
        return

    # Run all URLs simultaneously using threads
    threads = []
    for url_info in config["urls"]:
        thread = threading.Thread(target=process_url, args=(url_info, config))
        threads.append(thread)
        thread.start()

    # Wait for all threads to complete
    for thread in threads:
        thread.join()

def main():
    #check_slots()
    """Main function to schedule daily slot checking."""
    print("Scheduling daily slot checks at 04:00 AM...")
    schedule.every().day.at("04:00").do(check_slots)

    while True:
        schedule.run_pending()
        time.sleep(1)  # Wait before checking the schedule again


if __name__ == "__main__":
    main()
