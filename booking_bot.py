import os
import time
import json
import threading
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
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
    """Set up the Selenium WebDriver."""
    service = webdriver.chrome.service.Service(ChromeDriverManager().install())
    options = webdriver.ChromeOptions()
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    return webdriver.Chrome(service=service, options=options)


def determine_scope(driver):
    """Determine if the page is for 'day' or 'month' scope."""
    try:
        if "appointment_showDay" in driver.current_url:
            return "day"
        elif "appointment_showMonth" in driver.current_url:
            return "month"
        else:
            raise ValueError("Unable to determine scope (day or month) from the URL.")
    except Exception as e:
        print(f"Error determining scope: {e}")
        return None


def handle_captcha(driver, captcha_solver_url, scope):
    """Solve the CAPTCHA and enter the value."""
    try:
        captcha_input = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.ID, f"appointment_captcha_{scope}_captchaText"))
        )

        captcha_value = solve_captcha(driver, captcha_solver_url)
        if not captcha_value:
            print("CAPTCHA solving failed. Exiting.")
            return False

        print(f"CAPTCHA solved: {captcha_value}")
        captcha_input.clear()
        captcha_input.send_keys(captcha_value)
        captcha_input.send_keys(Keys.RETURN)
        #time.sleep(2)
        return True
    except TimeoutException:
        print(f"No CAPTCHA input field found for scope '{scope}'. Skipping CAPTCHA.")
        return True  # Proceed if no CAPTCHA
    except Exception as e:
        print(f"Error entering CAPTCHA value: {e}")
        save_screenshot(driver, driver.current_url, f"{scope}_captcha_error")
        return False


def find_available_slot(driver):
    """Locate the first available appointment slot."""
    try:
        slots = driver.find_elements(By.XPATH, "//a[contains(@href, 'appointment_showForm.do')]")
        if slots:
            print(f"Found {len(slots)} slots available.")
            return slots[0].get_attribute("href")  # Return the first available slot link
        print("No available slots found.")
        return None
    except NoSuchElementException:
        print("No slots found on the page.")
        return None


def process_url(url_info, config):
    """Process a single URL for checking slots and filling forms."""
    category = url_info["category"]
    url = url_info["url"]
    form_data = config["form_data"]
    captcha_solver_url = config["captcha_solver_url"]

    driver = setup_driver()
    try:
        print(f"Checking for slots at: {url}")
        driver.get(url)
        time.sleep(2)

        # Determine scope (day or month)
        scope = determine_scope(driver)
        if scope is None:
            print("Failed to determine scope. Exiting.")
            return

        # Handle CAPTCHA for the first page
        if not handle_captcha(driver, captcha_solver_url, scope):
            return

        # Check for slots
        slot_link = find_available_slot(driver)
        if slot_link:
            print(f"Navigating to the booking form: {slot_link}")
            driver.get(slot_link)

            # Handle CAPTCHA for the final form
            if handle_captcha(driver, captcha_solver_url, "newAppointmentForm"):
                print("Filling out the final form.")
                fill_final_form(driver, form_data)
            else:
                print("Failed CAPTCHA for final form. Terminating.")
        else:
            print("No slots available. Exiting.")

    except Exception as e:
        print(f"An error occurred while processing {url}: {e}")
    finally:
        driver.quit()


def fill_final_form(driver, form_data):
    """Fill the final form fields."""
    try:
        driver.find_element(By.ID, "appointment_newAppointmentForm_lastname").send_keys(form_data["lastname"])
        driver.find_element(By.ID, "appointment_newAppointmentForm_firstname").send_keys(form_data["firstname"])
        driver.find_element(By.ID, "appointment_newAppointmentForm_email").send_keys(form_data["email"])
        driver.find_element(By.ID, "appointment_newAppointmentForm_emailrepeat").send_keys(form_data["email"])
        driver.find_element(By.ID, "appointment_newAppointmentForm_fields_0__content").send_keys(form_data["passport"])

        # Submit the form
        driver.find_element(By.ID, "appointment_newAppointmentForm_appointment_addAppointment").click()
        print("Form submitted successfully.")
    except Exception as e:
        print(f"Error while filling the final form: {e}")


def save_screenshot(driver, url, category):
    """Save a screenshot with a unique name based on the URL or category."""
    screenshot_dir = "screenshots"
    if not os.path.exists(screenshot_dir):
        os.makedirs(screenshot_dir)
    filename = f"{category}_{url.split('/')[-1]}.png"
    screenshot_path = os.path.join(screenshot_dir, filename)
    driver.save_screenshot(screenshot_path)
    print(f"Screenshot saved: {screenshot_path}")


def check_slots():
    """Check slots for all URLs."""
    config = load_config()
    if not config:
        return

    threads = []
    for url_info in config["urls"]:
        thread = threading.Thread(target=process_url, args=(url_info, config))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()


def main():
    print("Starting the bot...")
    check_slots()


if __name__ == "__main__":
    main()
