import requests

def solve_captcha(driver, captcha_solver_url):
    """Solve CAPTCHA using an external API."""
    captcha_element = driver.find_element_by_css_selector("captcha div")
    captcha_style = captcha_element.get_attribute("style")
 
    # Extract the CAPTCHA background image URL
    url_match = captcha_style.match(r"url\(['\"]?([^'\"]+)['\"]?\)")
    if not url_match:
        print("Failed to extract CAPTCHA image URL.")
        return None

    bg_image_url = url_match.group(1)

    # Send the CAPTCHA image URL to the solver
    payload = {"data": bg_image_url}
    try:
        response = requests.post(captcha_solver_url, json=payload)
        response_data = response.json()
        return response_data.get("captcha")  # Assuming the API returns `captcha`
    except Exception as e:
        print(f"Error solving CAPTCHA: {e}")
        return None
