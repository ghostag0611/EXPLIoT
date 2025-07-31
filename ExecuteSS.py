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


# === Configuration ===
# Define the project name you want to analyze. Update this value to switch projects.
project_name = "ax50v1_intel-up-ver1-0-7-P1[20200407-rel54193]_signed.bin"  # Change this to the desired project name

# Click on the specified project based on its visible name
row_link = wait.until(EC.element_to_be_clickable((
    By.XPATH,
    f"//p[text()='{project_name}']"
)))
driver.execute_script("arguments[0].click();", row_link)
time.sleep(1)

# Click on the first assessment (typically labeled 'V1')
wait.until(EC.element_to_be_clickable((By.XPATH, "//p[contains(text(), '1.0')]"))).click()
time.sleep(1)

# Navigate to the Firmware section in the left-hand side panel
firmware_element = wait.until(EC.element_to_be_clickable(
    (By.XPATH, "//a[@href='/assessment/firmware']//div[contains(text(), 'Firmware')]")
))

driver.execute_script("arguments[0].scrollIntoView(true);", firmware_element)
time.sleep(0.5)
driver.execute_script("arguments[0].click();", firmware_element)
time.sleep(1)

# Wait for the firmware page content to load
time.sleep(5)  # Adjust if needed based on actual load time
screenshot_dir = "screenshots"
os.makedirs(screenshot_dir, exist_ok=True)

# Identify all 11 clickable elements (adjust selector based on actual structure)
elements = wait.until(EC.presence_of_all_elements_located(
    (By.CSS_SELECTOR, "div.css-5gl46j")))


# Click on the CVE box using its label text
try:
    section_dir = os.path.join(screenshot_dir, "CVE")
    os.makedirs(section_dir, exist_ok=True)
    cve_box = wait.until(EC.element_to_be_clickable(
        (By.XPATH, "//dt[contains(text(), 'CVE')]/ancestor::div[contains(@class, 'css-5gl46j')]")
    ))
    driver.execute_script("arguments[0].scrollIntoView(true);", cve_box)
    time.sleep(1)
    driver.execute_script("arguments[0].click();", cve_box)
    time.sleep(5)  # Wait for content to load after click
    screenshot_path = os.path.join(section_dir, "cve_screenshot.png")
    scroll_height = driver.execute_script("return document.body.scrollHeight")
    viewport_height = driver.execute_script("return window.innerHeight")
    num_scrolls = scroll_height // viewport_height + 1

    for j in range(num_scrolls):
        driver.execute_script(f"window.scrollTo(0, {j * viewport_height});")
        time.sleep(1)
        multi_screenshot_path = os.path.join(section_dir, f"cve_screenshot_part{j+1}.png")
        driver.save_screenshot(multi_screenshot_path)

    driver.back()
    time.sleep(2)
except Exception as e:
    print(f"Error clicking on CVE box: {e}")

# Click on the Binaries box using its label text
try:
    section_dir = os.path.join(screenshot_dir, "Binaries")
    os.makedirs(section_dir, exist_ok=True)
    binaries_box = wait.until(EC.element_to_be_clickable(
        (By.XPATH, "//dt[contains(text(), 'Binaries')]/ancestor::div[contains(@class, 'chakra-stat')]")
    ))
    driver.execute_script("arguments[0].scrollIntoView(true);", binaries_box)
    time.sleep(1)
    driver.execute_script("arguments[0].click();", binaries_box)
    time.sleep(5)  # Wait for content to load after click
    screenshot_path = os.path.join(section_dir, "binaries_screenshot.png")
    scroll_height = driver.execute_script("return document.body.scrollHeight")
    viewport_height = driver.execute_script("return window.innerHeight")
    num_scrolls = scroll_height // viewport_height + 1

    for j in range(num_scrolls):
        driver.execute_script(f"window.scrollTo(0, {j * viewport_height});")
        time.sleep(1)
        multi_screenshot_path = os.path.join(section_dir, f"binaries_screenshot_part{j+1}.png")
        driver.save_screenshot(multi_screenshot_path)
    driver.back()
    time.sleep(2)
except Exception as e:
    print(f"Error clicking on Binaries box: {e}")

# Click on the Passwords box using its label text
try:
    section_dir = os.path.join(screenshot_dir, "Passwords")
    os.makedirs(section_dir, exist_ok=True)
    passwords_box = wait.until(EC.element_to_be_clickable(
        (By.XPATH, "//dt[contains(text(), 'Passwords')]/ancestor::div[contains(@class, 'chakra-stat')]")
    ))
    driver.execute_script("arguments[0].scrollIntoView(true);", passwords_box)
    time.sleep(1)
    driver.execute_script("arguments[0].click();", passwords_box)
    time.sleep(5)  # Wait for content to load after click
    screenshot_path = os.path.join(section_dir, "passwords_screenshot.png")
    scroll_height = driver.execute_script("return document.body.scrollHeight")
    viewport_height = driver.execute_script("return window.innerHeight")
    num_scrolls = scroll_height // viewport_height + 1

    for j in range(num_scrolls):
        driver.execute_script(f"window.scrollTo(0, {j * viewport_height});")
        time.sleep(1)
        multi_screenshot_path = os.path.join(section_dir, f"passwords_screenshot_part{j+1}.png")
        driver.save_screenshot(multi_screenshot_path)
    driver.back()
    time.sleep(2)
except Exception as e:
    print(f"Error clicking on Passwords box: {e}")

# Click on the Cryptography box using its label text
try:
    section_dir = os.path.join(screenshot_dir, "Cryptography")
    os.makedirs(section_dir, exist_ok=True)
    cryptography_box = wait.until(EC.element_to_be_clickable(
        (By.XPATH, "//dt[contains(text(), 'Cryptography')]/ancestor::div[contains(@class, 'chakra-stat')]")
    ))
    driver.execute_script("arguments[0].scrollIntoView(true);", cryptography_box)
    time.sleep(1)
    driver.execute_script("arguments[0].click();", cryptography_box)
    time.sleep(5)  # Wait for content to load after click
    screenshot_path = os.path.join(section_dir, "cryptography_screenshot.png")
    scroll_height = driver.execute_script("return document.body.scrollHeight")
    viewport_height = driver.execute_script("return window.innerHeight")
    num_scrolls = scroll_height // viewport_height + 1

    for j in range(num_scrolls):
        driver.execute_script(f"window.scrollTo(0, {j * viewport_height});")
        time.sleep(1)
        multi_screenshot_path = os.path.join(section_dir, f"cryptography_screenshot_part{j+1}.png")
        driver.save_screenshot(multi_screenshot_path)
    driver.back()
    time.sleep(2)
except Exception as e:
    print(f"Error clicking on Cryptography box: {e}")

# Click on the Strings box using its label text
try:
    section_dir = os.path.join(screenshot_dir, "Strings")
    os.makedirs(section_dir, exist_ok=True)
    strings_box = wait.until(EC.element_to_be_clickable(
        (By.XPATH, "//dt[contains(text(), 'Strings')]/ancestor::div[contains(@class, 'chakra-stat')]")
    ))
    driver.execute_script("arguments[0].scrollIntoView(true);", strings_box)
    time.sleep(1)
    driver.execute_script("arguments[0].click();", strings_box)
    time.sleep(5)  # Wait for content to load after click
    # Instead of full-page scroll, scroll within the scrollable <ul> element
    scroll_container = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "ul.css-955m5e")))
    scroll_height = driver.execute_script("return arguments[0].scrollHeight", scroll_container)
    viewport_height = driver.execute_script("return arguments[0].clientHeight", scroll_container)
    num_scrolls = scroll_height // viewport_height + 1

    for j in range(num_scrolls):
        driver.execute_script("arguments[0].scrollTop = arguments[1];", scroll_container, j * viewport_height)
        time.sleep(1)
        # Scroll container into view and adjust window to its height
        driver.execute_script("arguments[0].scrollIntoView(true);", scroll_container)
        container_height = driver.execute_script("return arguments[0].clientHeight", scroll_container)
        driver.set_window_size(1920, container_height + 200)
        multi_screenshot_path = os.path.join(section_dir, f"strings_screenshot_part{j+1}.png")
        driver.save_screenshot(multi_screenshot_path)
    driver.back()
    time.sleep(2)
except Exception as e:
    print(f"Error clicking on Strings box: {e}")

# Click on the URLs box using its label text
try:
    section_dir = os.path.join(screenshot_dir, "URLs")
    os.makedirs(section_dir, exist_ok=True)
    urls_box = wait.until(EC.element_to_be_clickable(
        (By.XPATH, "//dt[contains(text(), 'URL')]/ancestor::div[contains(@class, 'chakra-stat')]")
    ))
    driver.execute_script("arguments[0].scrollIntoView(true);", urls_box)
    time.sleep(1)
    driver.execute_script("arguments[0].click();", urls_box)
    time.sleep(10)
    screenshot_path = os.path.join(section_dir, "urls_screenshot.png")
    scroll_height = driver.execute_script("return document.body.scrollHeight")
    viewport_height = driver.execute_script("return window.innerHeight")
    num_scrolls = scroll_height // viewport_height + 1

    for j in range(num_scrolls):
        driver.execute_script(f"window.scrollTo(0, {j * viewport_height});")
        time.sleep(1)
        multi_screenshot_path = os.path.join(section_dir, f"urls_screenshot_part{j+1}.png")
        driver.save_screenshot(multi_screenshot_path)
    driver.back()
    time.sleep(2)
except Exception as e:
    print(f"Error clicking on URLs box: {e}")

# Click on the Addresses box using its label text
try:
    section_dir = os.path.join(screenshot_dir, "Addresses")
    os.makedirs(section_dir, exist_ok=True)
    addresses_box = wait.until(EC.element_to_be_clickable(
        (By.XPATH, "//dt[contains(text(), 'Address')]/ancestor::div[contains(@class, 'chakra-stat')]")
    ))
    driver.execute_script("arguments[0].scrollIntoView(true);", addresses_box)
    time.sleep(1)
    driver.execute_script("arguments[0].click();", addresses_box)
    time.sleep(5)
    screenshot_path = os.path.join(section_dir, "addresses_screenshot.png")
    scroll_height = driver.execute_script("return document.body.scrollHeight")
    viewport_height = driver.execute_script("return window.innerHeight")
    num_scrolls = scroll_height // viewport_height + 1

    for j in range(num_scrolls):
        driver.execute_script(f"window.scrollTo(0, {j * viewport_height});")
        time.sleep(1)
        multi_screenshot_path = os.path.join(section_dir, f"addresses_screenshot_part{j+1}.png")
        driver.save_screenshot(multi_screenshot_path)
    driver.back()
    time.sleep(2)
except Exception as e:
    print(f"Error clicking on Addresses box: {e}")

# Click on the SBOM box using its heading text
try:
    section_dir = os.path.join(screenshot_dir, "SBOM")
    os.makedirs(section_dir, exist_ok=True)
    sbom_box = wait.until(EC.element_to_be_clickable(
        (By.XPATH, "//h2[text()='SBOM']/ancestor::div[contains(@class, 'css-5xsoen')]")
    ))
    driver.execute_script("arguments[0].scrollIntoView(true);", sbom_box)
    time.sleep(1)
    driver.execute_script("arguments[0].click();", sbom_box)
    time.sleep(5)
    screenshot_path = os.path.join(section_dir, "sbom_screenshot.png")
    scroll_height = driver.execute_script("return document.body.scrollHeight")
    viewport_height = driver.execute_script("return window.innerHeight")
    num_scrolls = scroll_height // viewport_height + 1

    for j in range(num_scrolls):
        driver.execute_script(f"window.scrollTo(0, {j * viewport_height});")
        time.sleep(1)
        multi_screenshot_path = os.path.join(section_dir, f"sbom_screenshot_part{j+1}.png")
        driver.save_screenshot(multi_screenshot_path)
    driver.back()
    time.sleep(2)
except Exception as e:
    print(f"Error clicking on SBOM box: {e}")

# Click on the Files box
try:
    section_dir = os.path.join(screenshot_dir, "Files")
    os.makedirs(section_dir, exist_ok=True)
    files_box = wait.until(EC.element_to_be_clickable(
        (By.XPATH, "//h2[text()='Files']/ancestor::div[contains(@class, 'css-5xsoen')]")
    ))
    driver.execute_script("arguments[0].scrollIntoView(true);", files_box)
    time.sleep(1)
    driver.execute_script("arguments[0].click();", files_box)
    time.sleep(5)
    screenshot_path = os.path.join(section_dir, "files_screenshot.png")
    scroll_height = driver.execute_script("return document.body.scrollHeight")
    viewport_height = driver.execute_script("return window.innerHeight")
    num_scrolls = scroll_height // viewport_height + 1

    for j in range(num_scrolls):
        driver.execute_script(f"window.scrollTo(0, {j * viewport_height});")
        time.sleep(1)
        multi_screenshot_path = os.path.join(section_dir, f"files_screenshot_part{j+1}.png")
        driver.save_screenshot(multi_screenshot_path)
    driver.back()
    time.sleep(2)
except Exception as e:
    print(f"Error clicking on Files box: {e}")

# Click on the Packages box
try:
    section_dir = os.path.join(screenshot_dir, "Packages")
    os.makedirs(section_dir, exist_ok=True)
    packages_box = wait.until(EC.element_to_be_clickable(
        (By.XPATH, "//h2[text()='Packages']/ancestor::div[contains(@class, 'css-5xsoen')]")
    ))
    driver.execute_script("arguments[0].scrollIntoView(true);", packages_box)
    time.sleep(1)
    driver.execute_script("arguments[0].click();", packages_box)
    time.sleep(5)
    # Instead of full-page scroll, scroll within the scrollable package container
    scroll_container = wait.until(EC.presence_of_element_located(
        (By.XPATH, "//*[@id='tabs-:r2:--tabpanel-0']/div/div[2]/div[2]/div/div[3]/div/div[1]")))
    scroll_height = driver.execute_script("return arguments[0].scrollHeight", scroll_container)
    viewport_height = driver.execute_script("return arguments[0].clientHeight", scroll_container)
    num_scrolls = scroll_height // viewport_height + 1

    for j in range(num_scrolls):
        driver.execute_script("arguments[0].scrollTop = arguments[1];", scroll_container, j * viewport_height)
        time.sleep(1)
        driver.execute_script("arguments[0].scrollIntoView(true);", scroll_container)
        container_height = driver.execute_script("return arguments[0].clientHeight", scroll_container)
        driver.set_window_size(1920, container_height + 200)
        multi_screenshot_path = os.path.join(section_dir, f"packages_screenshot_part{j+1}.png")
        driver.save_screenshot(multi_screenshot_path)
    driver.back()
    time.sleep(2)
except Exception as e:
    print(f"Error clicking on Packages box: {e}")

# Click on the Services box
try:
    section_dir = os.path.join(screenshot_dir, "Services")
    os.makedirs(section_dir, exist_ok=True)
    services_box = wait.until(EC.element_to_be_clickable(
        (By.XPATH, "//h2[text()='Services']/ancestor::div[contains(@class, 'css-5xsoen')]")
    ))
    driver.execute_script("arguments[0].scrollIntoView(true);", services_box)
    time.sleep(1)
    driver.execute_script("arguments[0].click();", services_box)
    time.sleep(5)
    screenshot_path = os.path.join(section_dir, "services_screenshot.png")
    scroll_height = driver.execute_script("return document.body.scrollHeight")
    viewport_height = driver.execute_script("return window.innerHeight")
    num_scrolls = scroll_height // viewport_height + 1

    for j in range(num_scrolls):
        driver.execute_script(f"window.scrollTo(0, {j * viewport_height});")
        time.sleep(1)
        multi_screenshot_path = os.path.join(section_dir, f"services_screenshot_part{j+1}.png")
        driver.save_screenshot(multi_screenshot_path)
    driver.back()
    time.sleep(2)
except Exception as e:
    print(f"Error clicking on Services box: {e}")

for i, elem in enumerate(elements[:11]):  # Ensure only 11 are processed
    try:
        section_dir = os.path.join(screenshot_dir, f"FullPage_{i+1}")
        os.makedirs(section_dir, exist_ok=True)
        driver.execute_script("arguments[0].scrollIntoView(true);", elem)
        time.sleep(1)
        driver.execute_script("arguments[0].click();", elem)
        time.sleep(5)  # Wait for any modal/load to complete
        screenshot_path = os.path.join(section_dir, f"fullpage_screenshot_{i+1}.png")
        driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(1)
        scroll_height = driver.execute_script("return document.body.scrollHeight")
        driver.set_window_size(1920, scroll_height + 200)
        driver.save_screenshot(screenshot_path)
        driver.back()
        time.sleep(2)
        if i < 10:  # Only re-fetch if not the last element
            elements = wait.until(EC.presence_of_all_elements_located(
                (By.CSS_SELECTOR, "div.css-5gl46j")))
    except Exception as e:
        print(f"Error handling element {i+1}: {e}")

print("All screenshots captured.")

# Note: Screenshots in the 'screenshots' directory can be compiled into a PDF using tools like img2pdf, Pillow, or a separate script.

import os
from PIL import Image

# Define the base screenshots path
base_path = "/Users/ag/Payatu/Selenium/screenshots"

# Supported image formats
image_extensions = [".png", ".jpg", ".jpeg", ".bmp", ".tiff", ".webp"]

# Function to convert images in a folder to a PDF
def images_to_pdf(folder_path):
    images = []
    for file in sorted(os.listdir(folder_path)):
        file_path = os.path.join(folder_path, file)
        if os.path.isfile(file_path) and os.path.splitext(file)[1].lower() in image_extensions:
            try:
                img = Image.open(file_path).convert("RGB")
                images.append(img)
            except Exception as e:
                print(f"Error loading image {file_path}: {e}")
    
    if images:
        folder_name = os.path.basename(folder_path)
        output_path = os.path.join(folder_path, f"{folder_name} output.pdf")
        images[0].save(output_path, save_all=True, append_images=images[1:])
        print(f"Saved PDF in: {output_path}")
    else:
        print(f"No valid images found in: {folder_path}")

# Iterate through all folders in the base_path
for folder in sorted(os.listdir(base_path)):
    folder_path = os.path.join(base_path, folder)
    if os.path.isdir(folder_path):
        images_to_pdf(folder_path)

        
