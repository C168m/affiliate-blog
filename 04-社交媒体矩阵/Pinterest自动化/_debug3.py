import json, base64
with open(r"C:\Users\DELL\AppData\Local\Microsoft\Edge\User Data\Local State", "r", encoding="utf-8") as f:
    state = json.load(f)
ek_b64 = state["os_crypt"]["encrypted_key"]
ek_raw = base64.b64decode(ek_b64)
print(f"Raw key bytes ({len(ek_raw)}): {ek_raw.hex()}")
print(f"Prefix type: {ek_raw[:5]}")
print(f"Prefix hex: {ek_raw[:5].hex()}")
print(f"Prefix text: {ek_raw[:5]}")
