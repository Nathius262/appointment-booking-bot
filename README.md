# Appointment Booking Bot

A Python-based bot to automate the process of checking appointment availability and booking slots on the German consulate appointment system.

## Features
- Scrapes appointment availability for specific dates and months.
- Automatically solves CAPTCHAs using OCR or third-party services.
- Submits form data dynamically based on user inputs or configuration.
- Handles multiple steps in the appointment booking workflow:
  1. View monthly availability.
  2. Narrow down to available slots on a specific day.
  3. Book the desired appointment.

## Prerequisites
- Python 3.8+
- Chrome WebDriver (compatible with your version of Google Chrome)
- Required Python libraries (install via `requirements.txt`)

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/appointment-booking-bot.git
   cd appointment-booking-bot

2. Install dependencies:

```bash
  pip install -r requirements.txt
```

3. Download and install Chrome WebDriver:

  Ensure it matches your installed version of Google Chrome.
  Download here.
  
## Configuration
Update the config.json file (if included) with your preferences, e.g., locationCode, realmId, categoryId, and dates.
Alternatively, provide inputs directly in the script.

## Usage
1. Run the bot:

``` bash
python booking_bot.py
```

2. The bot will:

  - Check the availability of appointments for a specific month.
  - Loop through available dates and fetch time slots.
  - Solve CAPTCHA dynamically.
  - Optionally book an available appointment.
3. Results will be logged in the console or saved to an output file.

## Files
`booking_bot.py:` Main script that implements the bot functionality.

`captcha_solver.py:` Handles CAPTCHA solving using OCR or APIs.

`config.json:` Configuration file for user input and bot settings.

`requirements.txt:` Python dependencies for the project.

## Example Workflow
1. Start by viewing the monthly calendar:
Fetch and print all available dates.
2. Navigate to specific days:
Scrape and display available time slots.
3. Fill out the form and book the appointment:
Submit user details and solve CAPTCHA.

## CAPTCHA Solving
This bot uses a placeholder method for solving CAPTCHA. Replace the logic in captcha_solver.py with one of the following:

## OCR (e.g., Tesseract).
Third-party CAPTCHA-solving services (e.g., 2Captcha).

## Disclaimer
This project is for educational purposes only.
Ensure compliance with the website's terms of service before using this bot.


## License
This project is licensed under the MIT License.

## Contributing
Contributions are welcome! Feel free to fork the repository and submit a pull request.

## Contact
For questions or support, create an issue on the repository or contact me at egbodonathaniel@gamil.com.

