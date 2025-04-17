import http.client
import json
import requests


class AngelBrokingAPI:
    def __init__(self,base_url,client_code,password,totp,trading_symbol):
        self.base_url = base_url
        self.client_code = client_code
        self.password = password
        self.totp = totp
        self.private_key = 'IeQjnt6O'
        self.tradingsymbol=trading_symbol

    def login(self):
        payload = json.dumps({
            "clientcode": self.client_code,
            "password": self.password,
            "totp": self.totp
        })
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'X-UserType': 'USER',
            'X-SourceID': 'WEB',
            'X-ClientLocalIP': 'CLIENT_LOCAL_IP',
            'X-ClientPublicIP': 'CLIENT_PUBLIC_IP',
            'X-MACAddress': 'MAC_ADDRESS',
            'X-PrivateKey': self.private_key
        }
        headers_bytes = {key.encode(): value.encode() for key, value in headers.items()}
        conn = http.client.HTTPSConnection(self.base_url)
        conn.request("POST", "/rest/auth/angelbroking/user/v1/loginByPassword", payload.encode(), headers_bytes)
        res = conn.getresponse()
        data = res.read()
        print(data.decode("utf-8"))
        jdata=json.loads(data.decode("utf-8"))
        self.refresh_token=jdata['data']['refreshToken']
        self.jwtToken=jdata['data']['jwtToken']
        with open("tokens.json", "w") as f:
            f.write(json.dumps({"JWT": self.jwtToken, "REFRESH_TOKEN": self.refresh_token}))


    def generate_token(self):
        with open("tokens.json", "r") as f:
            token_file = f.read()
            d = json.loads(token_file)
            self.refresh_token = d.get("REFRESH_TOKEN")
            self.jwtToken = d.get("JWT")

        payload = {
            "refreshToken": self.refresh_token
        }
        headers = {
            'Authorization': 'Bearer ' + self.jwtToken,
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'X-UserType': 'USER',
            'X-SourceID': 'WEB',
            'X-ClientLocalIP': 'CLIENT_LOCAL_IP',
            'X-ClientPublicIP': 'CLIENT_PUBLIC_IP',
            'X-MACAddress': 'MAC_ADDRESS',
            'X-PrivateKey': self.private_key
        }
        conn = http.client.HTTPSConnection(self.base_url)
        conn.request("POST", "/rest/auth/angelbroking/jwt/v1/generateTokens", json.dumps(payload), headers)
        res = conn.getresponse()
        data = res.read()
        jdata=json.loads(data.decode("utf-8"))
        self.jwtToken=jdata['data']['jwtToken']
        self.refresh_token=jdata['data']['refreshToken']
        with open("tokens.json", "w") as f:
            f.write(json.dumps({"JWT": self.jwtToken, "REFRESH_TOKEN": self.refresh_token}))
        # print(data.decode("utf-8"))

    def place_order(self,quantity,ordertype,variety,producttype,duration,stoploss):
        self.fetch_data()
        payload = {
            "exchange": self.exchange,
            "symboltoken": self.token,
            "tradingsymbol": self.tradingsymbol,
            "quantity": str(quantity*self.lotsize),
            "disclosedquantity": 0,
            "transactiontype": "BUY",
            "ordertype": ordertype,
            "variety": variety,
            "producttype": producttype,
            "duration": duration,
            # "stoploss": stoploss,
            # "squareoff":"0",
        }
        headers = {
            'Authorization': 'Bearer ' + self.jwtToken,
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'X-UserType': 'USER',
            'X-SourceID': 'WEB',
            'X-ClientLocalIP': 'CLIENT_LOCAL_IP',
            'X-ClientPublicIP': 'CLIENT_PUBLIC_IP',
            'X-MACAddress': 'MAC_ADDRESS',
            'X-PrivateKey': self.private_key
        }
        conn = http.client.HTTPSConnection(self.base_url)
        conn.request("POST", "/rest/secure/angelbroking/order/v1/placeOrder", json.dumps(payload), headers)
        res = conn.getresponse()
        data = res.read()
        print(data.decode("utf-8"))

    def sell_order(self,quantity,ordertype,variety,producttype,duration,stoploss):
        self.fetch_data()
        payload = {
            "exchange": self.exchange,
            "symboltoken": self.token,
            "tradingsymbol": self.tradingsymbol,
            "quantity": str(quantity*self.lotsize),
            "disclosedquantity": 0,
            "transactiontype": "SELL",
            "ordertype": ordertype,
            "variety": variety,
            "producttype": producttype,
            "duration": duration,
            # "stoploss": stoploss,
            # "squareoff":"0",
        }
        headers = {
            'Authorization': 'Bearer ' + self.jwtToken,
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'X-UserType': 'USER',
            'X-SourceID': 'WEB',
            'X-ClientLocalIP': 'CLIENT_LOCAL_IP',
            'X-ClientPublicIP': 'CLIENT_PUBLIC_IP',
            'X-MACAddress': 'MAC_ADDRESS',
            'X-PrivateKey': self.private_key
        }
        conn = http.client.HTTPSConnection(self.base_url)
        conn.request("POST", "/rest/secure/angelbroking/order/v1/placeOrder", json.dumps(payload), headers)
        res = conn.getresponse()
        data = res.read()
        print(data.decode("utf-8"))

    def logout(self):
        payload = {
            "clientcode": self.client_code
        }
        headers = {
            'Authorization': self.bearer_token,
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'X-UserType': 'USER',
            'X-SourceID': 'WEB',
            'X-ClientLocalIP': 'CLIENT_LOCAL_IP',
            'X-ClientPublicIP': 'CLIENT_PUBLIC_IP',
            'X-MACAddress': 'MAC_ADDRESS',
            'X-PrivateKey': self.private_key
        }
        conn = http.client.HTTPSConnection(self.base_url)
        conn.request("POST", "/rest/secure/angelbroking/user/v1/logout", json.dumps(payload), headers)
        res = conn.getresponse()
        data = res.read()
        print(data.decode("utf-8"))

    def fetch_data(self):
        response = requests.get("https://margincalculator.angelbroking.com/OpenAPI_File/files/OpenAPIScripMaster.json")
        if response.status_code == 200:
            data = response.json()
            for item in data:
                if str(item.get('symbol'))==self.tradingsymbol:
                    self.token = str(item.get('token'))
                    self.exchange=str(item.get('exch_seg'))
                    self.lotsize=int(item.get('lotsize'))
                    break
        else:
            print("Invalid Trading Symbol:",self.tradingsymbol)
            return None

# if __name__ == "__main__":
    # angel_api = AngelBrokingAPI(base_url,client_code,password,totp,trading_symbol)
    # angel_api.login()
    # angel_api.generate_token()
    # angel_api.place_order(quantity,transactiontype,ordertype,variety,producttype,duration)
    # angel_api.logout()
