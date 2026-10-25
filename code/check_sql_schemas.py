import glob
import sqlite3
import sys

sys.stdout.reconfigure(encoding='utf-8')

for sql_file in sorted(glob.glob('dataset/evidence/databases/*.sql')):
    conn = sqlite3.connect(':memory:')
    with open(sql_file, 'r', encoding='utf-8') as f:
        sql = f.read()
    try:
        conn.executescript(sql)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [r[0] for r in cursor.fetchall()]
        print(f"{sql_file} : {tables}")
    except Exception as e:
        print(f"{sql_file} : error={e}")
