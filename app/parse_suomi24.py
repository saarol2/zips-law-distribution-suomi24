import os
import re
import zipfile
import psycopg2
from io import StringIO
from psycopg2 import sql


# CONFIG
DB_CONFIG = {
    "dbname": os.environ.get("POSTGRES_DB", "suomi24"),
    "user": os.environ.get("POSTGRES_USER", "postgres"),
    "password": os.environ.get("POSTGRES_PASSWORD", "secret"),
    "host": os.environ.get("POSTGRES_HOST", "suomi24db"),
    "port": os.environ.get("POSTGRES_PORT", "5432")
}

ZIP_PATH = "/data/suomi24-2001-2017-vrt-v1-1.zip"
BATCH_SIZE = 20000


# KEYWORDS
hate_keywords = [
    "vihapuhe", "rasismi", "rasistinen", "syrjintä",
    "vihaa", "viha", "vihaan", "neekeri", "homo", "lesbo",
    "maahanmuuttaja", "mamu", "muslimi", "juutalainen",
    "homofobia", "antisemitismi", "transu", "natsi"
]

friendly_keywords = [
    "ystävällinen", "kohteliaisuus", "vapaus",
    "ystävällisyys", "kunnioitus", "reilu", "tasa-arvo",
    "suvaitsevaisuus", "rauha", "ystävä",
    "ystävällisesti", "kaveri"
]

hate_pattern = re.compile(r'\b(' + '|'.join(re.escape(term) for term in hate_keywords) + r')\b', re.IGNORECASE)
friendly_pattern = re.compile(r'\b(' + '|'.join(re.escape(term) for term in friendly_keywords) + r')\b', re.IGNORECASE)

# DATABASE SAVE
def save_batch_to_db(records):
    """Efficient bulk insert with COPY FROM STDIN."""
    if not records:
        return

    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    buffer = StringIO()
    for r in records:
        buffer.write("\t".join("" if v is None else str(v) for v in r) + "\n")
    buffer.seek(0)

    cur.copy_from(buffer, "messages", sep="\t", columns=("title", "content", "date", "query_type"))
    conn.commit()
    cur.close()
    conn.close()


# PARSING LOGIC
def parse_vrt_from_zip(zip_path):
    """Stream zip file contents without extracting."""
    batch = []
    processed = 0

    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        vrt_files = sorted([n for n in zip_ref.namelist() if n.endswith('.vrt')])
        print(f"📦 Found {len(vrt_files)} .vrt files in zip.", flush=True)

        if vrt_files:
            filename = vrt_files[0]
            print(f"🔍 Processing only file: {filename}", flush=True)
            with zip_ref.open(filename) as f:
                text_block, date, title = [], None, None
                for raw_line in f:
                    line = raw_line.decode('utf-8', errors='ignore').strip()

                    if line.startswith("<text"):
                        date_match = re.search(r'date="(.*?)"', line)
                        title_match = re.search(r'title="(.*?)"', line)
                        date = date_match.group(1) if date_match else None
                        title = title_match.group(1) if title_match else None
                        text_block = []

                    elif line.startswith("</text>"):
                        content = " ".join(text_block).lower()

                        found_hate = bool(hate_pattern.search(content))
                        found_friendly = bool(friendly_pattern.search(content))

                        if found_hate or found_friendly:
                            query_type = (
                                "both" if found_hate and found_friendly
                                else "hate" if found_hate
                                else "friendly"
                            )
                            batch.append((title, content, date, query_type))

                            if len(batch) >= BATCH_SIZE:
                                save_batch_to_db(batch)
                                processed += len(batch)
                                print(f"💾 Saved {processed} messages...", flush=True)
                                batch.clear()

                        text_block = []

                    elif not line.startswith("<"):
                        word = line.split("\t")[0]
                        text_block.append(word)

    if batch:
        save_batch_to_db(batch)
        print(f"✅ Processed {len(batch)} messages.", flush=True)

    print("🎯 Done!", flush=True)