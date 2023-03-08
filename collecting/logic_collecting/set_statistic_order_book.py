from bots.bots import *
import multiprocessing
from json import dumps
from configs.config import host_redis, port_redis
import redis
from time import sleep
from collecting.methods_collecting.method_statistics import setLastValue, setOrdersBook


def setMainMetric(api_key, api_secret, symbol, interval, proxy):
    redis_con = redis.Redis(host=host_redis, port=port_redis, db=0)
    analyst_bot = botAnalyst(api_key, api_secret, symbol, interval, proxy)

    last_value_process = multiprocessing.Process(target=setLastValue, args=[analyst_bot, redis_con])
    orders_book_process = multiprocessing.Process(target=setOrdersBook, args=[analyst_bot, redis_con])

    last_value_process.start()
    orders_book_process.start()





