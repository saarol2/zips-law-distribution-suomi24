import psycopg2
import time

# Odotetaan hetki, että tietokanta ehtii käynnistyä
time.sleep(5)

print("Connecting to PostgreSQL...")

conn = psycopg2.connect(
    dbname="suomi24",
    user="postgres",
    password="secret",
    host="db",
    port=5432
)
cur = conn.cursor()

# Luodaan taulu viesteille
cur.execute("""
CREATE TABLE IF NOT EXISTS messages (
    id SERIAL PRIMARY KEY,
    title TEXT,
    content TEXT,
    date DATE
);
""")
conn.commit()

print("Database connection successful and table created!")

cur.close()
conn.close()
