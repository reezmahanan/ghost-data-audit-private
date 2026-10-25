import sqlite3
conn = sqlite3.connect(':memory:')
with open('dataset/evidence/databases/customer_data_inventory_20260916.sql', encoding='utf-8') as f:
    conn.executescript(f.read())
c = conn.cursor()
tables = [r[0] for r in c.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
print('Tables in inventory 20260916:', tables)
for t in tables:
    count = c.execute(f"SELECT count(*) FROM {t}").fetchone()[0]
    row = c.execute(f"SELECT * FROM {t} LIMIT 1").fetchone()
    print(f"  {t}: {count} rows. Sample: {row}")
