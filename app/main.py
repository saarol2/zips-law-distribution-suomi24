
import psycopg2
import time
import os
from parse_suomi24 import parse_vrt_from_folder


# Read settings from environment variables
DB_NAME = os.environ.get("POSTGRES_DB", "suomi24")
DB_USER = os.environ.get("POSTGRES_USER", "postgres")
DB_PASSWORD = os.environ.get("POSTGRES_PASSWORD", "secret")
DB_HOST = os.environ.get("POSTGRES_HOST", "db")
DB_PORT = int(os.environ.get("POSTGRES_PORT", 5432))
ZIP_PATH = os.environ.get("ZIP_PATH", "/data/suomi24.zip")

# Wait a moment for the database to start
time.sleep(5)


print("Connecting to PostgreSQL...")

conn = psycopg2.connect(
    dbname=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=DB_PORT
)
cur = conn.cursor()

# Create the messages table if it does not exist
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

parse_vrt_from_folder(ZIP_PATH)

cur.close()
conn.close()
