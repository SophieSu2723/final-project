import sqlite3
import os
import csv
import matplotlib.pyplot as plt
import pandas as pd

#calculation 1
def get_recipe_by_protein(protein, cur):
    cur.execute('''SELECT recipe_id, protein 
                FROM nutrition 
                WHERE protein > ?
        ''', (protein,))
    result = cur.fetchall()
    return result

#calculation 2
def get_recipe_price_if_sugar_above_protein(cur):
    cur.execute('''SELECT Price.recipe_id, total_price 
                FROM Price 
                JOIN nutrition ON Price.recipe_id = nutrition.recipe_id 
                WHERE nutrition.protein < nutrition.sugar
    ''', ())
    result = cur.fetchall()
    return result

#visualization data
def get_visualization_data(cur):
    cur.execute('''
        SELECT nutrition.recipe_id, nutrition.sugar, nutrition.protein, Price.total_price
        FROM nutrition
        JOIN Price ON nutrition.recipe_id = Price.recipe_id
    ''', ())
    result = cur.fetchall()
    return result

#store calculated result into a csv file
def write_calculation_csv(x, y, filename):
    with open(filename,'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['recipt id', 'protein amount'])
        writer.writerows(x)
        writer.writerow('')
        writer.writerow(['recipt id', 'sugar amount', 'protein amount'])
        writer.writerows(y)
    f.close()
    return None

def write_visualization_csv(z, filename):
    with open(filename,'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['recipt id', 'sugar amount', 'protein amount', 'total price'])
        writer.writerows(z)
    f.close()
    return None

#get calculated data
path = os.path.dirname(os.path.abspath(__file__))
conn = sqlite3.connect(path+'/'+'final.db')
cur = conn.cursor()
x = get_recipe_by_protein(10, cur)
# print(x)
y = get_recipe_price_if_sugar_above_protein(cur)
# print(y)
z = get_visualization_data(cur)
conn.close()

#write calculated data into separate files
dir_path = os.path.dirname(os.path.realpath(__file__))
filename = dir_path + '/' + "calculation.csv"
write_calculation_csv(x,y, filename)
filename = dir_path + '/' + "visualization.csv"
write_visualization_csv(z, filename)

#use data in visualization.csv to generate visulizations
visualization_csv = pd.read_csv('visualization.csv')

# Creating two scatterplots to visualize the relationships
plt.figure(figsize=(12, 6))

# Scatterplot for Price vs Sugar
plt.subplot(1, 2, 1) 
plt.scatter(visualization_csv['sugar amount'], visualization_csv['total price'], color='blue')
plt.title('Price vs Sugar')
plt.xlabel('Sugar (g)')
plt.ylabel('Total Price ($)')

# Scatterplot for Price vs Protein
plt.subplot(1, 2, 2) 
plt.scatter(visualization_csv['protein amount'], visualization_csv['total price'], color='green')
plt.title('Price vs Protein')
plt.xlabel('Protein (g)')
plt.ylabel('Total Price ($)')

# Show the plot
plt.tight_layout()
plt.show()