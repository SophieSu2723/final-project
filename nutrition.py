import json
import requests
import sqlite3
import os



api_key = 'c9a7161192fd4c2d914ecaf9654bd607'
filename = 'nutrition.json'

#for i in range(1, 151):
#     api_url = f'https://api.spoonacular.com/recipes/{i}/nutritionWidget.json'
#     params = {'apiKey': api_key}

#     try:
#        response = requests.get(api_url, params=params)
#        info = response.json()
#        info['recipe_id'] = i
#        if 'nutrients' in info:
#             write_json(filename, info)
#     except Exception:
#         pass

def write_json(filename, data):
    with open(filename, 'a') as file:
        json.dump(data, file)
        file.write('\n')

def read_json(file_path):
    with open(file_path, 'r') as f:
        file_data = f.read().split('\n')
        data = []
        for item in file_data:
            try:
                item = json.loads(item)
                data.append(item)
            except:
                continue
    return data

def create_table(cursor):
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS nutrition (
            recipe_id INTEGER PRIMARY KEY,
            sugar INTEGER,
            sugar_unit Text,
            protein INTEGER,
            protein_unit TEXT
        )
    ''')

def process_line(line, cursor):
    # Extract sugar and protein values
    sugar_amount = next((float(item['amount'].strip('g')) for item in line['bad'] if item['title'] == 'Sugar'), None)
    protein_amount = next((float(item['amount'].strip('g')) for item in line['good'] if item['title'] == 'Protein'), None)
    recipe_id = line['recipe_id']

    if sugar_amount is not None and protein_amount is not None:
        cursor.execute('''
            INSERT OR IGNORE INTO nutrition 
            (recipe_id, sugar, sugar_unit, protein, protein_unit) 
            VALUES (?, ?, ?, ?, ?)
        ''', (recipe_id, sugar_amount, 'g', protein_amount, 'g'))


def main():
    json_data = read_json('nutrition.json')
    conn = sqlite3.connect('final.db')
    cursor = conn.cursor()

    create_table(cursor)

    cursor.execute('SELECT MAX(recipe_id) FROM nutrition')
    last_processed_id = cursor.fetchone()[0] or 0

    batch_size = 25
    next_batch = json_data[last_processed_id:last_processed_id + batch_size]
    for line in next_batch:
        process_line(line, cursor)

    conn.commit()
    conn.close()

if __name__ == '__main__':
    main()
