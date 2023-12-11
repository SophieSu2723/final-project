import sqlite3
import json


def setup_database():
    conn = sqlite3.connect('final.db')

    # Vitamins table
    conn.execute('''CREATE TABLE IF NOT EXISTS vitamins (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        food_name TEXT,
                        nutrient_name TEXT,
                        nutrient_amount REAL,
                        unit_name TEXT,
                        UNIQUE(food_name, nutrient_name))''')

    # Proteins table
    conn.execute('''CREATE TABLE IF NOT EXISTS proteins (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        food_name TEXT,
                        nutrient_amount REAL,
                        unit_name TEXT,
                        UNIQUE(food_name))''')

    # Insert count table 
    conn.execute('''CREATE TABLE IF NOT EXISTS insert_count (
                        id INTEGER PRIMARY KEY,
                        count INTEGER DEFAULT 0)''')
    conn.execute("INSERT OR IGNORE INTO insert_count (id, count) VALUES (1, 0)")
    conn.commit()
    return conn 

def read_json_file(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data

def get_insert_count(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT count FROM insert_count WHERE id = 1")
    result = cursor.fetchone()
    return result[0] if result else 0

def update_insert_count(conn, new_count):
    cursor = conn.cursor()
    cursor.execute("UPDATE insert_count SET count = ? WHERE id = 1", (new_count,))
    conn.commit()

def insert_food_get_id(cursor, food_name):
    cursor.execute("INSERT OR IGNORE INTO foods (food_name) VALUES (?)", (food_name,))
    cursor.execute("SELECT food_id FROM foods WHERE food_name = ?", (food_name,))
    return cursor.fetchone()[0]


def insert_data_into_db(conn, data, limit=25):
    cursor = conn.cursor()
    count = get_insert_count(conn)
    total_items = len(data['FoundationFoods'])

    for food in data['FoundationFoods'][count:count+limit]:
        food_name = food.get('description', 'Unknown')
        protein_value = next((factor['value'] for factor in food.get('nutrientConversionFactors', []) 
                              if factor.get('type') == '.ProteinConversionFactor'), 0)
        if protein_value:
            protein_sql = '''INSERT OR IGNORE INTO proteins (food_name, nutrient_amount, unit_name)
                             VALUES (?, ?, ?)'''
            cursor.execute(protein_sql, (food_name, protein_value, 'g'))

        for nutrient in food.get('foodNutrients', []):
            nutrient_name = nutrient['nutrient']['name']
            if "vitamin" in nutrient_name.lower():
                vitamin_amount = nutrient.get('amount', 0)
                unit_name = nutrient['nutrient'].get('unitName', '')
                vitamin_sql = '''INSERT OR IGNORE INTO vitamins (food_name, nutrient_name, nutrient_amount, unit_name)
                                 VALUES (?, ?, ?, ?)'''
                cursor.execute(vitamin_sql, (food_name, nutrient_name, vitamin_amount, unit_name))

    new_count = min(count + limit, total_items)
    update_insert_count(conn, new_count)
    conn.commit()
    

def main():
    conn = setup_database()
    data = read_json_file('foundationDownload.json')
    insert_data_into_db(conn, data)
    conn.close()

if __name__ == "__main__":
    main()


