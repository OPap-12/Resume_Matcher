import urllib.request, json, traceback

try:
    req = urllib.request.Request('http://127.0.0.1:8001/auth/signup', data=json.dumps({'email': 'test20@example.com', 'password': 'password123'}).encode(), headers={'Content-Type': 'application/json'})
    res = urllib.request.urlopen(req)
    with open("response_log2.txt", "w") as f:
        f.write("SUCCESS\n")
        f.write(res.read().decode())
except Exception as e:
    with open("response_log2.txt", "w") as f:
        f.write(str(e) + "\n")
        if hasattr(e, "read"):
            f.write(e.read().decode())
