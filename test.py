import urllib.request
import urllib.error

try:
    urllib.request.urlopen('http://127.0.0.1:5000/register')
except urllib.error.HTTPError as e:
    with open('error.html', 'wb') as f:
        f.write(e.read())
