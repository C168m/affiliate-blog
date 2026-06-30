import sqlite3
db = r"D:\AI-Money-Machine\04-社交媒体矩阵\Pinterest自动化\edge_pin_profile\Default\Network\Cookies"
conn = sqlite3.connect(db)
c = conn.cursor()
c.execute("SELECT host_key, name, length(encrypted_value) FROM cookies WHERE host_key LIKE '%pinterest%' ORDER BY name")
rows = c.fetchall()
print(f"Total Pinterest cookies: {len(rows)}")
for r in rows:
    print(f"  {r[0]:30s} | {r[1]:25s} | enc_len={r[2]}")
conn.close()
