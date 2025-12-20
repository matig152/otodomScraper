import pandas as pd
import os
from scrape import scrape_data
from cleanup_data import parse

def process_city(city, offer_type, date_str):
    print(f"Przetwarzanie: {city} ({offer_type})...")
    
    raw_list = scrape_data(offer_type, city)
    df_raw = pd.DataFrame(raw_list)
    df_clean = parse(df_raw)
    
    save_to_file(date_str, city, offer_type, df_clean)
    
def save_to_file(date_str, city, offer_type, data):
    dir_path = f"scrape-res-{date_str}"
    os.makedirs(dir_path, exist_ok=True)
    filename = f"{dir_path}/data_{city}_{offer_type.replace(' ', '_')}.csv"
    data.to_csv(filename, index=False)
    print(f"Zapisano: {filename}")