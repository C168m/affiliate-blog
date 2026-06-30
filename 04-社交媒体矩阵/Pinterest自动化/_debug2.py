import sqlite3, json, base64
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import win32crypt

LOCAL_STATE = r"C:\Users\DELL\AppData\Local\Microsoft\Edge\User Data\Local State"
COOKIES_DB = r"C:\Users\DELL\AppData\Local\Microsoft\Edge\User Data\Default\Network\Cookies"

with open(LOCAL_STATE, "r", encoding="utf-8") as f:
    state = json.load(f)
ek_b64 = state["os_crypt"]["encrypted_key"]
ek = base64.b64decode(ek_b64)[5:]
key = win32crypt.CryptUnprotectData(ek, None, None, None, 0)[1]
print(f"Key: {key.hex()[:20]}... ({len(key)} bytes)")

conn = sqlite3.connect(COOKIES_DB)
c = conn.cursor()
c.execute("SELECT host_key, name, encrypted_value FROM cookies WHERE host_key LIKE '%pinterest%' AND name='_auth' LIMIT 1")
host, name, enc = c.fetchone()
conn.close()

print(f"Cookie: {name} on {host}")
print(f"enc value len: {len(enc)}")
print(f"prefix: {enc[:3]} => {enc[:3].hex()}")

nonce = enc[3:15]
ct = enc[15:]
print(f"nonce len: {len(nonce)}, ct+tag len: {len(ct)}")

aesgcm = AESGCM(key)
try:
    val = aesgcm.decrypt(nonce, ct, None)
    print(f"DECRYPTED: {val.decode('utf-8')[:80]}")
except Exception as e:
    print(f"AESGCM FAIL: {e}")
    try:
        val = win32crypt.CryptUnprotectData(enc, None, None, None, 0)[1]
        print(f"DPAPI fallback: {val.decode('utf-8')[:80]}")
    except Exception as e2:
        print(f"DPAPI also FAIL: {e2}")
