import urllib.request
import urllib.parse
from http.cookiejar import CookieJar

# Setup cookie jar to maintain session
cj = CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))

# 1. Fetch login page to get CSRF token (if needed, but WTForms might require it)
try:
    resp = opener.open('http://127.0.0.1:5000/login')
    html = resp.read().decode('utf-8')
    import re
    csrf_token = re.search(r'name="csrf_token" value="([^"]+)"', html).group(1)
    
    # 2. Login
    data = urllib.parse.urlencode({'email': 'ahmed@uni.edu', 'password': 'password123', 'csrf_token': csrf_token}).encode('ascii')
    resp = opener.open('http://127.0.0.1:5000/login', data)
    
    # 3. Access Dashboard
    resp = opener.open('http://127.0.0.1:5000/dashboard')
    print("Dashboard Status:", resp.getcode())
    print("Dashboard loaded successfully.")
except Exception as e:
    print("Error:", e)
    if hasattr(e, 'read'):
        with open('error_dashboard.html', 'wb') as f:
            f.write(e.read())
        print("Saved error to error_dashboard.html")
