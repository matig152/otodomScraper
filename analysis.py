import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import os

from utils import find_outliers_iqr


st.set_page_config(page_title="My App", layout="wide")

st.header("Otodom scraper - analiza ofert nieruchomości")

# Get available dates
cwd = os.getcwd()
directories = [d for d in os.listdir(cwd) if os.path.isdir(os.path.join(cwd, d))]
dates = []
for d in directories:
    if d.startswith("scrape-res-"):
        date_part = d.replace("scrape-res-", "")
        dates.append(date_part)
selected_date = st.selectbox("Wybierz datę:", options=dates)

available_cities_files = os.listdir(f"{cwd}\scrape-res-{selected_date}")
available_cities = []
for a in available_cities_files:
    a = a.replace("data_","").replace("_Na_wynajem.csv","").replace("_Na_sprzedaż.csv","")
    available_cities.append(a)
available_cities = list(set(available_cities))
selected_city = st.selectbox("Wybierz miasto:", options=available_cities)

data_rent = pd.read_csv(f"scrape-res-{selected_date}/data_{selected_city}_Na_wynajem.csv")
data_sell = pd.read_csv(f"scrape-res-{selected_date}/data_{selected_city}_Na_sprzedaż.csv")

# COLUMNS
col1, col2 = st.columns(2)


# COLUMN 1 - SELECT VARIABLE + BASIC STATS
variables_to_analyze = {
    'Cena': 'price',
    'Powierzchnia': 'area',
    'Cena za m²': 'price_per_m2',
    'Liczba pokoi': 'n_rooms'
}

variable = col1.selectbox("Wybierz zmienną do analizy:", variables_to_analyze.keys())

col1.write(f"Liczba ofert na wynajem w mieście {selected_city}: {data_rent.shape[0]}")
col1.write(f"Liczba ofert na sprzedaż w mieście {selected_city}: {data_sell.shape[0]}")

stats_df = pd.DataFrame({
    '': ['Średnia', 'Mediana', 'Odchylenie standardowe', 'Minimum', 'Maksimum'],
    'Na sprzedaż': [
        f"{data_sell[variables_to_analyze[variable]].mean():,.0f} {'PLN' if variables_to_analyze[variable]=='price' else 'm²' if variables_to_analyze[variable]=='area' else 'PLN/m²' if variables_to_analyze[variable]=='price_per_m2' else ''}",
        f"{data_sell[variables_to_analyze[variable]].median():,.0f} {'PLN' if variables_to_analyze[variable]=='price' else 'm²' if variables_to_analyze[variable]=='area' else 'PLN/m²' if variables_to_analyze[variable]=='price_per_m2' else ''}",
        f"{data_sell[variables_to_analyze[variable]].std():,.0f} {'PLN' if variables_to_analyze[variable]=='price' else 'm²' if variables_to_analyze[variable]=='area' else 'PLN/m²' if variables_to_analyze[variable]=='price_per_m2' else ''}",
        f"{data_sell[variables_to_analyze[variable]].min():,.0f} {'PLN' if variables_to_analyze[variable]=='price' else 'm²' if variables_to_analyze[variable]=='area' else 'PLN/m²' if variables_to_analyze[variable]=='price_per_m2' else ''}",
        f"{data_sell[variables_to_analyze[variable]].max():,.0f} {'PLN' if variables_to_analyze[variable]=='price' else 'm²' if variables_to_analyze[variable]=='area' else 'PLN/m²' if variables_to_analyze[variable]=='price_per_m2' else ''}"
    ],
    'Na wynajem': [
        f"{data_rent[variables_to_analyze[variable]].mean():,.0f} {'PLN' if variables_to_analyze[variable]=='price' else 'm²' if variables_to_analyze[variable]=='area' else 'PLN/m²' if variables_to_analyze[variable]=='price_per_m2' else ''}",
        f"{data_rent[variables_to_analyze[variable]].median():,.0f} {'PLN' if variables_to_analyze[variable]=='price' else 'm²' if variables_to_analyze[variable]=='area' else 'PLN/m²' if variables_to_analyze[variable]=='price_per_m2' else ''}",
        f"{data_rent[variables_to_analyze[variable]].std():,.0f} {'PLN' if variables_to_analyze[variable]=='price' else 'm²' if variables_to_analyze[variable]=='area' else 'PLN/m²' if variables_to_analyze[variable]=='price_per_m2' else ''}",
        f"{data_rent[variables_to_analyze[variable]].min():,.0f} {'PLN' if variables_to_analyze[variable]=='price' else 'm²' if variables_to_analyze[variable]=='area' else 'PLN/m²' if variables_to_analyze[variable]=='price_per_m2' else ''}",
        f"{data_rent[variables_to_analyze[variable]].max():,.0f} {'PLN' if variables_to_analyze[variable]=='price' else 'm²' if variables_to_analyze[variable]=='area' else 'PLN/m²' if variables_to_analyze[variable]=='price_per_m2' else ''}"
    ]
})
col1.table(stats_df)

avg_return = ((12 * data_rent['price_per_m2'].mean()) / data_sell['price_per_m2'].mean()) * 100
col1.write(f"Średnia roczna stopa zwrotu z wynajmu: {avg_return:.2f}%")


# COLUMN 2 - HISTOGRAM, BOXPLOT
sell_or_rent = {
    'na sprzedaż': 'Na_sprzedaż',
    'na wynajem': 'Na_wynajem'
}

offer_type = col2.selectbox("Wybierz rodzaj ofert:", sell_or_rent.keys())
#offer_type = col2.selectbox("Wybierz rodzaj ofert:", ('Na sprzedaż', 'Na wynajem'))
data_chosen = data_rent if offer_type == 'na wynajem' else data_sell

fig, ax = plt.subplots(figsize=(7,3))
ax.hist(data_chosen[variables_to_analyze[variable]].dropna(), bins=10, color='skyblue', edgecolor='black')
ax.set_xlabel(variable)
ax.set_title(f"{variable} lokali {offer_type} w mieście {selected_city}")
col2.pyplot(fig)

fig, ax = plt.subplots(figsize=(7,3))
plt.boxplot(data_chosen[variables_to_analyze[variable]].dropna(), vert=False, patch_artist=True, boxprops=dict(facecolor='skyblue'))
ax.set_xlabel(variable)
# ax.set_title(f"{variable}")
col2.pyplot(fig)



col1.subheader("Zmiany wartości w czasie")

means = []
medians = []
mins = []
for date in dates:
    data = pd.read_csv(f"scrape-res-{date}/data_{selected_city}_{sell_or_rent[offer_type]}.csv")
    means.append(data[variables_to_analyze[variable]].mean())
    medians.append(data[variables_to_analyze[variable]].median())
    mins.append(data[variables_to_analyze[variable]].min())

measures = {
    'średnia': 'means',
    'mediana': 'medians',
    'wartość minimalna': 'mins'
}

measure_chosen = col1.selectbox("Wybierz miarę:", measures.keys())

time_df = pd.DataFrame({'dates': dates, 'means': means, 'medians': medians, 'mins': mins})
time_df = time_df.set_index('dates')

fig, ax = plt.subplots(figsize=(7,3))
plt.plot(time_df.index, time_df[measures[measure_chosen]])
ax.set_ylabel(f"{variable} ({measure_chosen})")
# ax.set_title(f"{variable}")
col1.pyplot(fig)


# LOWEST PRICES FOR M2
st.subheader("Najtańsze oferty na sprzedaż (cena za m²)")
lowest_prices = data_sell.sort_values(by='price_per_m2').head(10)
st.table(lowest_prices)

# LOWEST PRICES (rent)
st.subheader("Najtańsze oferty na wynajem (cena całkowita)")
lowest_prices = data_rent.sort_values(by='price').head(10)
st.table(lowest_prices)

# OUTLIERS
st.subheader("Outlierzy")
outliers = find_outliers_iqr(data_sell)
st.table(outliers.head(10))
