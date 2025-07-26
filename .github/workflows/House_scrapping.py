"""This is a script that Scraps the House price Data from Zoopla.co.uk , 
The Records collected include 
- Amount last sold
- Amount last sold(-1)
- Amount last sold(-2)
- Property type
- Address
- Number of rooms
- Number of Baths
- Number of toilet
- EPC Rating
- Square foot meter SQM
- Tenure
- UPRN
- lowerPrice
- currentPrice 
- upperPrice
- Longitude
- Latitude
-listing URL



** HOW SCRIPT WORKS **
------------------------

step 1
Make Sure that the *Libararies* below used for analysis of this project are installed on your jupyter notebook or whatever software tool you are using.

step 2
The script scrapes data based on the outcode, postcode, county , or region in UK. e.g , "LS1","LS1 1PJ", "leeds", or "west yorkshire
the search = ["LS1 1AA","LS1 2AD"] can be added to accomdate more postcodes if scrapping is based on postcode as the case maybe


step 3
Once **step 2** is completed then you can go to "# 9. === Main script execution ===" comment section to increase or 
decrease the number of pages that you want to be scrapped from zoopla. by default the available number of pages is *40pages* 

**step 4**
When you run the script, it will web crawl through the listings while it is collecting the data needed for analysis

**step 5**
    once the **step 4** has been done, the data is now stored in a csv file
"""


# 1. === libraries needed for webscrapping ===
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
from selenium.webdriver.remote.webdriver import WebDriver
from typing import Iterator
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import undetected_chromedriver as uc
import tempfile



# 2. === search here we can change the list e.g we can search using e.g outcodes: 'LS1' ,postcode: 'LS1 1PJ', 'Leeds' , or 'west yorkshire' etc ===
search = ['CM22']


# this the the BASE URL for ZOOPLA e.g rentals note **this should not be changed**
BASE_URL = "https://www.zoopla.co.uk/house-prices/{outcode}/?new_homes=include&q={outcode}&view_type=list&pn="
TIMEOUT = 5


# 3. Headleess_driver; using chrome to access the the url to the scrapped
def get_headless_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64)")
    
    # 🔧 TEMP FIX: use unique user data directory
    user_data_dir = tempfile.mkdtemp()
    chrome_options.add_argument(f"--user-data-dir={user_data_dir}")
    
    return Chrome(options=chrome_options)



# 4. === Extracts text from a WebElement , more like strip's the text incase or whitespace infront or after the text ====
def etext(e: WebElement) -> str:
    if e:
        if t := e.text.strip():
            return t
        if (p := e.get_property("textContent")) and isinstance(p, str):
            return p.strip()
    return ""

# 5. === The Gets all WebElements that match the given CSS selector ===
def get_all(driver: WebDriver, css: str) -> Iterator[WebElement]:
    wait = WebDriverWait(driver, TIMEOUT)
    sel = (By.CSS_SELECTOR, css)
    try:
        yield from wait.until(EC.presence_of_all_elements_located(sel))
    except TimeoutException:
        pass

# 6. === Click the WebElement ===
def click(driver: WebDriver, e: WebElement) -> None:
    ActionChains(driver).click(e).perform()

# 7. === Handle cookie consent popup, it literally clicks and accepts cookies that may appear ===
def click_through(driver: WebDriver) -> None:
    try:
        wait = WebDriverWait(driver, TIMEOUT)
        shadow_root = driver.find_element(By.ID, "usercentrics-root").shadow_root
        button = wait.until(EC.element_to_be_clickable(
            (By.CSS_SELECTOR, "button[data-testid=uc-deny-all-button]")
        ))
        click(driver, button)
    except Exception:
        pass  # Ignore if cookies popup is not present


# 8. === Get additional details that is not on the first view ===
# note **try/except method was used because once the scripts try's to get a value, if it's not there it will return "N/A" instead of skipping the listing
""" 
(EPC rating, longitude,
latitude, UPRN,lowerPrice,currentPrice,UpperPrice,posttown name) """
def get_details(driver, listing_url):
    driver2 = get_headless_driver()
    driver2.get(listing_url)
    click_through(driver2)  # Handle cookies

    # EPC Rating
    try:
        epc_element = WebDriverWait(driver2, 5).until(
            EC.presence_of_element_located((By.XPATH, ".//*[contains(text(), 'EPC rating') or contains(text(), 'EPC Rating')]"))
        )
        epc_rating = etext(epc_element)
    except :
        epc_rating = "N/A"
        

    # get the longitude
    try:
        longitude = WebDriverWait(driver2, 5).until(EC.presence_of_element_located((By.XPATH, ".//*[contains(text(), 'longitude')]"))
        )
        longitude =etext(longitude)
        match = re.search(r'"longitude"\s*:\s*(-?\d+\.\d+)', longitude)
        if match:
            longitude = match.group(1)        
    except:
        longitude = 'N/A'

    # get the latitude
    try:
        latitude = WebDriverWait(driver2, 5).until(EC.presence_of_element_located((By.XPATH, ".//*[contains(text(), 'latitude')]"))
        )
        latitude =etext(latitude)
        latitude = latitude.replace(",","")
        match = re.search(r'"latitude"\s*:\s*(\d+\.\d+)', latitude)
        if match:
            latitude = match.group(1)
    except:
        latitude = 'N/A'


    try:
        uprn = WebDriverWait(driver2, 5).until(EC.presence_of_element_located((By.XPATH, ".//*[contains(text(), 'uprn')]"))
        )
        uprn =etext(uprn)
        match = re.search(r'"uprn"\s*:\s*"(\d+)"', uprn)
        if match:
            uprn = match.group(1)
        else:
            uprn = 'N/A'
    except:
        uprn = 'N/A'

    # gets the lowerPrice,CurrentPrice, UpperPrice
    try:
        saleEstimate = WebDriverWait(driver2, 5).until(EC.presence_of_element_located((By.XPATH, ".//*[contains(text(), 'saleEstimate')]"))
        )
        saleEstimate =etext(saleEstimate)
        match = re.search(r'"saleEstimate"\s*:\s*{[^}]*?"lowerPrice"\s*:\s*(\d+),\s*"currentPrice"\s*:\s*(\d+),\s*"upperPrice"\s*:\s*(\d+)', saleEstimate)
        if match:
            lowerPrice = int(match.group(1))
            currentPrice = int(match.group(2))
            upperPrice = int(match.group(3))
        else:
            lowerPrice = 'N/A'
            currentPrice = 'N/A'
            upperPrice = 'N/A'
    except:
            lowerPrice = 'N/A'
            currentPrice = 'N/A'
            upperPrice = 'N/A'

    # gets the posttown name
    try:
        postTownName = WebDriverWait(driver2, 5).until(EC.presence_of_element_located((By.XPATH, ".//*[contains(text(), 'postTownName')]"))
        )
        postTownName =etext(postTownName)
        match = re.search(r'"postTownName"\\?":\\?"([^"]+)"', postTownName)
        if match:
            postTownName = match.group(1)
        else:
            postTownName = 'N/A'
    except:
        postTownName = 'N/A'

    # closes once done       
    driver2.quit()
    # returns the scrapped element
    return epc_rating, longitude ,latitude,uprn,lowerPrice,currentPrice,upperPrice,postTownName

    

# 9 === This scrapes the information's on the main listings, each listings url as in *7* above and also stores the data in a list results ===
def scrape_page(driver: WebDriver) -> list[dict]:
    result = []
    # loops through each listing and gets the information
    for house in get_all(driver, "div[data-testid=result-item]"):
        try:
            # gets each listing URL so that we can get more  that is not on the main listing
            listing_url = house.find_element(By.XPATH, ".//a[starts-with(@href, '/property/')]").get_attribute("href")

            # calls the get_details functions in *7* so they can return the epc, longitude, latitude, ... 
            epc_rating,longitude,latitude,uprn,lowerPrice,currentPrice,upperPrice,postTownName = get_details(driver, listing_url)

            # gets the address
            try:
                address = etext(house.find_element(By.CSS_SELECTOR, "h2"))
            except:
                address = " "
            
            # gets the last date sold
            try:
                Latestdate_sold = etext(house.find_element(By.CSS_SELECTOR, "div._1i39aq44 > div:nth-child(1) > ul > li:nth-child(1)"))
            except:
                Latestdate_sold = " "

            # gets the last date sold (-1)
            try:
                Previousdate_sold_1 = etext(house.find_element(By.CSS_SELECTOR, "div._1i39aq44 > div:nth-child(1) > ul > li:nth-child(2)"))
            except:
                Previousdate_sold_1 = " "

            # # gets the last date sold (-2)
            try:
                Previousdate_sold_2 = etext(house.find_element(By.CSS_SELECTOR, "div._1i39aq44 > div:nth-child(1) > ul > li:nth-child(3)"))
            except:
                Previousdate_sold_2 = " "  # Set to None if missing or blank

            # gets the type of house
            try:
                House_Type = etext(house.find_element(By.CSS_SELECTOR, "div._1i39aq44 > div:nth-child(1) > div > div > div._1pbf8i51 > div._1pbf8i52"))
            except:
                House_Type = " "

            # gets the number of rooms
            try:
                Number_of_rooms = etext(house.find_element(By.XPATH, ".//*[contains(@aria-label, 'bed')]"))

            except:
                Number_of_rooms = " "

            # gets the number of bath
            try: 
                Number_of_bath =  etext(house.find_element(By.XPATH, ".//*[contains(@aria-label, 'bath')]"))
            except:
                Number_of_bath = " "

            # gets the number of reception
            try:
                Reception =  etext(house.find_element(By.XPATH, ".//*[contains(@aria-label, 'reception')]"))
            except:
                Reception = " "

            # gets the tenure
            try:
                Tenure = etext(house.find_element(By.CSS_SELECTOR, "div._1i39aq44 > div:nth-child(1) > div > div > div.agepcz0 > div:nth-child(1) > div"))
            except:
                Tenure = ""

            # gets the square meter
            try:
                Square_foot = etext(house.find_element(By.XPATH,".//*[contains(text(),'sqm' )]"))
            except:
                Square_foot = " "

            # # gets the data and append it to result
            result.append({"Address": address,"Date Last Sold": Latestdate_sold,"Previous date sold(-1)": Previousdate_sold_1,
                         "Previous date sold(-2)":Previousdate_sold_2,"Property Type": House_Type,"Number of rooms": Number_of_rooms,
                          "Number of Bath": Number_of_bath,"Reception" : Reception,"Tenure": Tenure , "Square foot" : Square_foot,
                          "EPC Rating": epc_rating,"UPRN":uprn,"lowerPrice":lowerPrice,"currentPrice":currentPrice,
                           "upperPrice":upperPrice,"longitude": longitude,"latitude": latitude,"Listing URL": listing_url})

        except NoSuchElementException:
            continue  # Skip missing elements
    return result


# 10. === Main script execution ===
if __name__ == "__main__":
    all_results = []
    max_pages = 4   # the maximum pages can be changed
    
    driver = get_headless_driver()

    # loops through the search and try's to scrape the pages
    for outcode in search:
        print(f"🔍 Searching: {outcode}")
        for page in range(1, max_pages + 1):
            url = BASE_URL.format(outcode=outcode) + str(page)
            print(f"Scraping page {page} → {url}")
            driver.get(url)
            click_through(driver)
            page_results = scrape_page(driver)

            if not page_results:
                print(f"No listings found on page {page} for {outcode}.")
                break

            all_results.extend(page_results)

    driver.quit() #

    # saves the data in a data frame
    df = pd.DataFrame(all_results)

    # Save to CSV
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
    os.makedirs("Zoopla_House_Scrapping", exist_ok=True)
    output_path = f"Zoopla_House_Scrapping/zoopla_House_{timestamp}.csv"
    df.to_csv(output_path, index=False)

    print(f"\n✅ Scraping complete. Listings scraped: {len(df)}")
    print(f"📁 Data saved to: {output_path}")
