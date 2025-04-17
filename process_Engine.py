import urllib.parse
import requests,json
from pathlib import Path
from fake_useragent import UserAgent
import time
from datetime import datetime
import gzip
import csv
from io import BytesIO
import codecs
import os


class MarketDataAPI:
    def __init__(self, symbol, authorization, instrument_key, expiry_date) -> None:
        self.ua = UserAgent()
        self.symbol = symbol
        self.encoded = False
        self.OC_symbol = {'NIFTY 50': 'NIFTY', 'NIFTY BANK': 'BANKNIFTY', 'NIFTY FINANCIAL SERVICES': 'FINNIFTY', 'NIFTY MID SELECT': 'NIFTYMID50'}.get(symbol)
        self.instrument_key = instrument_key
        self.expiry_date = expiry_date 
        self.base_url = "https://api.upstox.com/v2"
        self.authorization= authorization
        self.lowerLimit = 0
        self.upperLimit = 0
        self.option_chain_file_path = "./upstox_option_chain_socket/"

    def getCookies(self):
        self.user_agent = self.ua.random
        r = requests.get("https://www.nseindia.com/get-quotes/derivatives?symbol={}".format(self.symbol), timeout=10 ,headers={"User-Agent": self.user_agent})
        cookies = r.headers.get('Set-Cookie')
        return cookies

    def getMarktePrice(self):
        if not self.encoded:
            self.symbol = urllib.parse.quote(self.symbol, safe="")
            self.encoded = True
        cookies = self.getCookies()
        nsit = nseappid = bm_sz = bm_sv = _abck = ak_bmsc = ""

        if 'nsit=' in cookies:
            nsit = "nsit="+cookies.split('nsit=')[1].split(';')[0]+';'
        if 'nseappid=' in cookies:
            nseappid = 'nseappid='+cookies.split('nseappid=')[1].split(';')[0]+';'
        if 'bm_sz=' in cookies:
            bm_sz = 'bm_sz='+cookies.split('bm_sz=')[1].split(';')[0]+';'
        if 'bm_sv=' in cookies:
            bm_sv = 'bm_sv='+cookies.split('bm_sv=')[1].split(';')[0]+';'
        if '_abck=' in cookies:
            _abck = '_abck='+cookies.split('_abck=')[1].split(';')[0]+';'
        if 'ak_bmsc=' in cookies:
            ak_bmsc = 'ak_bmsc='+cookies.split('ak_bmsc=')[1].split(';')[0]+';'
        
        headers = {
            "accept": "*/*",
            "accept-language": "en-GB,en-US;q=0.9,en;q=0.8,hi;q=0.7",
            "sec-ch-ua": "\"Google Chrome\";v=\"123\", \"Not:A-Brand\";v=\"8\", \"Chromium\";v=\"123\"",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "\"Linux\"",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "cookie": "{} {} AKA_A2=A; {} {} defaultLang=en; {} {}".format(nsit, nseappid, bm_sz, bm_sv, _abck, ak_bmsc),
            "Referer": "https://www.nseindia.com/get-quotes/derivatives?symbol={}".format(self.symbol),
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "User-Agent": self.user_agent
        }
        url = "https://www.nseindia.com/api/chart-databyindex?index={}&indices=true".format(self.symbol)
        response = requests.get(url, timeout=10, headers=headers)
        try:
            resp = json.loads(response.text)
        except:
            resp = {}
            print("Failed to load JSON DATA: {}".format(str(response.text)))
        if resp.get('grapthData'):
            last_price = resp.get('grapthData')[-1]
            return last_price[1]
        else:
            print("NO DATA FOUND FOR SYMBOL: {}".format(self.symbol))
            return None

    def getLTPPrice(self, strike_price, options, expiry):
        if options == "PUT":
            option = 'PE'
        elif options == "CALL":
            option = 'CE'
        symbol = "OPTIDX{}{}{}{}.00".format(self.OC_symbol, expiry, option, str(strike_price))
        symbol = urllib.parse.quote(symbol, safe="")
        cookies = self.getCookies()
        nsit = nseappid = bm_sz = bm_sv = _abck = ak_bmsc = ""

        if 'nsit=' in cookies:
            nsit = "nsit="+cookies.split('nsit=')[1].split(';')[0]+';'
        if 'nseappid=' in cookies:
            nseappid = 'nseappid='+cookies.split('nseappid=')[1].split(';')[0]+';'
        if 'bm_sz=' in cookies:
            bm_sz = 'bm_sz='+cookies.split('bm_sz=')[1].split(';')[0]+';'
        if 'bm_sv=' in cookies:
            bm_sv = 'bm_sv='+cookies.split('bm_sv=')[1].split(';')[0]+';'
        if '_abck=' in cookies:
            _abck = '_abck='+cookies.split('_abck=')[1].split(';')[0]+';'
        if 'ak_bmsc=' in cookies:
            ak_bmsc = 'ak_bmsc='+cookies.split('ak_bmsc=')[1].split(';')[0]+';'
        
        headers = {
            "accept": "*/*",
            "accept-language": "en-GB,en-US;q=0.9,en;q=0.8,hi;q=0.7",
            "sec-ch-ua": "\"Google Chrome\";v=\"123\", \"Not:A-Brand\";v=\"8\", \"Chromium\";v=\"123\"",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "\"Linux\"",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "cookie": "{} {} AKA_A2=A; {} {} defaultLang=en; {} {}".format(nsit, nseappid, bm_sz, bm_sv, _abck, ak_bmsc),
            "Referer": "https://www.nseindia.com/get-quotes/derivatives?symbol={}".format(self.symbol),
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "User-Agent": self.user_agent
        }
        url = "https://www.nseindia.com/api/chart-databyindex?index={}&indices=true".format(symbol)
        response = requests.get(url, timeout=10, headers=headers)
        try:
            resp = json.loads(response.text)
        except:
            resp = {}
            print("Failed to load JSON DATA: {}".format(str(response.text)))
        if resp.get('grapthData'):
            last_price = resp.get('grapthData')[-1]
            return last_price[1]
        else:
            print("NO LTP DATA FOUND FOR SYMBOL: {}".format(symbol))
            return None

    def upstrox_analysis(self, market_Price, option_chain_upstox_socket_file):
        # analysis = {}

        # def readSocketFiles():
        #     data = {}
        #     all_files = os.listdir(self.option_chain_file_path)
        #     for file in all_files:
        #         with open(self.option_chain_file_path+file) as f:
        #             data[file.strip(".json")] = json.loads(f.read())
        #     return data

        symbol = self.OC_symbol
        analysis = {}

        time.sleep(1)
        if 1:
            
            # option_chain_upstox_socket_file = readSocketFiles()
            
            last_2_gigits = int(market_Price)%100
            if last_2_gigits >= 0 and last_2_gigits <= 49:
                last_2_gigit = '00'
            elif last_2_gigits >= 50 and last_2_gigits <= 99:
                last_2_gigit = '50'
            ATM = int(str(int(float(market_Price/100)))+last_2_gigit)
            
            strike_price_keys = option_chain_upstox_socket_file.keys()

            all_strike_prices = []
            # pick all STRIKE PRICES
            for sp in strike_price_keys:
                if 'CALL' in sp:
                    all_strike_prices.append(sp.split('_')[0])
            all_strike_prices.sort()

            index = all_strike_prices.index(str(ATM))
            below_six = all_strike_prices[max(0, index):index+1]
            above_six = all_strike_prices[index+1:index+2]
            required_strike_prices = below_six + above_six
            # index = all_strike_prices.index(str(ATM))
            # below_one = all_strike_prices[index-1]
            # above_one = all_strike_prices[index+1]
            # required_strike_prices = below_one + above_one

            strike_price_data = []
            for sp in required_strike_prices:
                strike_price_data.append({'sp': sp, 'CALL': option_chain_upstox_socket_file.get(str(sp)+'_CALL'), 'PUT': option_chain_upstox_socket_file.get(str(sp)+'_PUT')})

            call, call_lastPrice = {}, {}
            put, put_lastPrice = {}, {}
            for a in strike_price_data:
                call[a.get("CALL").get("oi")]={(a.get("CALL").get("oi"))-(a.get("CALL").get("poi")):a.get("sp")}
                put[a.get("PUT").get("oi")]={(a.get("PUT").get("oi"))-(a.get("PUT").get("poi")):a.get("sp")}
                put_lastPrice[str(a.get("sp"))] = a.get("PUT").get("ltp")
                call_lastPrice[str(a.get("sp"))] = a.get("CALL").get("ltp")

            analysis['call_min_strike_price'] = max(call_lastPrice.keys())
            analysis['put_max_strike_price'] = min(put_lastPrice.keys())
            
            sorted_call=dict(sorted(call.items(), reverse=True))
            sorted_put=dict(sorted(put.items(), reverse=True))
            # print("call",sorted_call)
            # print("put",sorted_put)
            concat_pairs = []

            for inner_dict in sorted_call.values():
                for inner_key, inner_value in inner_dict.items():
                    concatenated = f"{inner_key}_{inner_value}"
                    concat_pairs.append((abs(inner_key), concatenated))

            highest_pair = max(concat_pairs, key=lambda x: x[0])
            highest_call_changeinoi = highest_pair[1]
            concat_pairs = []

            for inner_dict in sorted_put.values():
                for inner_key, inner_value in inner_dict.items():
                    concatenated = f"{inner_key}_{inner_value}"
                    concat_pairs.append((abs(inner_key), concatenated))

            highest_pair = max(concat_pairs, key=lambda x: x[0])
            highest_put_changeinoi = highest_pair[1]

            highest_call_oi=f"{list(sorted_call.items())[0][0]}_{list(list(sorted_call.items())[0][1].values())[0]}"
            highest_put_oi=f"{list(sorted_put.items())[0][0]}_{list(list(sorted_put.items())[0][1].values())[0]}"

            highest_call_amount_strike, highest_put_amount_strike = highest_call_oi.split("_")[1], highest_put_oi.split("_")[1]
            r = [highest_call_amount_strike, highest_put_amount_strike]
            r.sort()
            analysis['range'] = r

            # print("highest_call_changeinoi = ", highest_call_changeinoi)
            # print("highest_put_changeinoi = ", highest_put_changeinoi)

            highest_call_oi_change, highest_put_oi_change = highest_call_changeinoi.split("_")[0], highest_put_changeinoi.split("_")[0]
            call_LTP = call_lastPrice.get(highest_call_changeinoi.split("_")[1])
            put_LTP = put_lastPrice.get(highest_put_changeinoi.split("_")[1])

            last_oi_prices_file = Path("./last_oi_prices.json")

            total_buy_call, total_sell_call = option_chain_upstox_socket_file.get(str(ATM)+'_CALL').get('tbq'), option_chain_upstox_socket_file.get(str(ATM)+'_CALL').get('tsq')
            total_buy_put, total_sell_put = option_chain_upstox_socket_file.get(str(ATM)+'_PUT').get('tbq'), option_chain_upstox_socket_file.get(str(ATM)+'_PUT').get('tsq')
            if last_oi_prices_file.is_file():
                with open("last_oi_prices.json", "r") as f:
                    # all_contracts = self.all_contracts_analysis(ATM)                    
                    last_oi_prices_file = f.read()
                    loaded_json = json.loads(last_oi_prices_file)
                    # d = loaded_json[-1]
                    d = loaded_json
                    last_highest_call_oi_change, last_highest_put_oi_change, last_ltp_call, last_ltp_put, last_total_buy_call, last_total_sell_call, last_total_buy_put, last_total_sell_put, last_market_direction = d.get('last_highest_call_oi_change'), d.get('last_highest_put_oi_change'), d.get('last_ltp_call'), d.get('last_ltp_put'), d.get('last_total_buy_call'), d.get('last_total_sell_call'), d.get('last_total_buy_put'), d.get('last_total_sell_put'), d.get('last_market_direction')

                    market_direction = {'CALL': 0, 'PUT': 0}
                    if highest_call_oi_change > highest_put_oi_change:
                        market_direction['CALL'] = market_direction['CALL'] + 33
                    elif highest_call_oi_change < highest_put_oi_change:
                        market_direction['PUT'] = market_direction['PUT'] + 33
                    
                    if call_LTP > put_LTP:
                        market_direction['CALL'] = market_direction['CALL'] + 33
                    elif call_LTP < put_LTP:
                        market_direction['PUT'] = market_direction['PUT'] + 33                    
                    
                    if total_buy_call > total_buy_put:
                        market_direction['CALL'] = market_direction['CALL'] + 33
                    elif total_buy_call < total_buy_put:
                        market_direction['PUT'] = market_direction['PUT'] + 33
                    
                    if market_direction.get('PUT') > market_direction.get('CALL'):
                        md = 'PUT'
                    else:
                        md = 'CALL'

                    # print(last_highest_call_oi_change)
                    # print(highest_call_oi_change)
                    # print(last_highest_put_oi_change)
                    # print(highest_put_oi_change)
                    if last_market_direction == md:
                        if int(float(last_highest_call_oi_change)) != int(float(highest_call_oi_change)) or int(float(last_highest_put_oi_change)) != int(float(highest_put_oi_change)):
                            print("Last OI updated!")

                            # with open("last_oi_prices.json", "r") as f:
                            #     data = f.read()
                            # json_data = json.loads(data)
                            # if len(json_data) > 10:
                            #     json_data = json_data[10:]
                            # json_data.append({"last_highest_call_oi_change": highest_call_oi_change, "last_highest_put_oi_change": highest_put_oi_change, "last_ltp_call": call_LTP, "last_ltp_put": put_LTP, "last_total_buy_call": total_buy_call, "last_total_sell_call": total_sell_call, "last_total_buy_put": total_buy_put, "last_total_sell_put": total_sell_put, "last_market_direction": md})
                            with open("last_oi_prices.json", "w") as f:
                                # f.write(json.dumps(json_data))
                                f.write(json.dumps({"last_highest_call_oi_change": highest_call_oi_change, "last_highest_put_oi_change": highest_put_oi_change, "last_ltp_call": call_LTP, "last_ltp_put": put_LTP, "last_total_buy_call": total_buy_call, "last_total_sell_call": total_sell_call, "last_total_buy_put": total_buy_put, "last_total_sell_put": total_sell_put, "last_market_direction": md}))
                            
                            # CHANGE IN OI INDICATOR
                            if int(float(highest_call_oi_change)) > int(float(last_highest_call_oi_change)):
                                analysis['call_oi_increase_rate'] = '{}% : {}'.format(str((int(float(highest_call_oi_change))-int(float(last_highest_call_oi_change)))/int(float(last_highest_call_oi_change))*100), str(int(float(last_highest_call_oi_change)))+', '+str(int(float(highest_call_oi_change))))
                                print(analysis['call_oi_increase_rate'])
                                if (int(float(highest_call_oi_change))-int(float(last_highest_call_oi_change)))/int(float(last_highest_call_oi_change))*100 > self.upperLimit or (int(float(highest_call_oi_change))-int(float(last_highest_call_oi_change)))/int(float(last_highest_call_oi_change))*100 < self.lowerLimit:
                                    analysis['call_oi_increased'] = True
                            else:
                                print("Call OI has decreased!")
                                analysis['call_oi_increased'] = False
                            
                            if int(float(highest_put_oi_change)) > int(float(last_highest_put_oi_change)):
                                analysis['put_oi_increase_rate'] = '{}% : {}'.format(str((int(float(highest_put_oi_change))-int(float(last_highest_put_oi_change)))/int(float(last_highest_put_oi_change))*100), str(int(float(last_highest_put_oi_change)))+', '+str(int(float(highest_put_oi_change))))
                                print("Put OI has increased!")
                                print(analysis['put_oi_increase_rate'])
                                if (int(float(highest_put_oi_change))-int(float(last_highest_put_oi_change)))/int(float(last_highest_put_oi_change))*100 > self.upperLimit or (int(float(highest_put_oi_change))-int(float(last_highest_put_oi_change)))/int(float(last_highest_put_oi_change))*100 < self.lowerLimit:
                                    analysis['put_oi_increased'] = True
                            else:
                                print("Put OI has decreased!")
                                analysis['put_oi_increased'] = False
                            
                            # LTP INDICATOR
                            if int(call_LTP) > int(last_ltp_call):
                                analysis['call_ltp_increase_rate'] = '{}% : {}'.format(str((int(call_LTP)-int(last_ltp_call))/int(last_ltp_call)*100), str(int(last_ltp_call))+', '+str(int(call_LTP)))
                                print("Call LTP has increased!")
                                print(analysis['call_ltp_increase_rate'])
                                if (int(call_LTP)-int(last_ltp_call))/int(last_ltp_call)*100 > self.upperLimit or (int(call_LTP)-int(last_ltp_call))/int(last_ltp_call)*100 < self.lowerLimit:
                                    analysis['call_ltp_increased'] = True
                            else:
                                print("Call LTP has decreased!")
                                analysis['call_ltp_increased'] = False
                            
                            if int(put_LTP) > int(last_ltp_put):
                                analysis['put_ltp_increase_rate'] = '{}% : {}'.format(str((int(put_LTP)-int(last_ltp_put))/int(last_ltp_put)*100), str(int(last_ltp_put))+', '+str(int(put_LTP)))
                                print("Put LTP has increased!")
                                print(analysis['put_ltp_increase_rate'])
                                if (int(put_LTP)-int(last_ltp_put))/int(last_ltp_put)*100 > self.upperLimit or (int(put_LTP)-int(last_ltp_put))/int(last_ltp_put)*100 < self.lowerLimit:
                                    analysis['put_ltp_increased'] = True
                            else:
                                print("Put LTP has decreased!")
                                analysis['put_ltp_increased'] = False

                            # TOTAL BUY AND TOTAL SELL QUANTITY INDICATOR
                            if int(total_buy_call) > int(last_total_buy_call):
                                analysis['call_totalBuyContracts_increase_rate'] = '{}% : {}'.format(str((int(total_buy_call)-int(last_total_buy_call))/int(last_total_buy_call)*100), str(int(last_total_buy_call))+', '+str(int(total_buy_call)))
                                print("Call TOTAL BUY CONTRACTS has increased")
                                print(analysis['call_totalBuyContracts_increase_rate'])
                                analysis['call_totalBuyContracts_increased'] = True
                            else:
                                analysis['call_totalBuyContracts_increased'] = False

                            if int(total_buy_put) > int(last_total_buy_put):
                                analysis['put_totalBuyContracts_increase_rate'] = '{}% : {}'.format(str((int(total_buy_put)-int(last_total_buy_put))/int(last_total_buy_put)*100), str(int(last_total_buy_put))+', '+str(int(total_buy_put)))
                                print("Put TOTAL BUY CONTRACTS has increased")
                                print(analysis['put_totalBuyContracts_increase_rate'])
                                analysis['put_totalBuyContracts_increased'] = True
                            else:
                                analysis['put_totalBuyContracts_increased'] = False

                            if int(total_sell_call) > int(last_total_sell_call):
                                analysis['call_totalSellContracts_increase_rate'] = '{}% : {}'.format(str((int(total_sell_call)-int(last_total_sell_call))/int(last_total_sell_call)*100), str(int(last_total_sell_call))+', '+str(int(total_sell_call)))
                                print("Call TOTAL SELL CONTRACTS has increased")
                                print(analysis['call_totalSellContracts_increase_rate'])
                                analysis['call_totalSellContracts_increased'] = True
                            else:
                                analysis['call_totalSellContracts_increased'] = False

                            if int(total_buy_put) > int(last_total_buy_put):
                                analysis['put_totalBuyContracts_increase_rate'] = '{}% : {}'.format(str((int(total_buy_put)-int(last_total_buy_put))/int(last_total_buy_put)*100), str(int(last_total_buy_put))+', '+str(int(total_buy_put)))
                                print("Put TOTAL BUY CONTRACTS has increased")
                                print(analysis['put_totalBuyContracts_increase_rate'])
                                analysis['put_totalBuyContracts_increased'] = True
                            else:
                                analysis['put_totalBuyContracts_increased'] = False

                        else:
                            print("Change in OI not updated! No new data to analyze.")
                    else:
                        print("MARKET DIRECTION WAS : {} earlier and NOW IT IS: {}".format(last_market_direction, md))
                        # with open("last_oi_prices.json", "r") as f:
                        #     data = f.read()
                        # json_data = json.loads(data)
                        # if len(json_data) > 10:
                        #     json_data = json_data[10:]
                        # json_data.append({"last_highest_call_oi_change": highest_call_oi_change, "last_highest_put_oi_change": highest_put_oi_change, "last_ltp_call": call_LTP, "last_ltp_put": put_LTP, "last_total_buy_call": total_buy_call, "last_total_sell_call": total_sell_call, "last_total_buy_put": total_buy_put, "last_total_sell_put": total_sell_put, "last_market_direction": md})
                        with open("last_oi_prices.json", "w") as f:
                            # f.write(json.dumps(json_data))
                            f.write(json.dumps({"last_highest_call_oi_change": highest_call_oi_change, "last_highest_put_oi_change": highest_put_oi_change, "last_ltp_call": call_LTP, "last_ltp_put": put_LTP, "last_total_buy_call": total_buy_call, "last_total_sell_call": total_sell_call, "last_total_buy_put": total_buy_put, "last_total_sell_put": total_sell_put, "last_market_direction": md}))
            else:
                # all_contracts = self.all_contracts_analysis(ATM)
                total_buy_call, total_sell_call = option_chain_upstox_socket_file.get(str(ATM)+'_CALL').get('tbq'), option_chain_upstox_socket_file.get(str(ATM)+'_CALL').get('tsq')
                total_buy_put, total_sell_put = option_chain_upstox_socket_file.get(str(ATM)+'_PUT').get('tbq'), option_chain_upstox_socket_file.get(str(ATM)+'_PUT').get('tsq')
                print("Running first time, NO DATA FOR ANALYSIS..")
                market_direction = {'CALL': 0, 'PUT': 0}
                if highest_call_oi_change > highest_put_oi_change:
                    market_direction['CALL'] = market_direction['CALL'] + 33
                elif highest_call_oi_change < highest_put_oi_change:
                    market_direction['PUT'] = market_direction['PUT'] + 33
                
                if call_LTP > put_LTP:
                    market_direction['CALL'] = market_direction['CALL'] + 33
                elif call_LTP < put_LTP:
                    market_direction['PUT'] = market_direction['PUT'] + 33
                
                if total_buy_call > total_buy_put:
                    market_direction['CALL'] = market_direction['CALL'] + 33
                elif total_buy_call < total_buy_put:
                    market_direction['PUT'] = market_direction['PUT'] + 33
                
                if market_direction.get('PUT') > market_direction.get('CALL'):
                    md = 'PUT'
                else:
                    md = 'CALL'

                with open("last_oi_prices.json", "w") as f:
                    # f.write(json.dumps([{"last_highest_call_oi_change": highest_call_oi_change, "last_highest_put_oi_change": highest_put_oi_change, "last_ltp_call": call_LTP, "last_ltp_put": put_LTP, "last_total_buy_call": total_buy_call, "last_total_sell_call": total_sell_call, "last_total_buy_put": total_buy_put, "last_total_sell_put": total_sell_put, "last_market_direction": md}]))
                    f.write(json.dumps({"last_highest_call_oi_change": highest_call_oi_change, "last_highest_put_oi_change": highest_put_oi_change, "last_ltp_call": call_LTP, "last_ltp_put": put_LTP, "last_total_buy_call": total_buy_call, "last_total_sell_call": total_sell_call, "last_total_buy_put": total_buy_put, "last_total_sell_put": total_sell_put, "last_market_direction": md}))
            analysis['put_totalBuyContracts'] = total_buy_put
            analysis['put_totalSellContracts'] = total_sell_put
            analysis['call_totalBuyContracts'] = total_buy_call
            analysis['call_totalSellContracts'] = total_sell_call
            analysis['ATM'] = ATM
            analysis['ltp'] = {'call': int(call_LTP), 'put': int(put_LTP)}
            return analysis

    def all_contracts_analysis(self, sp):
        global RETRY_COUNT
        global symbol
        try:
            cookies = self.getCookies()
            nsit = nseappid = bm_sz = bm_sv = _abck = ak_bmsc = ""
            
            if 'nsit=' in cookies:
                nsit = "nsit="+cookies.split('nsit=')[1].split(';')[0]+';'
            if 'nseappid=' in cookies:
                nseappid = 'nseappid='+cookies.split('nseappid=')[1].split(';')[0]+';'
            if 'bm_sz=' in cookies:
                bm_sz = 'bm_sz='+cookies.split('bm_sz=')[1].split(';')[0]+';'
            if 'bm_sv=' in cookies:
                bm_sv = 'bm_sv='+cookies.split('bm_sv=')[1].split(';')[0]+';'
            if '_abck=' in cookies:
                _abck = '_abck='+cookies.split('_abck=')[1].split(';')[0]+';'
            if 'ak_bmsc=' in cookies:
                ak_bmsc = 'ak_bmsc='+cookies.split('ak_bmsc=')[1].split(';')[0]+';'
            headers = {
                "accept": "*/*",
                "accept-language": "en-GB,en-US;q=0.9,en;q=0.8,hi;q=0.7",
                "sec-ch-ua": "\"Google Chrome\";v=\"123\", \"Not:A-Brand\";v=\"8\", \"Chromium\";v=\"123\"",
                "sec-ch-ua-mobile": "?0",
                "sec-ch-ua-platform": "\"Linux\"",
                "sec-fetch-dest": "empty",
                "sec-fetch-mode": "cors",
                "sec-fetch-site": "same-origin",
                "cookie": "{} {} AKA_A2=A; {} {} defaultLang=en; {} {}".format(nsit, nseappid, bm_sz, bm_sv, _abck, ak_bmsc),
                "Referer": "https://www.nseindia.com/get-quotes/derivatives?symbol=NIFTY",
                "Referrer-Policy": "strict-origin-when-cross-origin",
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.106 Safari/537.36 OPR/38.0.2220.41"
            }
            url = "https://www.nseindia.com/api/quote-derivative?symbol="+self.OC_symbol
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                json_result = json.loads(response.text).get('stocks')
                response = {}
                for data in json_result:
                    strikePrice = data.get("metadata").get("strikePrice")
                    optionType = data.get("metadata").get("optionType")
                    if strikePrice == sp:
                        response[optionType.lower()] = [int(data.get("marketDeptOrderBook").get("totalBuyQuantity")), int(data.get("marketDeptOrderBook").get("totalSellQuantity"))]
                return response
            else:
                print("Error: Failed to fetch data from {}. Status code: {}".format(url, response.status_code))
                if RETRY_COUNT >= 0:
                    RETRY_COUNT = RETRY_COUNT - 1
                    import time
                    time.sleep(10)
                    self.all_contracts_analysis(sp)
                return (None, None)
        except requests.RequestException as e:
            print("Error: Failed to fetch data from ALL CONTRACTS ANALYSIs. Exception: {}".format(e))
            return (None, None)

    def getltp(self,strike_price=None,call_put=None):
        # time.sleep(1)
        if strike_price and call_put: 
            instrument_key=self.create_symbol_to_instrument_mapping(strike_price,call_put)
            instrument=instrument_key.split('|')[0]+'|'+self.symbol1
        else:
            instrument_key=self.instrument_key
            instrument=self.instrument_key
        # print(instrument_key)

        url = f'{self.base_url}/market-quote/ltp?instrument_key={instrument_key}'
        headers = {
            'Authorization': f'Bearer '+self.authorization,
            'Accept': 'application/json'
        }
        response = requests.get(url, headers=headers)
        instrument=instrument.replace('|',':')
        # print(instrument)
        if response.status_code == 200:
            # print(response.json())
            return response.json().get('data').get(instrument).get('last_price')
        else:
            print(f"Error fetching option chain: {response.status_code}, {response.text}")
            return None

    def create_symbol_to_instrument_mapping(self,strike_price,call_put):
        url = "https://assets.upstox.com/market-quote/instruments/exchange/NSE.csv.gz"
        input_date = datetime.strptime(self.expiry_date, '%Y-%m-%d')
        year = input_date.year % 100 
        month = input_date.month
        day = input_date.day
        formatted_date = "{:02d}{:01d}{:02d}".format(year, month, day)
        if call_put == "PUT":
            option = 'PE'
        elif call_put == "CALL":
            option = 'CE'
        self.symbol1 = self.OC_symbol+str(formatted_date)+str(strike_price)+option
        # print(self.symbol1)
        # symbol_to_instrument = {}
        # response = requests.get(url, stream=True)
        # if response.status_code == 200:
        #     with gzip.GzipFile(fileobj=BytesIO(response.content)) as f:
        #         reader = csv.DictReader(codecs.iterdecode(f, 'utf-8'))
        #         for row in reader:
        #             if row['name'] == symbol1:
        #                 symbol_to_instrument[row['name']] = row['instrument_key']
        #                 break
        # return symbol_to_instrument.get(symbol1)
        script_dir = os.path.dirname(os.path.abspath(__file__))
        # Path to the .csv file in the same directory as the script
        file_path = os.path.join(script_dir, "NSE.csv")
        with open(file_path, mode='r', encoding='utf-8') as file:
            rows = file.read().split("\n")
            for row in rows:
                if self.symbol1 in row:
                    items = row.split(",")
                    # print(items[0].strip('"'))
                    break
        return items[0].strip('"')