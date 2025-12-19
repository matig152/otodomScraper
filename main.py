from scrape import scrape_data
import pandas as pd
from cleanup_data import parse
from datetime import datetime
import os


if __name__ == "__main__":

    cities_to_scrape = ["Łódź", "Kraków", "Warszawa"]

    today = datetime.today()
    formatted_date = today.strftime('%Y-%m-%d')

    for city in cities_to_scrape:
        print(f"\nScraping data for city: {city}...")
        for offer_type in ["Na wynajem", "Na sprzedaż"]:
            print(f" -> Offer type: {offer_type}...")
            data = scrape_data(offer_type, city)
            data = pd.DataFrame(data)
            parsed_data = parse(data)

            # Check/create directory
            dir_path = f"scrape-res-{formatted_date}"
            os.makedirs(dir_path, exist_ok=True)
            # Save to CSV
            parsed_data.to_csv(f"{dir_path}/data_{city}_{offer_type.replace(' ', '_')}.csv", index=False)