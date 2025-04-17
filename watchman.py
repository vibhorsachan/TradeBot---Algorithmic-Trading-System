from google.protobuf.json_format import MessageToDict
from process_Engine import MarketDataAPI
from angelone_OPs import AngelBrokingAPI
import MarketDataFeed_pb2_UPSTOX as pb
from proxy import SetupConnection
from pathlib import Path
import upstox_client
import websockets
import traceback
import requests
import asyncio
import time
import uuid
import json
import ssl



async def get_market_data_feed_authorize(api_version, configuration):
    """Get authorization for market data feed."""
    api_instance = upstox_client.WebsocketApi(
        upstox_client.ApiClient(configuration))
    api_response = api_instance.get_market_data_feed_authorize(api_version)
    return api_response

async def decode_protobuf(buffer):
    """Decode protobuf message."""
    feed_response = pb.FeedResponse()
    feed_response.ParseFromString(buffer)
    return feed_response


class WATCHFORTRADE:

    def __init__(self) -> None:
        # TRADING SYMBOL
        self.trading_symbol = 'NIFTY09MAY24'
        self.expiry = '09-05-2024'
        self.ATM = None
        symbol = 'NIFTY 50'
        # symbol = 'NIFTY BANK'
        # self.instrument_key='NSE_INDEX|Nifty Bank'
        #symbol = 'NIFTY FINANCIAL SERVICES'
        #symbol = 'NIFTY MID SELECT'
        self.instrument_key='NSE_INDEX|Nifty 50'
        self.expiry_date = '2024-05-16'

        # ANGEL ONE CREDS
        self.base_url = "apiconnect.angelbroking.com"
        self.client_code = "S53514013"
        self.password = "8782"
        self.totp = "593545"
        
        # AUTH
        self.authorization = 'eyJ0eXAiOiJKV1QiLCJrZXlfaWQiOiJza192MS4wIiwiYWxnIjoiSFMyNTYifQ.eyJzdWIiOiI1NkEySEciLCJqdGkiOiI2NjQ0MmU3MmQ2YWU4ZDI0ZGNjMmEzZjEiLCJpc011bHRpQ2xpZW50IjpmYWxzZSwiaWF0IjoxNzE1NzQ0MzcwLCJpc3MiOiJ1ZGFwaS1nYXRld2F5LXNlcnZpY2UiLCJleHAiOjE3MTU4MTA0MDB9.QPjrOW_W6c-SC-vIbx2Q5wpky1T9ht2ZU5qo31xnmZU'
        
        self.NSEAPI_Obj = MarketDataAPI(symbol, self.authorization, self.instrument_key, self.expiry_date)
        self.vpn=SetupConnection('trading')
        self.LOT_SIZE = 25

        self.option_chain_file_path = "./upstox_option_chain_socket/"
        self.oi_data_map = {}
        self.instrument_array = []
        # angel_smart_api = AngelBrokingAPI(self.base_url, self.client_code, self.password, self.totp, '')
        # angel_smart_api.login()
        # exit()

    async def writeLogs(self, data):
        try:
            with open("result.text", "a") as f:
                f.write(data)
        except Exception as e:
            print(str(e))

    async def monitor(self):
        await asyncio.sleep(2)
        """Fetch market data using WebSocket and print it."""

        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE

        configuration = upstox_client.Configuration()
        api_version = '2.0'
        configuration.access_token = self.authorization

        response = await get_market_data_feed_authorize(api_version, configuration)

        instrument_key_call = self.NSEAPI_Obj.create_symbol_to_instrument_mapping(self.ATM, 'CALL')
        instrument_key_put = self.NSEAPI_Obj.create_symbol_to_instrument_mapping(self.ATM, 'PUT')

        async with websockets.connect(response.data.authorized_redirect_uri, ssl=ssl_context) as websocket:
            # print('Connection established')

            self.instrument_array.append(self.instrument_key)
            if not instrument_key_call in self.instrument_array:
                self.instrument_array.append(instrument_key_call)
            if not instrument_key_put in self.instrument_array:
                self.instrument_array.append(instrument_key_put)
                
            await asyncio.sleep(1)
            data = {
                "guid": str(uuid.uuid4()),
                "method": "sub",
                "data": {
                    "mode": "full",
                    "instrumentKeys": self.instrument_array
                }
            }

            binary_data = json.dumps(data).encode('utf-8')
            await websocket.send(binary_data)

            TRADE_LOCKED = False
            trade_price = 0
            option_chain_data = {}
            LTP, price, last_price = None, None, 0
            last_tbq = 1
            last_tsq = 1
            last_opposite_tbq = 1
            last_opposite_tsq = 1
            while True:
                tbq, tsq, opposite_tbq, opposite_tsq = None, None, None, None
                message = await websocket.recv()
                decoded_data = await decode_protobuf(message)

                data_dict = MessageToDict(decoded_data)
                # print(data_dict)
                if data_dict.get('feeds').get(self.instrument_key):
                    price = data_dict["feeds"][self.instrument_key]["ff"]["indexFF"]["ltpc"]["ltp"]
                else:
                    continue
                if not data_dict.get('feeds').get(instrument_key_call) or not data_dict.get('feeds').get(instrument_key_put):
                    continue

                if data_dict.get('feeds').get(instrument_key_call):
                    tbq = data_dict["feeds"][instrument_key_call]["ff"]["marketFF"]["eFeedDetails"]["tbq"]
                    tsq = data_dict["feeds"][instrument_key_call]["ff"]["marketFF"]["eFeedDetails"]["tsq"]
                if data_dict.get('feeds').get(instrument_key_put):
                    opposite_tbq = data_dict["feeds"][instrument_key_put]["ff"]["marketFF"]["eFeedDetails"]["tbq"]
                    opposite_tsq = data_dict["feeds"][instrument_key_put]["ff"]["marketFF"]["eFeedDetails"]["tsq"]
                

                for key in data_dict['feeds']:
                    if key == self.instrument_key:
                        continue
                    option_chain_data[str(self.oi_data_map.get(key).get('sp'))+'_'+self.oi_data_map.get(key).get('option')] = {'oi':data_dict.get('feeds').get(key).get('ff').get('marketFF').get('eFeedDetails').get('oi'),'poi':data_dict.get('feeds').get(key).get('ff').get('marketFF').get('eFeedDetails').get('poi'),'tbq':data_dict.get('feeds').get(key).get('ff').get('marketFF').get('eFeedDetails').get('tbq'),'tsq':data_dict.get('feeds').get(key).get('ff').get('marketFF').get('eFeedDetails').get('tsq'),'ltp':data_dict.get('feeds').get(key).get('ff').get('marketFF').get('ltpc').get('ltp'), "sp": self.oi_data_map.get(key).get('sp'), "option": self.oi_data_map.get(key).get('option')
                        }

                PROBABILITY = {'call': 0, 'put': 0}
                # print(count)
                print('^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^')
                # print(self.vpn.getCurrentIP())
                # self.vpn.connect(premium=True)
                # print(self.vpn.getCurrentIP())
                try:
                    analysis = self.NSEAPI_Obj.upstrox_analysis(price, option_chain_data)
                    # self.vpn.disconnect()

                    # print("CURRENT MARKET PRICE: " + str(price))
                    # print("RANGE WILL LIE BETWEEN " + str(analysis.get('range')))

                    # # OI Indicator [33%]
                    # WEIGHTAGE = 33
                    # if analysis.get('call_oi_increased') and analysis.get('call_oi_increased') == True and analysis.get('put_oi_increased') and analysis.get('put_oi_increased') == True:
                    #     print("#### PUT AND CALL BOTH OI INCREASED ####")
                    # elif analysis.get('call_oi_increased'):
                    #     print("$$ CALL OI INCREASED $$")
                    #     PROBABILITY['call'] = PROBABILITY['call'] + WEIGHTAGE
                    # elif analysis.get('put_oi_increased'):
                    #     print("$$ PUT OI INCREASED $$")
                    #     PROBABILITY['put'] = PROBABILITY['put'] + WEIGHTAGE

                    # # LTP Indicator [33%]
                    # WEIGHTAGE = 33
                    # if analysis.get('call_ltp_increased') and analysis.get('call_ltp_increased') == True and analysis.get('put_ltp_increased') and analysis.get('put_ltp_increased') == True:
                    #     print("**** PUT AND CALL BOTH LTP INCREASED ****")
                    # elif analysis.get('call_ltp_increased'):
                    #     print("$$ CALL LTP INCREASED $$")
                    #     PROBABILITY['call'] = PROBABILITY['call'] + WEIGHTAGE
                    # elif analysis.get('put_ltp_increased'):
                    #     print("$$ PUT LTP INCREASED $$")
                    #     PROBABILITY['put'] = PROBABILITY['put'] + WEIGHTAGE
                    
                    # # totalBuyContracts Indicator [33%]
                    # WEIGHTAGE = 33
                    # if analysis.get('call_totalBuyContracts_increased') and analysis.get('call_totalBuyContracts_increased') == True and analysis.get('put_totalBuyContracts_increased') and analysis.get('put_totalBuyContracts_increased') == True:
                    #     print("**** PUT AND CALL BOTH totalBuyContracts INCREASED BY MORE THAN 3L ****")
                    # elif analysis.get('call_totalBuyContracts_increased'):
                    #     print("$$ CALL totalBuyContracts INCREASED $$")
                    #     PROBABILITY['call'] = PROBABILITY['call'] + WEIGHTAGE
                    # elif analysis.get('put_totalBuyContracts_increased'):
                    #     print("$$ PUT totalBuyContracts INCREASED $$")
                    #     PROBABILITY['put'] = PROBABILITY['put'] + WEIGHTAGE
                    
                    # print("Probability to buy CALL OPTION: {}".format(str(PROBABILITY.get('call'))))
                    # print("Probability to buy PUT OPTION: {}".format(str(PROBABILITY.get('put'))))

                    # strike_price, call_put = '', ''
                    # if PROBABILITY.get('call') > 50:
                    #     print("BUY CALL OPTION AT ATM SP: {}".format(str(analysis.get('ATM'))))
                    #     strike_price, call_put = analysis.get('ATM'), 'CALL'
                    # elif PROBABILITY.get('put') > 50:
                    #     print("BUY PUT OPTION AT ATM SP: {}".format(str(analysis.get('ATM'))))
                    #     strike_price, call_put = analysis.get('ATM'), 'PUT'
                    # else:
                    #     print("######## UNABLE TO DETERMINE TRADE NO CONDITIONS MATCHING ########")

                    await self.writeLogs("-----------------------------------"+"\n")
                    await self.writeLogs("CURRENt TIME : " + str(time.strftime("%H:%M:%S"))+"\n")
                    await self.writeLogs("-----------------------------------"+"\n\n")
                    await self.writeLogs(json.dumps(analysis)+"\n")
                    await self.writeLogs("MARKET PRICE : " + str(price)+"\n")
                    await self.writeLogs("ATM: {}" + str(self.ATM)+"\n")
                    await self.writeLogs("CALL TOTAL BUY QUANT.: {}".format(tbq)+"\n")
                    await self.writeLogs("CALL TOTAL SELL QUANT.: {}".format(tsq)+"\n")
                    await self.writeLogs("PUT TOTAL BUY QUANT.: {}".format(opposite_tbq)+"\n")
                    await self.writeLogs("PUT TOTAL SELL QUANT.: {}".format(opposite_tsq)+"\n")
                    await self.writeLogs("CALL TOTAL BUY QUANT. CHANGES: {}%".format(str((tbq-int(last_tbq))/int(last_tbq)*100))+"\n")
                    await self.writeLogs("CALL TOTAL SELL QUANT. CHANGES: {}%".format(str((tsq-int(last_tsq))/int(last_tsq)*100))+"\n")
                    await self.writeLogs("PUT TOTAL BUY QUANT. CHANGES: {}%".format(str((opposite_tbq-int(last_opposite_tbq))/int(last_opposite_tbq)*100))+"\n")
                    await self.writeLogs("PUT TOTAL SELL QUANT. CHANGES: {}%".format(str((opposite_tsq-int(last_opposite_tsq))/int(last_opposite_tsq)*100))+"\n")
                    await self.writeLogs("-----------------------------------"+"\n")
                    await self.writeLogs("-----------------------------------"+"\n")

                    print("-----------------------------------")
                    print("CURRENt TIME : " + str(time.strftime("%H:%M")))
                    print("-----------------------------------"+"\n\n")
                    print(json.dumps(analysis))
                    print("MARKET PRICE : " + str(price))
                    print("ATM: {}" + str(self.ATM))
                    print("CALL TOTAL BUY QUANT.: {}".format(tbq))
                    print("CALL TOTAL SELL QUANT.: {}".format(tsq))
                    print("PUT TOTAL BUY QUANT.: {}".format(opposite_tbq))
                    print("PUT TOTAL SELL QUANT.: {}".format(opposite_tsq))
                    print("CALL TOTAL BUY QUANT. CHANGES: {}%".format(str((tbq-int(last_tbq))/int(last_tbq)*100)))
                    print("CALL TOTAL SELL QUANT. CHANGES: {}%".format(str((tsq-int(last_tsq))/int(last_tsq)*100)))
                    print("PUT TOTAL BUY QUANT. CHANGES: {}%".format(str((opposite_tbq-int(last_opposite_tbq))/int(last_opposite_tbq)*100)))
                    print("PUT TOTAL SELL QUANT. CHANGES: {}%".format(str((opposite_tsq-int(last_opposite_tsq))/int(last_opposite_tsq)*100)))
                    print("-----------------------------------")
                    print("-----------------------------------")

                    last_tbq = tbq
                    last_tsq = tsq
                    last_opposite_tbq = opposite_tbq
                    last_opposite_tsq = opposite_tsq
                        
                except Exception:
                    print(traceback.format_exc())

    
    def upstrox_option_chain(self, market_Price=None):
        if not market_Price:
            market_Price=self.NSEAPI_Obj.getltp()
        
        last_2_gigits = int(market_Price)%100
        if last_2_gigits >= 0 and last_2_gigits <= 49:
            last_2_gigit = '00'
        elif last_2_gigits >= 50 and last_2_gigits <= 99:
            last_2_gigit = '50'
        self.ATM = int(str(int(float(market_Price/100)))+last_2_gigit)

        # print(ATM)
        given_value = self.ATM
        difference = 50
        num_values = 2
        positive_values = [given_value + (i * difference) for i in range(1, num_values + 1)]
        negative_values = [given_value - (i * difference) for i in range(1, num_values + 1)]
        all_values = positive_values + negative_values+[given_value]
        sorted_values = sorted(all_values)
        for value in sorted_values:
            self.instrument_array.append(self.NSEAPI_Obj.create_symbol_to_instrument_mapping(value,"CALL"))
            self.instrument_array.append(self.NSEAPI_Obj.create_symbol_to_instrument_mapping(value,"PUT"))
            self.oi_data_map[self.NSEAPI_Obj.create_symbol_to_instrument_mapping(value,"CALL")]={"option": "CALL", "sp": value}
            self.oi_data_map[self.NSEAPI_Obj.create_symbol_to_instrument_mapping(value,"PUT")]={"option": "PUT", "sp": value}

async def __start__():
    try:
        W = WATCHFORTRADE()
        # try:
        W.upstrox_option_chain()
        await W.monitor()
        # await asyncio.gather(W.keep_option_chain_live(), W.monitor())
    except:
        await __start__()

asyncio.run(__start__())