import sqlite3, json, os, base64
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import win32crypt

EDGE_COOKIES = r"C:\Users\DELL\AppData\Local\Microsoft\Edge\User Data\Default\Network\Cookies"
EDGE_LOCAL_STATE = r"C:\Users\DELL\AppData\Local\Microsoft\Edge\User Data\Local State"
OUTPUT = r"D:\AI-Money-Machine\04-社交媒体矩阵\Pinterest自动化\pinterest_cookies.json"

# Step 1: Get decryption key from Local State
with open(EDGE_LOCAL_STATE, "r", encoding="utf-8") as f:
    local_state = json.load(f)
encrypted_key_b64 = local_state["os_crypt"]["encrypted_key"]
encrypted_key = base64.b64decode(encrypted_key_b64)[5:]  # strip DPAPI prefix
key = win32crypt.CryptUnprotectData(encrypted_key, None, None, None, 0)[1]
print(f"[KEY] Decrypted AES key ({len(key)*8}-bit)")

# Step 2: Query Pinterest cookies from Edge SQLite DB
conn = sqlite3.connect(EDGE_COOKIES)
cursor = conn.cursor()
cursor.execute("SELECT host_key, name, encrypted_value, path, expires_utc, is_secure, is_httponly FROM cookies WHERE host_key LIKE '%pinterest%'")
rows = cursor.fetchall()
print(f"[DB] Found {len(rows)} Pinterest cookies in Edge")

# Step 3: Decrypt each cookie
cookies = []
for host_key, name, enc_value, path, expires, secure, httponly in rows:
    # Modern Edge (v80+): AES-256-GCM with 12-byte nonce prefix
    nonce = enc_value[3:15]
    ciphertext = enc_value[15:]
    aesgcm = AESGCM(key)
    try:
        value = aesgcm.decrypt(nonce, ciphertext, None).decode("utf-8")
    except Exception:
        # Fallback: old DPAPI-only encryption
        try:
            value = win32crypt.CryptUnprotectData(enc_value, None, None, None, 0)[1].decode("utf-8")
        except:
            continue
    
    cookie = {
        "name": name,
        "value": value,
        "domain": host_key.replace(".pinterest.com", ".pinterest.com") if "pinterest" in host_key else host_key,
        "path": path or "/",
        "secure": bool(secure),
        "httpOnly": bool(httponly),
    }
    cookies.append(cookie)
    print(f"  [{host_key}] {name} = {value[:40]}...")

conn.close()

# Step 4: Save
with open(OUTPUT, "w", encoding="utf-8") as f:
    json.dump(cookies, f, indent=2, ensure_ascii=False)
print(f"[DONE] Saved {len(cookies)} cookies to {OUTPUT}")
