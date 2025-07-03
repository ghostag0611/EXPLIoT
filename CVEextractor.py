from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
import re

# === Configuration ===
# Define the project name you want to analyze. Update this value to switch projects.
project_name = "SP_sample-3.ima"  # Change this to the desired project name

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
        email_field.send_keys("na24b021@smail.iitm.ac.in")
        password_field.click()
        password_field.send_keys("dgadcEcuo1l")

        login_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']")))
        login_button.click()
        time.sleep(1)
except Exception as e:
    print(f"Login may have already occurred or failed: {e}")

time.sleep(1)

# Click on the specified project based on its visible name
row_link = wait.until(EC.element_to_be_clickable((
    By.XPATH,
    f"//p[text()='{project_name}']"
)))
driver.execute_script("arguments[0].click();", row_link)
time.sleep(1)

# Click on the first assessment (typically labeled 'V1')
wait.until(EC.element_to_be_clickable((By.XPATH, "//p[contains(text(), 'V1')]"))).click()
time.sleep(1)

# Navigate to the Firmware section in the left-hand side panel
firmware_element = wait.until(EC.element_to_be_clickable(
    (By.XPATH, "//a[@href='/assessment/firmware']//div[contains(text(), 'Firmware')]")
))
driver.execute_script("arguments[0].scrollIntoView(true);", firmware_element)
time.sleep(0.5)
driver.execute_script("arguments[0].click();", firmware_element)
time.sleep(1)


# Scroll to the Packages section and click it; store the resulting URL for future reloads
driver.execute_script("window.scrollBy(0, 1000);")
packages_element = wait.until(EC.element_to_be_clickable(
    (By.XPATH, "//h2[contains(text(), 'Packages')]")
))
driver.execute_script("arguments[0].scrollIntoView(true);", packages_element)
time.sleep(0.5)
driver.execute_script("arguments[0].click();", packages_element)
time.sleep(1)

package_url = driver.current_url


# === Data Extraction ===
# Initialize dictionary to store package and CVE information
data1 = {}

# Locate package blocks and extract their headings, including hover-based full titles when truncated
package_blocks = driver.find_elements(By.CSS_SELECTOR, "div.css-1jlpasf, div.css-13igt5i")
package_headings = []
for block in package_blocks:
    try:
        name_elem = block.find_element(By.CSS_SELECTOR, "p.chakra-text.css-5crqjj")
        version_elem = block.find_element(By.CSS_SELECTOR, "p.chakra-text.css-669a8z")
        visible = f"{name_elem.text.strip()}({version_elem.text.strip()})"
    except:
        continue

    # Extract CVE count from the badge
    try:
        badge_elem = block.find_element(By.CSS_SELECTOR, "span.chakra-badge")
        cve_count_text = badge_elem.text.strip()
        if cve_count_text.isdigit() and int(cve_count_text) > 0:
            if visible not in package_headings:
                package_headings.append(visible)
    except:
        continue

print(f"Found {len(package_headings)} packages with CVEs")

# For each package heading, reload the Packages page to reset the view
for heading in package_headings:
    try:
        if not heading.strip():
            continue

        driver.get(package_url)
        time.sleep(2)

        # Locate the matching package block, hover if needed, and click to open details in the right pane
        pkg_blocks = driver.find_elements(By.CSS_SELECTOR, "div.css-1jlpasf, div.css-13igt5i")
        for block in pkg_blocks:
            try:
                name_elem = block.find_element(By.CSS_SELECTOR, "p.chakra-text.css-5crqjj")
                version_elem = block.find_element(By.CSS_SELECTOR, "p.chakra-text.css-669a8z")
                visible = f"{name_elem.text.strip()}({version_elem.text.strip()})"

                if visible.strip() == heading.strip():
                    driver.execute_script("arguments[0].scrollIntoView(true);", block)
                    time.sleep(0.5)
                    driver.execute_script("arguments[0].click();", block)
                    break
            except:
                continue
        else:
            raise Exception(f"No clickable element matched title: {heading}")
        time.sleep(2)

        # After clicking, extract the package name and version from the right pane
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

        # Wait until CVE data is rendered in the CVEs section
        try:
            wait.until(EC.presence_of_all_elements_located((By.XPATH, "//h2[text()='CVEs']/following-sibling::div[1]//li")))
            time.sleep(1)
        except:
            print(f"Timeout waiting for CVEs for {name}")

        # Extract all CVE IDs (e.g., CVE-2023-xxxx) from the CVEs list
        cve_elements = driver.find_elements(By.XPATH, "//h2[text()='CVEs']/following-sibling::div[1]//li")
        cves = set()
        for el in cve_elements:
            full_text = el.get_attribute("innerText").strip()
            if full_text.startswith("CVE-"):
                cves.add(full_text)
        cves = sorted(cves)

        # Extract the corresponding CPE name listed in the right pane
        try:
            cpe_elem = driver.find_element(By.XPATH, "//h2[text()='cpe name']/following-sibling::p")
            cpe_name = cpe_elem.text.strip()
        except:
            cpe_name = ""

        # Store all gathered data into the output dictionary under the package name key
        data1[name] = {
            "package_name": name,
            "package_version": version,
            "cpe_name": cpe_name,
            "cve_count": len(cves),
            "cves": cves
        }

    # Log and skip any package that causes an error during processing
    except Exception as e:
        print(f"Error processing package '{heading}': {e}")

# === Save & Exit ===
# Close the browser and write the final data to a JSON file in the same folder as this script
driver.quit()

import json
output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "package_data.json")
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(data1, f, indent=4)
print("Data saved to package_data.json")
