import requests

url = 'https://api.upstox.com/v2/login/authorization/token'
headers = {
    'accept': 'application/json',
    'Content-Type': 'application/x-www-form-urlencoded',
}

data = {
    'code': '6sYNdT',
    'client_id': '4d10741a-cf5d-4b31-9fae-506d93ae7704',
    'client_secret': 'qllw76f9g1',
    'redirect_uri': 'https://www.google.com/',
    'grant_type': 'authorization_code',
}

response = requests.post(url, headers=headers, data=data)

print(response.status_code)
print(response.json())
