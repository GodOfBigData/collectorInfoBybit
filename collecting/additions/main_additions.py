def infinity(func):
    def wrapper(analyst_bot, redis_con):
        while True:
            func(analyst_bot, redis_con)
    return wrapper


def fault_tolerance(func):
    def wrapper(analyst_bot, redis_con):
        try:
            func(analyst_bot, redis_con)
        except Exception as exc:
            pass
    return wrapper