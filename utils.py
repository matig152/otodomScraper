from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd

def safe_click(driver, xpath, timeout=100):
    """Clicks an element safely by waiting for it to be clickable."""
    wait = WebDriverWait(driver, timeout)
    element = wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
    element.click()

def safe_send_keys(driver, xpath, keys, timeout=10):
    """Sends keys to an input element safely by waiting for it to be present."""
    wait = WebDriverWait(driver, timeout)
    element = wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
    element.click()
    element.clear()
    element.send_keys(keys)

def safe_get_text(driver, xpath, timeout=100):
    """Gets text from an element safely by waiting for it to be present."""
    wait = WebDriverWait(driver, timeout)
    element = wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
    return element.get_attribute('innerText')

def safe_scroll_into_view(driver, xpath, timeout=100):
    """Scrolls an element into view safely by waiting for it to be present."""
    wait = WebDriverWait(driver, timeout)
    element = wait.until(EC.visibility_of_element_located((By.XPATH, xpath)))
    driver.execute_script("arguments[0].scrollIntoView({ behavior: 'smooth', block: 'center' });", element)

def find_outliers_iqr(df):
    numeric = df.select_dtypes(include='number')

    # compute IQR
    Q1 = numeric.quantile(0.25)
    Q3 = numeric.quantile(0.75)
    IQR = Q3 - Q1

    lower = Q1 - 1.5 * IQR
    upper = Q3 + 1.5 * IQR

    # boolean mask of outliers per column
    mask = (numeric < lower) | (numeric > upper)

    # return original rows where ANY column is an outlier
    return df[mask.any(axis=1)]