import sqlite3
import json

con = sqlite3.connect("orbital.db")

cur = con.cursor()

cur.execute("""DROP TABLE IF EXISTS titles;""")

cur.execute(
    """
    CREATE TABLE IF NOT EXISTS titles
        (id integer, \
        title_number text, \
        title_class text, \
        content text)
    """
)

with open("data.json", "r") as data:
    cur.executemany(
        "INSERT INTO titles (id, title_number, title_class, content) "
        "VALUES (:id,:title_number,:title_class,:content)",
        json.load(data),
    )

con.commit()
cur.close()
con.close()
