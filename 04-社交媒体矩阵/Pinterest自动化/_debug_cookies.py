import sqlite3
db = r"C:\Users\DELL\AppData\Local\Microsoft\Edge\User Data\Default\Network\Cookies"
conn = sqlite3.connect(db)
c = conn.cursor()
c.execute("SELECT host_key, name, length(encrypted_value), hex(substr(encrypted_value,1,35)) FROM cookies WHERE host_key LIKE '%pinterest%' LIMIT 5")
for r in c.fetchall():
    print(f"host={r[0]}  name={r[1]}  len={r[2]}  hex={r[3]}")
conn.close()
