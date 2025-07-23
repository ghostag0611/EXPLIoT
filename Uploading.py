from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
import re


# === Setup ===
# Initialize Chrome browser with a persistent user profile to retain session data (e.g., cookies)
chrome_options = Options()
chrome_options.add_argument("--new-window")
chrome_options.add_argument('--user-data-dir=' + os.path.expanduser('~/selenium-profile'))  
chrome_options.add_argument('--profile-directory=Profile 1')  
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

service = Service('/Users/ag/.bin/chromedriver')  
driver = webdriver.Chrome(service=service, options=chrome_options)
time.sleep(1)

# Navigate to Expliot login page and attempt to log in
driver.get("https://community.expliot.io/login")
wait = WebDriverWait(driver, 10)
time.sleep(1)

# Wait for email and password fields to load, input credentials, and click login
login_url = driver.current_url
try:
    if "login" in login_url:
        email_field = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='email'][placeholder='Email']")))
        password_field = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='password'][placeholder='Password']")))

        email_field.click()
        email_field.send_keys("email_address")
        password_field.click()
        password_field.send_keys("password")

        login_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']")))
        login_button.click()
        time.sleep(1)
except Exception as e:
    print(f"Login may have already occurred or failed: {e}")

time.sleep(1)

# === Create New Project ===
try:
    start_project_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[.//p[text()='Start New Project']]")))
    start_project_button.click()

    browse_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@class='chakra-button css-dj0jog']")))
    driver.execute_script("arguments[0].click();", browse_button)


    # Wait for upload details and continue button
    continue_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Continue')]")))
    continue_button.click()

    # Wait for scan to complete
    WebDriverWait(driver, 600).until(
        EC.text_to_be_present_in_element(
            (By.XPATH, "//div[contains(@class, 'scan-progress')]"),
            "100%"
        )
    )

    # Wait until status says "Done"
    WebDriverWait(driver, 600).until(
        EC.text_to_be_present_in_element(
            (By.XPATH, "//p[contains(@class, 'chakra-text') and text()='done']"),
            "done"
        )
    )

    print("Scan completed successfully.")
except Exception as e:
    print(f"Error during project creation or scan: {e}")
