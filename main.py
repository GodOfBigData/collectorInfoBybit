from collecting.statistics_collectors import setMainMetric
from configs.config import api_key, api_secret, proxy, currency, interval
from time import sleep


if __name__ == "__main__":
    sleep(10)
    setMainMetric(api_key, api_secret, currency, interval, proxy)