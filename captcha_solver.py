import requests
from selenium.webdriver.common.by import By
import re

def solve_captcha(driver, captcha_solver_url, retries=3):
    """Solve CAPTCHA using an external API with retry logic."""
    for attempt in range(retries):
        try:
            captcha_element = driver.find_element(By.CSS_SELECTOR, "captcha div")
            if not captcha_element:
                print("CAPTCHA element not found.")
                return None

            captcha_style = captcha_element.get_attribute("style")
            #print(f"CAPTCHA style: {captcha_style}")

            url_match = re.search(r"url\(['\"]?([^'\"]+)['\"]?\)", captcha_style)
            if not url_match:
                print("Failed to extract CAPTCHA image URL.")
                return None

            bg_image_url = url_match.group(1)
            #print(f"Extracted CAPTCHA URL: {bg_image_url}")

            payload = {"data": bg_image_url}
            response = requests.post(captcha_solver_url, json=payload)
            response_data = response.json()

            if "captcha" in response_data:
                print(f"CAPTCHA solved: {response_data['captcha']}")
                return response_data["captcha"]
            else:
                print(f"Unexpected response structure: {response_data}")
        except Exception as e:
            print(f"Error solving CAPTCHA on attempt {attempt + 1}: {e}")

    print("Failed to solve CAPTCHA after retries.")
    return None
