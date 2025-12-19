from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from streamlit import button
from utils import safe_click, safe_send_keys, safe_get_text, safe_scroll_into_view
import time
from selenium.common.exceptions import StaleElementReferenceException


def scrape_data(offer_type, city):
    options = Options()
    #options.add_argument("--headless=new")
    options.add_argument("--window-size=1200,800")
    driver = webdriver.Chrome(options=options)


    print("Wait for homepage to load...")
    HOME_URL = "https://www.otodom.pl/"
    driver.get(HOME_URL)


    # ACCEPT COOKIES
    safe_click(driver, '//*[@id="onetrust-accept-btn-handler"]')

    # INPUT DATA
    
    # Offer type
    safe_click(driver, "//*[@id=\"transaction-dropdown\"]")
    if offer_type == "Na sprzedaż":
        safe_click(driver, '/html/body/div[1]/main/section[1]/div/div/form/div/div[1]/div[1]/div[2]/div/div[2]/div/div/div[2]')
    elif offer_type == "Na wynajem":
        safe_click(driver, '/html/body/div[1]/main/section[1]/div/div/form/div/div[1]/div[1]/div[2]/div/div[2]/div/div/div[1]')
    # City
    safe_click(driver, '//*[@id="__next"]/main/section[1]/div/div/form/div/div[1]/div[2]/div[1]')
    safe_send_keys(driver, '//*[@id="location-search-input"]', city)
    safe_click(driver, '/html/body/div[1]/main/section[1]/div/div/form/div/div[1]/div[2]/div[1]/div[2]/div/div/div/div/div[1]/div[1]/div')

    # Search
    safe_click(driver, '//*[@id="search-form-submit"]')


    PAGE_LOAD_TIMEOUT = 5

    # Get number of pages
    time.sleep(PAGE_LOAD_TIMEOUT)  # Wait for page to load properly
    pagination = WebDriverWait(driver, 100).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'ul[data-cy="nexus-pagination-component"]'))
    )
    li_elements = pagination.find_elements(By.TAG_NAME, 'li')
    last_li = li_elements[-2]
    y = last_li.location['y']
    driver.execute_script(f"window.scrollTo(0, {y - 100});")
    pages_number = last_li.get_attribute('innerText')
    print(f"Number of pages: {pages_number}")


    data = []

    # Get list of organic results
    print("Starting to scrape data...")
    current_page = 1
    while (current_page <= int(pages_number)):
        print(f"Page {current_page} / {pages_number}", end='\r')
        ul = driver.find_element(By.XPATH, '//div[@data-cy="search.listing.organic"]/ul')
        li_elements = ul.find_elements(By.TAG_NAME, 'li')
        for li in li_elements:    
            try:
                price_text = li.find_element(By.CSS_SELECTOR, 'span[data-sentry-element="MainPrice"]').text
                desc_text = li.find_element(By.CSS_SELECTOR, 'dl[data-sentry-element="StyledDescriptionList"]').text
                rooms_text = desc_text.split('\n')[1]
                area_text = desc_text.split('\n')[3]
                link_text = li.find_element(By.TAG_NAME, 'a').get_attribute('href')
                title_text = li.find_element(By.CSS_SELECTOR, 'p[data-cy="listing-item-title"]').text
                address_text = li.find_element(By.CSS_SELECTOR, 'p[data-sentry-element="StyledParagraph"]').text
                data.append([price_text, rooms_text, area_text, link_text, title_text, address_text])
            except:
                pass

        if li_elements:
            for i in range(5):
                try: 
                    driver.execute_script("arguments[0].scrollIntoView(true);", li_elements[-1])
                    time.sleep(1)  # Give browser time to render if needed
                except StaleElementReferenceException:
                    time.sleep(5)    

        # Next page
        pagination = WebDriverWait(driver, 100).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'ul[data-cy="nexus-pagination-component"]'))
        )
        li_elements = pagination.find_elements(By.TAG_NAME, 'li')
        last_li = li_elements[-1]
        y = last_li.location['y']
        driver.execute_script(f"window.scrollTo(0, {y - 100});")
        last_li.click()
        current_page += 1
        time.sleep(PAGE_LOAD_TIMEOUT)
    print("\nScraping finished.\n")

    driver.quit()
    return data

   