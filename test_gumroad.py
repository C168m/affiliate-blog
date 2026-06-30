import sys, os, json, requests
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from dotenv import load_dotenv
load_dotenv()

token = os.getenv('GUMROAD_ACCESS_TOKEN', '')
if not token:
    print('ERROR: No Gumroad token')
    sys.exit(1)

print(f'Token: {token[:20]}...')

# list existing products
resp = requests.get(
    'https://api.gumroad.com/v2/products',
    headers={'Authorization': f'Bearer {token}'},
    timeout=15
)
print(f'GET products: {resp.status_code}')
if resp.status_code == 200:
    data = resp.json()
    prods = data.get('products', [])
    print(f'Existing: {len(prods)}')
    for p in prods[:3]:
        name = p.get('name', '?')[:50]
        url = p.get('short_url', '?')
        price = p.get('price', 0)
        print(f'  {name} - {url} - {price}c')

# create product
payload = {
    'name': '100+ AI Marketing ChatGPT Prompts - Ultimate Bundle 2026',
    'description': 'Premium AI prompt pack. 100+ ready-to-use prompts for marketing.',
    'price': 999,
    'published': 'true'
}
print('\nCreating product...')
resp2 = requests.post(
    'https://api.gumroad.com/v2/products',
    headers={'Authorization': f'Bearer {token}'},
    data=payload,
    timeout=30
)
print(f'POST status: {resp2.status_code}')
data2 = resp2.json() if resp2.headers.get('content-type', '').startswith('application/json') else {}
if resp2.status_code in (200, 201):
    pd = data2.get('product', data2)
    print(f'SUCCESS: id={pd.get("id")} url={pd.get("short_url")}')
else:
    print(f'Body: {resp2.text[:300]}')
