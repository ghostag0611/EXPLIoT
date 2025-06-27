from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
import re

# Import required libraries

# === Configuration ===
# Set the project name to be used for navigation
project_name = "your_project_name"  # Change this to the desired project name

# === Setup ===
# Configure Chrome WebDriver options and initialize the driver
chrome_options = Options()
chrome_options.add_argument("--new-window")
chrome_options.add_argument('--user-data-dir=' + os.path.expanduser('~/selenium-profile'))  
chrome_options.add_argument('--profile-directory=Profile 1')  
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

service = Service('/Users/ag/.bin/chromedriver')  
driver = webdriver.Chrome(service=service, options=chrome_options)
time.sleep(1)

# Navigate to the login page of Expliot and log in if not already logged in
driver.get("https://community.expliot.io/login")
wait = WebDriverWait(driver, 10)
time.sleep(1)

# Try logging in using email and password if on login page
login_url = driver.current_url
try:
    if "login" in login_url:
        email_field = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='email'][placeholder='Email']")))
        password_field = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='password'][placeholder='Password']")))

        email_field.click()
        email_field.send_keys("your_email_address")
        password_field.click()
        password_field.send_keys("your_password")

        login_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']")))
        login_button.click()
        time.sleep(1)
except Exception as e:
    print(f"Login may have already occurred or failed: {e}")

time.sleep(1)

# Click on the desired project by its name
row_link = wait.until(EC.element_to_be_clickable((
    By.XPATH,
    f"//p[text()='{project_name}']"
)))
driver.execute_script("arguments[0].click();", row_link)
time.sleep(1)

# Click on the first available assessment (e.g., 'V1')
wait.until(EC.element_to_be_clickable((By.XPATH, "//p[contains(text(), 'V1')]"))).click()
time.sleep(1)

# Navigate to the Firmware tab using side navigation
firmware_element = wait.until(EC.element_to_be_clickable(
    (By.XPATH, "//a[@href='/assessment/firmware']//div[contains(text(), 'Firmware')]")
))
driver.execute_script("arguments[0].scrollIntoView(true);", firmware_element)
time.sleep(0.5)
driver.execute_script("arguments[0].click();", firmware_element)
time.sleep(1)


# Scroll to and click the 'Packages' section header
# Save the URL of the Packages page to reload it later in the loop
driver.execute_script("window.scrollBy(0, 1000);")
packages_element = wait.until(EC.element_to_be_clickable(
    (By.XPATH, "//h2[contains(text(), 'Packages')]")
))
driver.execute_script("arguments[0].scrollIntoView(true);", packages_element)
time.sleep(0.5)
driver.execute_script("arguments[0].click();", packages_element)
time.sleep(1)

package_url = driver.current_url


# Initialize dictionary to store extracted package and CVE data
data1 = {}

# Extract all package names from the page
package_blocks = driver.find_elements(By.CSS_SELECTOR, "div.css-3ajk5, div.css-itplzt")
package_headings = []
for block in package_blocks:
    title_attr = block.get_attribute("title")
    if title_attr:
        clean_title = title_attr.strip()
        if clean_title not in package_headings:
            package_headings.append(clean_title)
    else:
        try:
            h2 = block.find_element(By.TAG_NAME, "h2")
            clean_title = h2.text.strip()
            if clean_title not in package_headings:
                package_headings.append(clean_title)
        except:
            continue

# Filter package names to avoid duplicates and unwanted entries
package_headings = [
    h for h in package_headings
    if h.strip() and not (
        h.endswith(")0") or
        (len(h) > 1 and h[-1] == "0" and not h[-2].isdigit())
    )
]

print(f"Found {len(package_headings)} packages with CVEs")

# Iterate through all package names to collect CVE data
for heading in package_headings:
    try:
        if not heading.strip():
            continue

        # Reload the Packages page before processing each package to avoid stale element errors
        driver.get(package_url)
        time.sleep(2)

        # Locate the correct package block and click it
        # Handle case where package name may be truncated with '...'
        pkg_blocks = driver.find_elements(By.CSS_SELECTOR, "div.css-3ajk5, div.css-itplzt")
        for block in pkg_blocks:
            try:
                h2 = block.find_element(By.TAG_NAME, "h2")
                visible = h2.text.strip()
                if visible[-5:-2] == "...":
                    # Hover to trigger tooltip
                    webdriver.ActionChains(driver).move_to_element(h2).perform()
                    title_attr = h2.get_attribute("title") or block.get_attribute("title")
                    match_heading = title_attr.strip() if title_attr else visible
                else:
                    match_heading = visible

                if match_heading.strip() == heading.strip():
                    driver.execute_script("arguments[0].scrollIntoView(true);", block)
                    time.sleep(0.5)
                    driver.execute_script("arguments[0].click();", block)
                    break
            except:
                continue
        else:
            raise Exception(f"No clickable element matched title: {heading}")
        time.sleep(2)

        try:
            name_elem = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "h2.chakra-heading.css-5lyheq")))
            name = name_elem.text.strip()
        except:
            name = ""

        try:
            version_elem = driver.find_element(By.XPATH, "//h2[text()='Version']/following-sibling::p")
            version = version_elem.text.strip()
        except:
            version = ""

        if not name:
            continue

        # Wait for CVEs to load after clicking the package
        try:
            wait.until(EC.presence_of_all_elements_located((By.XPATH, "//h2[text()='CVEs']/following-sibling::div[1]//li")))
            time.sleep(1)  # buffer to ensure all CVEs are rendered
        except:
            print(f"Timeout waiting for CVEs for {name}")

        # Extract all CVE identifiers listed for the current package
        cve_elements = driver.find_elements(By.XPATH, "//h2[text()='CVEs']/following-sibling::div[1]//li")
        cves = set()
        for el in cve_elements:
            full_text = el.get_attribute("innerText").strip()
            if full_text.startswith("CVE-"):
                cves.add(full_text)
        cves = sorted(cves)  # convert to sorted list

        # Extract CPE name
        try:
            cpe_elem = driver.find_element(By.XPATH, "//h2[text()='cpe name']/following-sibling::p")
            cpe_name = cpe_elem.text.strip()
        except:
            cpe_name = ""

        # Save the extracted information into the data dictionary
        data1[name] = {
            "package_name": name,
            "package_version": version,
            "cpe_name": cpe_name,
            "cve_count": len(cves),
            "cves": cves
        }

    # Handle exceptions gracefully and print error message if package processing fails
    except Exception as e:
        print(f"Error processing package '{heading}': {e}")

# Close the browser after data collection is complete
driver.quit()

# Save the collected package data with CVEs into a JSON file in the same directory as the script
import json
output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "package_data.json")
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(data1, f, indent=4)
print("Data saved to package_data.json")
