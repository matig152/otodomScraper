import pandas as pd
import warnings
warnings.simplefilter(action="ignore", category=FutureWarning)

def parse(data):

    parsed_data = pd.DataFrame(columns=['price', 'n_rooms', 'area', 'price_per_m2', 'link', 'title', 'address', 'district'])
    for index, row in data.iterrows():

        # Parse price
        formatted_price = row[0].replace(' ', '').replace('zł', '')
        if not formatted_price.isdigit():
            continue # omitting record with non-numeric price
        formatted_price = int(formatted_price)

        # Parse number of rooms
        rooms_text = row[1]
        if not(rooms_text.endswith('pokój') or rooms_text.endswith('pokoje')):
            continue
        n_rooms = int(rooms_text.split(' ')[0])

        # Parse area
        area_text = row[2]
        if not area_text.endswith('m²'):
            continue
        area = area_text.replace(' m²', '')
        area = float(area)

        # Get price per m2
        price_per_m2 = round(formatted_price / area, 0)

        # Parse district from adress
        address_text = row[5]
        district = address_text.split(',')[-3].strip() if ',' in address_text else ''

        # append to DataFrame        
        parsed_data = pd.concat([parsed_data, pd.DataFrame([{
            'price': formatted_price,
            'n_rooms': n_rooms,
            'area': area,
            'price_per_m2': price_per_m2,
            'link': row[3],
            'title': row[4],
            'address': address_text,
            'district': district
        }])], ignore_index=True)

    return parsed_data