import calendar
import datetime
import hashlib
import hmac
import logging
import math
from urllib.parse import quote_plus
import urllib3
from json import loads, dumps
from bots.settings import *
import requests
from math import floor
import pandas as pd
from time import sleep
import time
import numpy as np

log_debug = logging.getLogger('bots_debug')
log_info = logging.getLogger('bots_info')
log_error = logging.getLogger('bots_error')

file_handler_debug = logging.FileHandler(filename='logs/bots.log')
file_handler_debug.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s', datefmt='%d-%m-%Y %H:%M'))
file_handler_debug.setLevel(logging.DEBUG)
log_debug.addHandler(file_handler_debug)
log_debug.setLevel(logging.DEBUG)

file_handler_info = logging.FileHandler(filename='logs/bots.log')
file_handler_info.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s', datefmt='%d-%m-%Y %H:%M'))
file_handler_info.setLevel(logging.INFO)
log_info.addHandler(file_handler_info)
log_info.setLevel(logging.INFO)

file_handler_error = logging.FileHandler(filename='logs/bots.log')
file_handler_error.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s', datefmt='%d-%m-%Y %H:%M'))
file_handler_error.setLevel(logging.ERROR)
log_error.addHandler(file_handler_error)
log_error.setLevel(logging.ERROR)


class BotBybit:

    def __init__(self, api_key: str, api_secret: str, mode: str):
        """
        Initializing the parent bot
        :param api_key: api account key
        :type api_key: str
        :param api_secret: api account secret key
        :type api_secret: str
        :param mode: mode work (testnet or Mainenet)
        :type mode: str
        :return: None
        """
        self.api_key = api_key
        self.api_secret = api_secret
        self.mode = mode

    def go_command(self, method: str, url: str, secret_key: str, params: dict, proxies: dict):
        """
        Function creating a request
        :param method: GET or POST
        :type method: str
        :param url: url bybit
        :type url: str
        :param secret_key: client's secret key
        :type secret_key: str
        :param params: dict with data for request
        :type params: str
        :param proxies: dict with proxy
        :type proxies: dict
        :return: dict with data
        """

        # Create the param str
        param_str = ""
        for key in sorted(params.keys()):
            v = params[key]
            if isinstance(params[key], bool):
                if params[key]:
                    v = "true"
                else:
                    v = "false"
            param_str += f"{key}={v}&"
        param_str = param_str[:-1]

        # Generate the signature
        hash = hmac.new(bytes(secret_key, "utf-8"), param_str.encode("utf-8"),
                        hashlib.sha256)
        signature = hash.hexdigest()
        sign_real = {
            "sign": signature
        }
        # Prepare params in the query string format
        # quote_plus helps quote rare characters like "/" and "+"; this must be
        # applied after the signature generation.
        param_str = quote_plus(param_str, safe="=&")
        full_param_str = f"{param_str}&sign={sign_real['sign']}"
        # Request information
        if "spot" in url or method == "GET":
            headers = {"Content-Type": "application/x-www-form-urlencoded"}
            body = None
        else:
            headers = {"Content-Type": "application/json"}
            body = dict(params, **sign_real)

        urllib3.disable_warnings()
        s = requests.session()
        s.keep_alive = False

        # Send the request(s)

        if "spot" in url:
            # Send a request to the spot API
            response = requests.requeimportst(method, f"{url}?{full_param_str}",
                                        headers=headers, verify=False)
        else:
            # Send a request to the futures API
            if method == "POST":
                response = requests.request(method, url, data=dumps(body),
                                            headers=headers, verify=False, proxies=proxies)
            else:  # GET
                response = requests.request(method, f"{url}?{full_param_str}",
                                            headers=headers, verify=False, proxies=proxies)

        return loads(response.text)

    def get_timestamp(self, proxy):
        """
        Get timestamp function
        :return: time
        """
        resp = requests.request('GET', url=f'https://{self.mode}.bybit.com/v2/public/time', proxies={'http': proxy})
        server_time = int(float(loads(resp.text)['time_now']) * 1000)
        return server_time


class botAnalyst(BotBybit):

    def __init__(self, api_key, api_secret, mode, symbol, interval, proxy):
        super().__init__(api_key, api_secret, mode)
        self.symbol = symbol
        self.interval = interval
        self.dataFrame = None
        self.listValueMa = list()
        self.listValueEma = list()
        self.proxy = proxy
        self.currentValue = 0
        self.sizeWindow = 5

    def getData(self):
        """
        Take max count candles = 200
        interval per minutes
        """
        timestamp = floor((self.get_timestamp(self.proxy) - self.interval * 60000 * 200) / 1000)
        url = f"https://{self.mode}.bybit.com/public/linear/kline?symbol={self.symbol}&interval={self.interval}&limit=200&from={timestamp}"
        response = requests.get(url=url)
        data_json = loads(response.text)
        self.dataFrame = pd.DataFrame.from_dict(data_json["result"])
        self.currentValue = self.dataFrame["close"].iloc[-1]

    def calcMa(self):
        self.listValueMa = list(self.dataFrame["close"].rolling(window=9).mean())

    def calcEMA(self):
        self.listValueEma = list(self.dataFrame["close"].ewm(span=5, adjust=False).mean())

    def getCurrentMaEma(self):
        self.runCalcMetrics()
        return self.listValueMa[-1], self.listValueEma[-1]


    def runCalcMetrics(self):
        self.getData()
        self.calcMa()
        self.calcEMA()

    # определение бычьего фрактала  
    def is_support(self, i):  
        cond1 = self.dataFrame['low'][i] < self.dataFrame['low'][i-1]   
        cond2 = self.dataFrame['low'][i] < self.dataFrame['low'][i+1]   
        cond3 = self.dataFrame['low'][i+1] < self.dataFrame['low'][i+2]   
        cond4 = self.dataFrame['low'][i-1] < self.dataFrame['low'][i-2]  
        return (cond1 and cond2 and cond3 and cond4) 

    # определение медвежьего фрактал 
    def is_resistance(self, i):  
        cond1 = self.dataFrame['high'][i] > self.dataFrame['high'][i-1]   
        cond2 = self.dataFrame['high'][i] > self.dataFrame['high'][i+1]   
        cond3 = self.dataFrame['high'][i+1] > self.dataFrame['high'][i+2]   
        cond4 = self.dataFrame['high'][i-1] > self.dataFrame['high'][i-2]  
        return (cond1 and cond2 and cond3 and cond4)

    def is_far_from_level(self, value, levels):    
        ave =  np.mean(self.dataFrame['high'] - self.dataFrame['low'])    
        return np.sum([abs(value - level) < ave for _,level in levels]) == 0

    def identify_support_resistance_levels(self):
        levels = []
        for i in range(2, self.dataFrame.shape[0] - 2):  
            if self.is_support(i):    
                low = self.dataFrame['low'][i]    
                if self.is_far_from_level(low, levels):
                    levels.append((i, low))
            elif self.is_resistance(i):    
                high = self.dataFrame['high'][i]    
                if self.is_far_from_level(high, levels):
                    levels.append((i, high))
        return levels

    def getOrderBook(self):
        url = f"https://{self.mode}.bybit.com/v2/public/orderBook/L2?symbol={self.symbol}"
        response = requests.get(url=url)
        array_data = loads(response.text)["result"]
        list_orders_buy = list()
        list_orders_sell = list()
        for dict_info in array_data:
            if dict_info["side"] == "Buy":
                list_orders_buy.append(dict_info)
            else:
                list_orders_sell.append(dict_info)
        return list_orders_buy, list_orders_sell

        


class analystOnhcainMetrics:

    def __init__(self, key_coinMarket):
        self.globalMetrics = dict()
        self.headers = {
            'Accepts': 'application/json',
            'X-CMC_PRO_API_KEY': key_coinMarket,
        }
        self.url = "https://pro-api.coinmarketcap.com/v1/global-metrics/quotes/latest"

    def getGlobalMetrics(self):
        response = loads(requests.get(self.url, headers=self.headers).text)
        self.globalMetrics = response["data"]
        return self.globalMetrics

    def getInformationEth(self):
        response = loads(requests.get(self.url, headers=self.headers).text)
        globalMetrics = response["data"]
        return globalMetrics["eth_dominance"], globalMetrics["eth_dominance_yesterday"], globalMetrics["last_updated"]
