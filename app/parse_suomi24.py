import os
import glob
import re
import psycopg2
from psycopg2.extras import execute_values

DB_CONFIG = {
    "dbname": "suomi24",
    "user": "postgres",
    "password": "secret",
    "host": "suomi24db",
    "port": "5432"
}

hate_keywords = ["vihapuhe", "rasismi", "rasistinen", "syrjintä",
    "vihaa", "viha", "vihaan", "neekeri", "homo", "lesbo",
    "maahanmuuttaja", "mamu", "muslimi", "juutalainen",
    "homofobia", "antisemitismi", "transu", "transsukupuolinen", "natsi"]

def save_to_db(records):
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    execute_values(
        cur,
        "INSERT INTO messages (title, content, date) VALUES %s",
        records
    )
    conn.commit()
    cur.close()
    conn.close()

def parse_vrt_from_folder(folder_path):
    vrt_files = glob.glob(os.path.join(folder_path, "*.vrt"))
    print(f"Löytyi {len(vrt_files)} vrt-tiedostoa.")

    if vrt_files:
        filename = vrt_files[0]
        print(f"Käsitellään tiedosto: {filename}")
        with open(filename, 'r', encoding='utf-8') as f:
            text_block = []
            date = None
            title = None
            for line in f:
                line = line.strip()

                if line.startswith("<text"):
                    match_title = re.search(r'title="(.*?)"', line)
                    if match_title:
                        title = match_title.group(1)
                    else:
                        title = None
                    match = re.search(r'date="(.*?)"', line)
                    if match:
                        date = match.group(1)
                    else:
                        date = None
                    text_block = []

                elif line.startswith("</text>"):
                    content = " ".join(text_block).lower()
                    if any(term in content for term in hate_keywords):
                        print(f"HAKUSANA LÖYTYI: {date} {content[:100]}...")
                        save_to_db([(title, content, date)])
                    text_block = []

                elif not line.startswith("<"):
                    word = line.split("\t")[0]
                    text_block.append(word)