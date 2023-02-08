from collecting.statistics_collectors import setMainMetric


if __name__ == "__main__":
    # userInfo = getUsersInfo()[0]
    # api_key = userInfo[1]
    # api_secret = userInfo[2]
    api_key = "wbgNetpsKWLQsMWLOE"
    api_secret = "uukzvsrp1urhlux9Wgs20XALROXOnPY2LjDE"
    proxy = "htpp://10.7.22.6:8443"
    # proxy = userInfo[3]
    # runIntersectionStrategy(api_key, api_secret, proxy, "BTCUSDT", 60)
    # test(api_key, api_secret)
    setMainMetric(api_key, api_secret, "BTCUSDT", 60, proxy)