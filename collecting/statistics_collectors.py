from bots.bots import *
import multiprocessing
from json import dumps
from configs.config import host_redis, port_redis
import redis
from time import sleep

def setMa(analyst_bot, redis_con):
    while True:
        analyst_bot.getData()
        analyst_bot.calcMa()
        redis_con.set('ma', analyst_bot.listValueMa[-1])

def setEma(analyst_bot, redis_con):
    while True:
        analyst_bot.getData()
        analyst_bot.calcEMA()
        redis_con.set('ema', analyst_bot.listValueEma[-1])
    

def setLevels(analyst_bot, redis_con):
    while True:
        analyst_bot.getData()
        levels = analyst_bot.identify_support_resistance_levels()
        redis_con.set('levels', dumps(levels))

def setLastValue(analyst_bot, redis_con):
    while True:
        analyst_bot.getData()
        redis_con.set('last_value', analyst_bot.currentValue)
    sleep(1)




def setMainMetric(api_key, api_secret, symbol, interval, proxy):
    redis_con = redis.Redis(host=host_redis, port=port_redis, db=0)
    analyst_bot = botAnalyst(api_key, api_secret, symbol, interval, proxy)

    ma_process = multiprocessing.Process(target=setMa, args=[analyst_bot, redis_con])
    ema_process = multiprocessing.Process(target=setEma, args=[analyst_bot, redis_con])
    levels_process = multiprocessing.Process(target=setLevels, args=[analyst_bot, redis_con])
    last_value_process = multiprocessing.Process(target=setLastValue, args=[analyst_bot, redis_con])

    ma_process.start()
    ema_process.start()
    levels_process.start()
    last_value_process.start()





