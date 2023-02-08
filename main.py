from collecting.statistics_collectors import setMainMetric
from configs.config import api_key, api_secret, proxy, currency, interval


if __name__ == "__main__":
    setMainMetric(api_key, api_secret, currency, interval, proxy)