from flask import Flask, render_template, request
import requests
import sqlite3 as sql

app = Flask(__name__)

# con = sql.connect("database.db")
# con.execute("CREATE TABLE food (id INTEGER PRIMARY KEY AUTOINCREMENT, item TEXT, protein INTEGER, fat INTEGER)")
# con.close()

api_key = '0gTcQtweKZPOZFF1MUZL5Uh71zuQHH3AU6gV3y7O'
url = 'https://api.nal.usda.gov/fdc/v1/foods/list?api_key='
url_and_api_key = url+api_key

r = requests.get(url_and_api_key).json()
r = r[0:5]

def apidata_to_json():
    with sql.connect("database.db") as con:
        cur = con.cursor()
        for i in range(0, len(r)):
            cur.execute("INSERT INTO food (item, protein, fat) values (?, ?, ?)", (r[i]['description'], r[i]['foodNutrients'][0]['amount'], r[i]['foodNutrients'][1]['amount']))
        con.commit()

@app.errorhandler(404)
def page_not_found(e):
    return "Page not found", 404

@app.route('/')
def home():
    con = sql.connect("database.db")
    con.row_factory = sql.Row
    cur = con.cursor()
    cur.execute("select * from food")
    results = cur.fetchall()
    return render_template("homepage.html", rows = results)

@app.route('/delete/<id>', methods=['DELETE'])
def guide_delete(id):
    con = sql.connect("database.db")
    con.row_factory = sql.Row
    cur = con.cursor()
    cur.execute("select * from food where id=?", id)
    cur.commit()
    return "item deletted"

@app.route('/update')
def update():
    return 'update'

@app.route('/individual', methods=['GET'])
def api_route():
    query_params = request.args
    print(query_params)

    id = query_params.get("id")
    item = query_params.get("item")
    protein = query_params.get("protein")
    fat = query_params.get("fat")

    to_filter = []
    query = "select * from food where"

    if(id):
        query += ' id=? AND'
        to_filter.append(id)
    if(item):
        query += ' item=? AND'
        to_filter.append(item)
    if(protein):
        query += ' protein=? AND'
        to_filter.append(protein)
    if(fat):
        query += ' fat=? AND'
        to_filter.append(fat)
    if(not id and not item and not protein and not fat):
        return page_not_found(404)

    query = query[:-4]

    con = sql.connect('database.db')
    cur = con.cursor()
    results = cur.execute(query, to_filter).fetchall()

    if not results:
        return page_not_found(404)

    protein_results = cur.execute("select protein from food").fetchall()
    total_protein = 0

    for j in range(0, len(protein_results)):
        total_protein += protein_results[j][0]

    avg_protein = round((total_protein/len(protein_results)), 2)

    fat_results = cur.execute("select fat from food").fetchall()
    total_fat = 0

    for j in range(0, len(fat_results)):
        total_fat += fat_results[j][0]

    avg_fat = round((total_fat/len(fat_results)), 2)

    return "{} has a protein of {} g and fat of {} g compared to the average of {} g and {} g respectively.".format(results[0][1], results[0][2], results[0][3], avg_protein, avg_fat)

if __name__ == "__main__":
    app.run(debug = True)
