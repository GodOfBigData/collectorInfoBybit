from json import dumps
from collecting.additions.main_additions import infinity, fault_tolerance

@infinity
@fault_tolerance
def setMa(analyst_bot, redis_con):
    while True:
        analyst_bot.getData()
        analyst_bot.calcMa()
        redis_con.set('ma', analyst_bot.listValueMa[-1])

@infinity
@fault_tolerance
def setEma(analyst_bot, redis_con):
    while True:
        analyst_bot.getData()
        analyst_bot.calcEMA()
        redis_con.set('ema', analyst_bot.listValueEma[-1])

@infinity
@fault_tolerance
def setLevels(analyst_bot, redis_con):
    while True:
        analyst_bot.getData()
        levels = analyst_bot.identify_support_resistance_levels()
        redis_con.set('levels', dumps(levels))

@infinity
@fault_tolerance
def setLastValue(analyst_bot, redis_con):
    while True:
        analyst_bot.getData()
        redis_con.set('last_value', analyst_bot.currentValue)

@infinity
@fault_tolerance
def setOrdersBook(analyst_bot, redis_con):
    while True:
        orders_book = analyst_bot.getOrderBook()
        redis_con.set('orders_book', dumps(orders_book))

@infinity
@fault_tolerance
def setSuperioritySell(analyst_bot, redis_con):
    while True:
        orders_book = analyst_bot.getOrderBook()
        sum_size_buy = sum([float(order_info["size"]) for order_info in orders_book[0]])
        sum_size_sell = sum([float(order_info["size"]) for order_info in orders_book[1]])
        dif = sum_size_sell - sum_size_buy
        redis_con.set('superiority_sell', dif)

@infinity
@fault_tolerance
def setSuperiorityBuy(analyst_bot, redis_con):
    while True:
        orders_book = analyst_bot.getOrderBook()
        sum_size_buy = sum([float(order_info["size"]) for order_info in orders_book[0]])
        sum_size_sell = sum([float(order_info["size"]) for order_info in orders_book[1]])
        dif = sum_size_buy - sum_size_sell
        redis_con.set('superiority_buy', dif)