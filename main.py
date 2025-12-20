from datetime import datetime
from save_and_process import process_city

if __name__ == "__main__":
    CONFIG = {
        "cities": ["Ciechocinek"],
        "types": ["Na wynajem", "Na sprzedaż"]
    }
    
    today = datetime.today().strftime('%Y-%m-%d')
    
    for city in CONFIG["cities"]:
        for t in CONFIG["types"]:
            process_city(city, t, today)