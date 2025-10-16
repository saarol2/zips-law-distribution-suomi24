
import os
import re
import zipfile
import psycopg2
from psycopg2.extras import execute_values


# Read database settings from environment variables
DB_CONFIG = {
    "dbname": os.environ.get("POSTGRES_DB", "suomi24"),
    "user": os.environ.get("POSTGRES_USER", "postgres"),
    "password": os.environ.get("POSTGRES_PASSWORD", "secret"),
    "host": os.environ.get("POSTGRES_HOST", "suomi24db"),
    "port": os.environ.get("POSTGRES_PORT", "5432")
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

def parse_vrt_from_folder(zip_path):
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        vrt_files = sorted([name for name in zip_ref.namelist() if name.endswith('.vrt')])
        print(f"Found {len(vrt_files)} vrt files in the zip.")

        if vrt_files:
            filename = vrt_files[0]
            print(f"Processing file: {filename}")
            with zip_ref.open(filename) as f:
                text_block = []
                date = None
                title = None
                for raw_line in f:
                    line = raw_line.decode('utf-8').strip()

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
                            print(f"Keyword found: {date} {content[:100]}...")
                            save_to_db([(title, content, date)])
                        text_block = []

                    elif not line.startswith("<"):
                        word = line.split("\t")[0]
                        text_block.append(word)