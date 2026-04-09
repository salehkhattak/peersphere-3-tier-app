import urllib.request
import urllib.parse
from http.cookiejar import CookieJar

cj = CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))

try:
    resp = opener.open('http://127.0.0.1:5000/login')
    html = resp.read().decode('utf-8')
    import re
    csrf_token = re.search(r'name="csrf_token" value="([^"]+)"', html).group(1)
    
    data = urllib.parse.urlencode({'email': 'ahmed@uni.edu', 'password': 'password123', 'csrf_token': csrf_token}).encode('ascii')
    opener.open('http://127.0.0.1:5000/login', data)
    
    resp = opener.open('http://127.0.0.1:5000/messages/')
    print("Messages Status:", resp.getcode())
    print("Messages loaded successfully.")
except Exception as e:
    print("Error:", e)
    if hasattr(e, 'read'):
        with open('error_messages.html', 'wb') as f:
            f.write(e.read())
        print("Saved error to error_messages.html")
