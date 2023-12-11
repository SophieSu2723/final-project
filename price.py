import requests
import os
import json
import sqlite3

def load_json(filename):
    try:
        with open(filename,'r') as f:
            # contents = f.read()
            data = json.load(f)
        f.close()
        return data
    except:
        return {}

#write the json file
def write_json(filename, dict):
    with open(filename, 'a') as f:
        json.dump(dict,f)
        f.write('\n')
    return None

def read_json(file_path):
    """
    Reads data from a file with the given filename.

    Parameters
    -----------------------
    filename: str
        The name of the file to read.

    Returns
    -----------------------
    dict:
        Parsed JSON data from the file.
    """
    with open(file_path, 'r') as f:
        file_data = f.read().split('\n')
        # print(type(file_data))
        data = []
        for item in file_data:
            try:
                item = json.loads(item)
                # print(type(item))
                data.append(item)
            except:
                continue
        # print(data)
    return data

#sets up a SQLite database connection and cursor
def set_up_database(db_name):
    """
    Returns
    -----------------------
    Tuple (Cursor, Connection):
        A tuple containing the database cursor and connection objects.
    """
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path + "/" + db_name)
    cur = conn.cursor()
    return cur, conn

#set up total price table
def set_up_price_table(data, cur, conn):
    # cur.execute(
    #     'CREATE TABLE IF NOT EXISTS Price (recipe_id TEXT PRIMARY KEY, total_price INTEGER, price_per_serving INTEGER)'
    # )
    # print(data)
    for recipe in data:
        recipe_id = recipe['recipe_id']
        total_price = float(recipe['totalCost'])
        price_per_serving = float(recipe['totalCostPerServing'])

        cur.execute(
                "INSERT INTO Price (recipe_id, total_price, price_per_serving) VALUES (?, ?, ?)",
                (recipe_id, total_price, price_per_serving)
            )
    conn.commit()
    return None

# # get data from the API and write it into the json file
dir_path = os.path.dirname(os.path.realpath(__file__))
filename = dir_path + '/' + "price.json"
# for i in range(1,151):
#     recipe_id = i
#     api_key = '8215a29f2904438f86f520ec142abf8e'
#     api_url = f'https://api.spoonacular.com/recipes/{recipe_id}/priceBreakdownWidget.json'
#     params = {'apiKey': api_key}

#     # make the API request and add the recipe id to each recipe
#     response = requests.get(api_url, params=params)
#     info = response.json()
#     info['recipe_id'] = i
#     if 'ingredients' in info:
#         # print(type(info))
#         write_json(filename,info)

# write data into database
json_data = read_json(filename)
cur, conn = set_up_database("final.db")
# print(json_data)
batch_size = 25
table_name = 'Price'
cur.execute(
    'CREATE TABLE IF NOT EXISTS Price (recipe_id TEXT PRIMARY KEY, total_price INTEGER, price_per_serving INTEGER)'
)
cur.execute(f'SELECT COUNT(*) FROM {table_name}')
row_count = cur.fetchone()[0]
if row_count < 100:
    batch = json_data[row_count:row_count+batch_size]
    set_up_price_table(batch, cur, conn)
conn.close()