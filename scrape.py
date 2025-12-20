from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from utils import safe_click, safe_send_keys
import time
import os
import yaml

# Load locators and URLs from YAML
_loc_file = os.path.join(os.path.dirname(__file__), 'locators.yml')
with open(_loc_file, 'r', encoding='utf-8') as _f:
    LOC = yaml.safe_load(_f)

# Extracting offer info
def extract_listing_info(li):
    try:
        desc_text = li.find_element(By.CSS_SELECTOR, LOC['DESCRIPTION_LIST_CSS']).text
        desc_parts = desc_text.split('\n')
        return [
            li.find_element(By.CSS_SELECTOR, LOC['PRICE_SPAN_CSS']).text,
            desc_parts[1], # rooms
            desc_parts[3], # area
            li.find_element(By.TAG_NAME, 'a').get_attribute('href'),
            li.find_element(By.CSS_SELECTOR, LOC['LISTING_TITLE_P_CSS']).text,
            li.find_element(By.CSS_SELECTOR, LOC['LISTING_PARAGRAPH_CSS']).text
        ]
    except Exception:
        return None

# Processing all offers from current page
def process_offers(driver):
    ul = driver.find_element(By.XPATH, LOC['LISTINGS_UL_XPATH'])
    li_elements = ul.find_elements(By.TAG_NAME, 'li')
    # Mapping and filtering
    return list(filter(None, map(extract_listing_info, li_elements)))

def scrape_data(offer_type, city):
    options = Options()
    options.add_argument("--window-size=1200,800")
    driver = webdriver.Chrome(options=options)
    
    try:
        open_home_page(driver)
        navigate_to_listings(driver, city, offer_type)
        
        # Checking number of pages
        try:
            pagination = driver.find_element(By.CSS_SELECTOR, LOC['PAGINATION_UL_CSS'])
            pages_number = int(pagination.find_elements(By.TAG_NAME, 'li')[-2].text)
        except NoSuchElementException: # for single pages
            print("Znaleziono jedną stronę. Pobieranie danych...")
            return process_offers(driver)
        
        all_results = scrape_page_and_recurse(
            driver=driver,
            current_page=1,
            pages_number=pages_number,
            all_results=[]
        )

        print("Pobieranie zakończono sukcesem. Zapisywanie pliku...")
        return all_results
    except Exception:
        print("Wystąpił nieoczekiwany błąd podczas pobierania danych.")
    finally:
        driver.quit()
    
def open_home_page(driver):
    driver.get(LOC['HOME_URL'])
    safe_click(driver, LOC['COOKIE_ACCEPT_XPATH']) # Cookies

def navigate_to_listings(driver, city, offer_type):
    # Choose type and city
    safe_click(driver, LOC['TRANSACTION_DROPDOWN_XPATH'])
    xpath_type = LOC['TRANSACTION_TYPE_SALE_XPATH'] if offer_type == "Na sprzedaż" else LOC['TRANSACTION_TYPE_RENT_XPATH']
    safe_click(driver, xpath_type)

    safe_click(driver, LOC['LOCATION_DROPDOWN_XPATH'])
    safe_send_keys(driver, LOC['LOCATION_INPUT_XPATH'], city)
    safe_click(driver, LOC['LOCATION_SUGGESTION_XPATH'])
    safe_click(driver, LOC['SEARCH_SUBMIT_XPATH'])

    time.sleep(5)

def scrape_page_and_recurse(driver, current_page, pages_number, all_results):
    print(f"Pobieranie strony {current_page} z {pages_number}...", end='\r')
    all_results.extend(process_offers(driver))

    if current_page >= pages_number:
        return all_results

    pagination = driver.find_element(By.CSS_SELECTOR, LOC['PAGINATION_UL_CSS'])
    next_btn = pagination.find_elements(By.TAG_NAME, 'li')[-1]

    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", next_btn)
    time.sleep(1)
    next_btn.click()
    time.sleep(3)

    return scrape_page_and_recurse(
        driver,
        current_page + 1,
        pages_number,
        all_results
    )