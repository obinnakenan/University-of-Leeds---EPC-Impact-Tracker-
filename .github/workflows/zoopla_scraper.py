import re
import os
import pandas as pd
from datetime import datetime
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Constants
TIMEOUT = 5
search = ['LS1']
BASE_URL = "https://www.zoopla.co.uk/to-rent/property/{outcode}/?price_frequency=per_month&q={outcode}&search_source=home&recent_search=true&pn="

def get_headless_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless=chrome")  # Changed from 'new' for stability
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36")
    return Chrome(options=chrome_options)

def etext(e: WebElement) -> str:
    try:
        return e.text.strip() if e.text else e.get_property("textContent").strip()
    except:
        return ""

def click(driver, e):
    ActionChains(driver).click(e).perform()

def get_all(driver, css):
    try:
        wait = WebDriverWait(driver, TIMEOUT)
        return wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, css)))
    except TimeoutException:
        return []

def click_through(driver):
    try:
        wait = WebDriverWait(driver, TIMEOUT)
        button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-testid='uc-deny-all-button']")))
        print("✅ Cookie popup found. Clicking deny all.")
        click(driver, button)
    except Exception as e:
        print(f"ℹ️ No cookie popup or error dismissing: {e}")

def get_details(driver, listing_url):
    driver2 = get_headless_driver()
    driver2.get(listing_url)
    click_through(driver2)

    def extract_from_json(text, pattern):
        match = re.search(pattern, text)
        return match.group(1) if match else 'N/A'

    def find_and_extract(pattern, regex):
        try:
            raw = etext(WebDriverWait(driver2, 5).until(EC.presence_of_element_located((By.XPATH, f"//*[contains(text(), '{pattern}')]"))))
            return extract_from_json(raw, regex)
        except:
            return "N/A"

    epc_rating = find_and_extract("EPC rating", r"(EPC rating.*?)\s")
    stations = ",".join([etext(e) for e in get_all(driver2, "div.b1ub3l4")])
    schools = ",".join([etext(e) for e in get_all(driver2, "div.b1ub3l7")])
    longitude = find_and_extract("longitude", r'"longitude":(-?\d+\.\d+)')
    latitude = find_and_extract("latitude", r'"latitude":(-?\d+\.\d+)')
    postalCode = find_and_extract("postalCode", r'"postalCode":"([^"]+)"')
    uprn = find_and_extract("uprn", r'"uprn":"(\d+)"')
    county_area_name = find_and_extract("county_area_name", r'"county_area_name":"(.*?)"')
    post_town_name = find_and_extract("post_town_name", r'"post_town_name":"(.*?)"')
    price_actual = find_and_extract("price_actual", r'"price_actual":"(\d+)"')
    price_max = find_and_extract("price_max", r'"price_max":"(\d+)"')
    price_min = find_and_extract("price_min", r'"price_min":"(\d+)"')
    property_type = find_and_extract("property_type", r'"property_type":"(.*?)"')
    region_name = find_and_extract("region_name", r'"region_name":"(.*?)"')

    try:
        council_tax_raw = etext(WebDriverWait(driver2, 5).until(EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Council')]"))))
        council_tax = re.findall(r"Council\s*tax\s*band?[\s:,\"]*\s*([A-F])", council_tax_raw) or ['N/A']
    except:
        council_tax = ['N/A']

    driver2.quit()
    return epc_rating, stations, schools, longitude, latitude, postalCode, uprn, county_area_name, post_town_name, price_actual, price_max, price_min, property_type, region_name, ",".join(council_tax)

def scrape_page(driver, page_num):
    result = []
    cards = get_all(driver, "div._19tyedx0")
    print(f"🔎 Found {len(cards)} listings on page {page_num}.")

    # Take screenshot for debugging
    screenshot_name = f"output/debug_page_{page_num}.png"
    driver.save_screenshot(screenshot_name)
    print(f"🖼️ Screenshot saved: {screenshot_name}")

    for house in cards:
        try:
            listing_url = house.find_element(By.XPATH, ".//*[starts-with(@href, '/to-rent/')]").get_attribute("href")
            details = get_details(driver, listing_url)
            epc_rating, stations, schools, longitude, latitude, postalCode, uprn, county_area_name, post_town_name, price_actual, price_max, price_min, property_type, region_name, council_tax = details

            Amount = etext(house.find_element(By.XPATH, ".//*[contains(text(),'pcm')]"))
            Amount_per_week = etext(house.find_element(By.XPATH, ".//*[contains(text(),'pw')]"))
            Address = etext(house.find_element(By.CSS_SELECTOR, "address"))
            Number_of_rooms = etext(house.find_element(By.XPATH, ".//*[contains(text(),'bed')]"))
            Number_of_bath = etext(house.find_element(By.XPATH, ".//*[contains(text(),'bath')]"))
            Reception = etext(house.find_element(By.XPATH, ".//*[contains(text(),'reception')]"))
            Square_foot = etext(house.find_element(By.XPATH, ".//*[contains(text(),'sq. ft')]"))

            result.append({
                "Amount": Amount, "Amount per week": Amount_per_week, "Address": Address,
                "Number of rooms": Number_of_rooms, "Number of Bath": Number_of_bath,
                "Reception": Reception, "Square foot": Square_foot, "EPC Rating": epc_rating,
                "Nearby Stations": stations, "Nearby Schools": schools, "Longitude": longitude,
                "Latitude": latitude, "postalCode": postalCode, "UPRN": uprn,
                "County area name": county_area_name, "Post town name": post_town_name,
                "Price actual": price_actual, "Price max": price_max, "Price min": price_min,
                "Property type": property_type, "Region name": region_name,
                "Council tax": council_tax, "Listing URL": listing_url
            })

        except Exception as e:
            print(f"⚠️ Skipped a listing due to error: {e}")
            continue

    return result

# Main script execution
if __name__ == "__main__":
    all_results = []
    max_pages = 40
    driver = get_headless_driver()

    for outcode in search:
        print(f"\n🔍 Searching: {outcode}")
        for page in range(1, max_pages + 1):
            url = BASE_URL.format(outcode=outcode) + str(page)
            print(f"\n📄 Scraping page {page} → {url}")
            driver.get(url)
            click_through(driver)
            page_results = scrape_page(driver, page)

            if not page_results:
                print(f"🛑 No listings found on page {page} for {outcode}. Stopping...")
                break

            all_results.extend(page_results)

    driver.quit()

    df = pd.DataFrame(all_results)

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
    os.makedirs("output", exist_ok=True)
    output_path = f"output/zoopla_scrape_{timestamp}.csv"
    df.to_csv(output_path, index=False)

    print(f"\n✅ Scraping complete. Listings scraped: {len(df)}")
    print(f"📁 Data saved to: {output_path}")
