import urllib.request, json, traceback

try:
    req = urllib.request.Request('http://127.0.0.1:8000/auth/signup', data=json.dumps({'email': 'test10@example.com', 'password': 'password123'}).encode(), headers={'Content-Type': 'application/json'})
    res = urllib.request.urlopen(req)
    print("SUCCESS", res.read().decode())
except Exception as e:
    with open("error_log.txt", "w") as f:
        f.write(str(e) + "\n")
        if hasattr(e, "read"):
            f.write(e.read().decode())
