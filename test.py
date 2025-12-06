import os


cwd = os.getcwd()
directories = [d for d in os.listdir(cwd) if os.path.isdir(os.path.join(cwd, d))]
dates = []
for d in directories:
    if d.startswith("scrape-res-"):
        date_part = d.replace("scrape-res-", "")
        dates.append(date_part)

date = "2025-11-30"

available_cities = os.listdir(f"scrape-res-{date}")
for a in available_cities:
    a = a.replace("data_","").replace("_Na_wynajem.csv","").replace("_Na_sprzedaż.csv","")
available_cities = list(set(available_cities))
print(available_cities)