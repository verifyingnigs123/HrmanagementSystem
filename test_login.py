import json
import urllib.request
import urllib.error

data = json.dumps({'username': 'employee1', 'password': 'emp123'}).encode()
req = urllib.request.Request('http://192.168.254.107:8000/api/auth/jwt/token/', data=data, headers={'Content-Type': 'application/json'})

try:
    r = urllib.request.urlopen(req)
    print("Status: 200 OK")
    print(r.read().decode())
except urllib.error.HTTPError as e:
    print(f'Status: {e.code}')
    print(e.read().decode())
