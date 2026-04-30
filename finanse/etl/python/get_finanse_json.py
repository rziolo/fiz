import csv
import json
import os
from datetime import datetime

file_path = '/var/www/html/flask/finanse/etl/csv/finanse_miesiac.csv'
data_dict = {}

if os.path.exists(file_path):
    with open(file_path, mode='r', encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) == 2:
                key, value = row[0], row[1]
                # Konwersja na float jeśli to możliwe, inaczej zostaje string
                try:
                    data_dict[key] = float(value)
                except ValueError:
                    data_dict[key] = value

    # Dodanie flagi czy dane są z dzisiaj
    if 'fin_data' in data_dict:
        try:
            is_today = data_dict['fin_data'] == datetime.now().strftime('%Y-%m-%d')
            data_dict['fin_is_today'] = is_today
        except:
            data_dict['fin_is_today'] = False

    print(json.dumps(data_dict))
else:
    print(json.dumps({"error": "File not found"}))
