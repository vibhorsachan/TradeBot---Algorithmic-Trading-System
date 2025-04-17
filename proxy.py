import json
import os
import requests
import random
from os.path import join, dirname
from dotenv import load_dotenv

dotenv_path = join(dirname(__file__), '.env').replace('webShare/','')
env = load_dotenv(dotenv_path)

LUMINATI_USERNAME = os.environ.get("LUMINATI_USERNAME")
LUMINATI_PASSWORD = os.environ.get("LUMINATI_PASSWORD")
LUMINATI_USERNAME_RES = os.environ.get("LUMINATI_USERNAME_RES")
LUMINATI_PASSWORD_RES = os.environ.get("LUMINATI_PASSWORD_RES")
LUMINATI_USERNAME_RET = os.environ.get("LUMINATI_USERNAME_RET")
LUMINATI_PASSWORD_RET = os.environ.get("LUMINATI_PASSWORD_RET")

OXYLABS_USERNAME = os.environ.get("OXYLABS_USERNAME")
OXYLABS_PASSWORD = os.environ.get("OXYLABS_PASSWORD")

# TEMP MEDIAFEVERR
# LUMINATI_USERNAME = 'um-customer-hl_55c3b71b-zone-datacenterinst'
# LUMINATI_PASSWORD = 'h5reasgrdu6547'

# SMART_P_USERNAME= "logsUser"
# SMART_P_PASSWORD= "sS2dq9yzuJs3m9rOZb"
SMART_P_USERNAME= "logsUser"
SMART_P_PASSWORD= "loBWjO54wnid4glbZ8"

PROXY_CHEAP_USER=os.environ.get("PROXY_CHEAP_USER")
PROXY_CHEAP_PASSWORD=os.environ.get("PROXY_CHEAP_PASSWORD")

COUNTRY_MAP = {"US": "USA","GB": "UK","UK": "UK","CA": "Canada","FR": "France","NL": "Netherlands","NLD": "Netherlands","DE": "Germany","CH": "Switzerland","AU": "Australia","SG": "Singapore","JP": "Japan","ID": "Indonesia","ES": "Spain","NO": "Norway","RU": "Russia","AT": "Austria","IT": "Italy","ITA": "Italy","HK": "HongKong","AE": "UnitedArabEmirates","BR": "Brazil","KR": "SouthKorea","PH": "Philippines","BE": "Belgium","BH": "Bahrain","BHR": "Bahrain","KW": "Kuwait","HR": "Croatia","HRV": "Croatia","SA": "SaudiArabia","ZA": "SouthAfrica","ZAF": "SouthAfrica","PT": "Portugal","PRT": "Portugal","MY": "Malaysia","MX": "Mexico","FI": "Finland","NZ": "NewZealand","CZ": "CzechRepublic","DK": "Denmark","AUT": "Austria","TW": "Taiwan","TR": "Turkey","TH": "Thailand","VN": "Vietnam","IL": "Israel","ISR": "Israel","IE": "Ireland","IRL": "Ireland","QA": "Qatar","QAT": "Qatar","Rus": "Russia","Hon": "HongKong","Sou": "SouthKorea","Sou": "SouthAfrica","PK": "Pakistan","PAK": "Pakistan","OM": "Oman","OMN": "Oman","CAN": "Canada","JPN": "Japan","GBR": "UK","DEU": "Germany","KOR": "SouthKorea","VNM": "Vietnam","RUS": "Russia","AUS": "Australia","CHE": "Switzerland","FRA": "France","SGP": "Singapore","USA": "USA","BRA": "Brazil","THA": "Thailand","IDN": "Indonesia","NOR": "Norway","DNK": "Denmark","MYS": "Malaysia","TWN": "Taiwan","CZE": "CzechRepublic","HKG": "HongKong","TUR": "Turkey","MEX": "Mexico","NZL": "NewZealand","BEL": "Belgium","SWE": "Sweden","FIN": "Finland","ESP": "Spain","POL": "Poland","PL": "Poland","ARE": "UnitedArabEmirates","JO": "Jordan","IR": "Iran","IRN": "Iran","JOR": "Jordan","EG": "Egypt","EGY": "Egypt","PHL": "Philippines","SE": "Sweden","KWT": "Kuwait","SAU": "SaudiArabia","MM": "Myanmar","MMR": "Myanmar","NG": "Nigeria","CO": "Colombia","COL": "Colombia","BD": "Bangladesh","BGD": "Bangladesh","PE": "Peru","PER": "Peru","CL": "Chile","CHL": "Chile","GR": "Greece","GRC": "Greece","CR": "CostaRica","CRI": "CostaRica","GH": "Ghana","GHA": "Ghana","SN": "Senegal","SEN": "Senegal","TN": "Tunisia","TUN": "Tunisia","UG": "Uganda","UGA": "Uganda","MA": "Morocco","MAR": "Morocco","CN": "China","CHN": "China","BO": "Bolivia","BOL": "Bolivia","LK": "SriLanka","LKA": "SriLanka","TZ": "Tanzania","TZA": "Tanzania","KE": "Kenya","KEN": "Kenya","UA": "Ukraine","UKR": "Ukraine","NGA": "Nigeria","IN": "India","IND": "India","MO": "Macau","MAC": "Macau","CI": "IvoryCoast","CIV": "IvoryCoast","CM": "Cameroon","CMR": "Cameroon","DZ": "Algeria","DZA": "Algeria","KH": "Cambodia","KHM": "Cambodia","AR": "Argentina","SK": "Slovakia","KZ": "Kazakhstan","BY": "Belarus","SY": "Syria"}

class SetupConnection:
    def __init__(self, campaign_name):
        self.campaign_name = campaign_name

    def connect(self, country='IN', premium=False, proxy_vendor='luminati', targeting_data={}, retention=False):
        session_id = str(random.random())
        if premium:
            if proxy_vendor=='luminati':
                # LUMINATI_USERNAME_RES = "um-customer-hl_2bc42eca-zone-sv_res"
                # LUMINATI_PASSWORD_RES = "mcskdjsdolk768"
                
                
                proxy_str = "brd" + LUMINATI_USERNAME_RES[2:] + "-country-" + str(country).upper() + "-session-" + session_id + ":" + LUMINATI_PASSWORD_RES + "@brd.superproxy.io:22225"
                print('Connecting to Proxy server:' + proxy_str)

            elif proxy_vendor=='oxylabs:targeting' and targeting_data.get("city"):
                city = str(random.choice(targeting_data.get("city")))
                proxy_str = ('customer-%s-cc-%s-city-%s:%s@pr.oxylabs.io:7777' %(OXYLABS_USERNAME, str(country).upper(), city, OXYLABS_PASSWORD))

            elif proxy_vendor=='smartproxy':
                proxy_str = "user-"+SMART_P_USERNAME+"-country-"+str(country.lower())+"-sessionduration-30:"+SMART_P_PASSWORD+"@gate.smartproxy.com:{}".format(str(random.randint(10000, 19999)))
                print('Connecting to Proxy server:' + proxy_str)

            elif proxy_vendor=='smartproxy:targeting' and targeting_data.get("city"):
                # city = str(random.choice(targeting_data.get("city")))
                city=str(targeting_data.get("city"))
                proxy_str = "user-"+SMART_P_USERNAME+"-country-"+str(country.lower())+"-city-"+str(city.lower())+"-sessionduration-30:"+SMART_P_PASSWORD+"@gate.smartproxy.com:{}".format(str(random.randint(10000, 19999)))
                print(proxy_str)
            elif proxy_vendor=='oxylabs':
                proxy_str = ('customer-%s-cc-%s:%s@pr.oxylabs.io:7777' %(OXYLABS_USERNAME, str(country).upper(), OXYLABS_PASSWORD))
                
            elif proxy_vendor=='proxycheap':
                proxy_str = PROXY_CHEAP_USER+":"+PROXY_CHEAP_PASSWORD+"country-"+COUNTRY_MAP.get(str(country).upper())+"@proxy.proxy-cheap.com:31112"

            else:
                proxy_str = ('http://customer-%s-cc-%s:%s@pr.oxylabs.io:7777' %(OXYLABS_USERNAME, str(country).upper(), OXYLABS_PASSWORD))

        elif not retention:
            proxy_str = "brd" + LUMINATI_USERNAME[2:] + "-country-" + str(country).upper() + "-session-" + session_id + ":" + LUMINATI_PASSWORD + "@brd.superproxy.io:22225"

        else:
            proxy_str = "brd" + LUMINATI_USERNAME_RET[2:] + "-country-" + str(country).upper() + "-session-" + session_id + ":" + LUMINATI_PASSWORD_RET + "@brd.superproxy.io:22225"
            print('Connecting to Proxy server:' + proxy_str)

        os.environ['http_proxy'] = 'http://'+proxy_str
        os.environ['https_proxy'] = 'http://'+proxy_str

    def disconnect(self):
        if os.environ.get('http_proxy'):
            del os.environ['http_proxy']
        if os.environ.get('https_proxy'):
            del os.environ['https_proxy']

    def getCurrentIP(self):
        try:
            get_ip = requests.get('http://lumtest.com/myip.json')
            return json.loads(get_ip.text).get('ip')
        except:
            try:
                get_ip = requests.get('https://api.ipify.org/?format=json')
                return json.loads(get_ip.text).get('ip')
            except:
                try:
                    get_ip = requests.get('https://www.trackip.net/ip?json')
                    return json.loads(get_ip.text).get('IP')
                except Exception as e:
                    print("###########  FAILED TO FETCH IP   ###########")
                    print(e)
                    return "0.0.0.0"


# vpn = SetupConnection("mcdonaldsriyadh")
# vpn.connect("SA", premium=True, proxy_vendor="smartproxy", targeting_data={"city": ["riyadh"]})

# print(vpn.getCurrentIP())
# vpn.disconnect()