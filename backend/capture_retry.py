import urllib.request, json

try:
    req = urllib.request.Request('http://127.0.0.1:8000/auth/signup', data=json.dumps({'email': 'test11@example.com', 'password': 'password123'}).encode(), headers={'Content-Type': 'application/json'})
    res = urllib.request.urlopen(req)
    print("SUCCESS", res.read().decode())
except Exception as e:
    print("ERROR", str(e))
    if hasattr(e, "read"):
        print("CONTENT:", e.read().decode())
