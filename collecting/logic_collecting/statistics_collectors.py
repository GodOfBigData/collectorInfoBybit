from bots.bots import *
import multiprocessing
from json import dumps
from configs.config import host_redis, port_redis
import redis
from time import sleep
from collecting.methods_collecting.method_statistics import setLevels, setLastValue, setSuperioritySell, setSuperiorityBuy

def setMainMetric(api_key, api_secret, mode, symbol, interval, proxy):
    redis_con = redis.Redis(host=host_redis, port=port_redis, db=0)
    analyst_bot = botAnalyst(api_key, api_secret, mode, symbol, interval, proxy)

    levels_process = multiprocessing.Process(target=setLevels, args=[analyst_bot, redis_con])
    last_value_process = multiprocessing.Process(target=setLastValue, args=[analyst_bot, redis_con])
    superiority_sell_process = multiprocessing.Process(target=setSuperioritySell, args=[analyst_bot, redis_con])
    superiority_buy_process = multiprocessing.Process(target=setSuperiorityBuy, args=[analyst_bot, redis_con])


    levels_process.start()
    last_value_process.start()
    superiority_sell_process.start()
    superiority_buy_process.start()





