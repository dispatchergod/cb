import db_manager as db
from datetime import datetime
from enum import Enum

fields = ['pair',
          'price',
          'sell_total',
          'buy_total',
          'sell_mean',
          'buy_mean',
          'date']


class Trend(Enum):
    UP = 1
    DOWN = -1


class Rating(Enum):
    GRAY = 0
    GREEN = 1
    ORANGE = 2
    RED = 3


class Operation(Enum):
    BUY = 1
    SELL = -1


def get_all_data():
    query = "SELECT DISTINCT pair FROM coinsdata;"

    pairs = [pair[0] for pair in db.db_query(db.get_data, query=query)]
    data = []
    for pair in pairs:
        data.append(db.db_query(db.search_data,
                                table="coinsdata",
                                fields=fields,
                                condition=f"pair='{pair}'"))
    return data


def get_useful_data():
    data = get_all_data()
    useful_data = []
    cur_time = int(datetime.now().timestamp())
    for pair in data:
        res = [d for d in pair if d[-1] + 86400 > cur_time]
        if res:
            if res[0][3] != 0 and res[0][4] != 0 and len(res) > 4:
                useful_data.append(res)

    return useful_data


def check_trend(data):
    now = int(datetime.now().timestamp())
    res_data = [pair for pair in data if pair[-1] + 86400 > now]

    trend = 0
    for index in range(len(res_data) - 2):
        trend += res_data[index][1] - res_data[index + 1][1]
    if trend < 0:
        return Trend.UP
    else:
        return Trend.DOWN


def check_price(data):
    prices = [pair[1] for pair in data]
    diff = 0.02
    one_diff = diff * 3

    rating = Rating.GRAY
    operation = None

    cost_diff = prices[-4] * one_diff
    if prices[-4] + cost_diff < prices[-1]:
        operation = Operation.BUY
        rating = Rating.GREEN

    cost_diff = prices[-4] * one_diff
    if prices[-4] - cost_diff > prices[-1]:
        operation = Operation.SELL
        rating = Rating.GREEN

    cost_diff = prices[-4] * diff
    if prices[-4] + cost_diff < prices[-3]:
        cost_diff = prices[-3] * diff
        if prices[-3] + cost_diff < prices[-2]:
            cost_diff = prices[-2] * diff
            if prices[-2] + cost_diff < prices[-1]:
                operation = Operation.BUY
                rating = Rating.ORANGE

    cost_diff = prices[-4] * diff
    if prices[-4] - cost_diff > prices[-3]:
        cost_diff = prices[-3] * diff
        if prices[-3] - cost_diff > prices[-2]:
            cost_diff = prices[-2] * diff
            if prices[-2] - cost_diff > prices[-1]:
                operation = Operation.SELL
                rating = Rating.ORANGE
    return operation, rating


def ask_bid_check(data):
    # возможно надо добавить каскадную проверку, вместо разовой, но это потом проверю
    # params: pair, ask, bid
    # pair = data[0][0]
    # day_ago_price = data[]
    back_ask = data[-4][4]
    back_bid = data[-4][3]
    back_diff = back_ask / back_bid

    now_ask = data[-1][4]
    now_bid = data[-1][3]
    now_diff = now_ask / now_bid

    total_diff = now_diff - back_diff

    rating = Rating.GRAY
    operation = None

    if total_diff < 0:
        operation = Operation.BUY
        if back_ask < now_ask or back_bid > now_bid:
            rating = Rating.GREEN
            if back_ask < now_ask and back_bid > now_bid:
                rating = Rating.ORANGE
    else:
        operation = Operation.SELL
        if back_ask > now_ask or back_bid < now_bid:
            rating = Rating.GREEN
            if back_ask > now_ask and back_bid < now_bid:
                rating = Rating.ORANGE
    return operation, rating


def trend_price_demand(data):
    trend = check_trend(data)
    price = check_price(data)
    ask_bid = ask_bid_check(data)

    res_rating = Rating.GRAY
    if not (price[1] == Rating.GRAY or ask_bid[1] == Rating.GRAY):
        if price[1] == Rating.ORANGE and ask_bid[1] == Rating.ORANGE:
            res_rating = Rating.RED
        else:
            res_rating = Rating.ORANGE

    res_operation = None
    if trend == Trend.UP:
        if price[0] == ask_bid[0]:
            res_operation = ask_bid[0]
    else:
        if price[0] == ask_bid[0] and ask_bid[0] == Operation.SELL:
            res_operation = ask_bid[0]

    return res_operation, res_rating


def demand(data):
    cur_buy_sell = data[-1][3] / data[-1][2]

    day_buy_sell = data[0][3] / data[0][2]
    day_diff = abs(day_buy_sell - cur_buy_sell)

    operation = None
    rating = Rating.GRAY

    if day_diff > 1:
        if day_buy_sell < 1:
            operation = Operation.BUY
            rating = Rating.ORANGE
        else:
            operation = Operation.SELL
            rating = Rating.ORANGE
    return operation, rating


def trend_price(data):
    trend = check_trend(data)
    price = check_price(data)

    operation = None
    rating = Rating.GRAY
    if price[0] is None:
        return operation, rating

    if trend == Trend.UP:
        operation = price[0]
        rating = price[1]
    else:
        if price[0].value == Operation.SELL:
            operation = price[0]
            rating = price[1]
    return operation, rating


def prepare_message_data():
    results = []
    for data in get_useful_data():
        pair = data[0][0]

        tpd = trend_price_demand(data)
        tp = trend_price(data)
        d = demand(data)

        temp_data = [None] * 3
        if tpd[0] is not None and tpd[1].value > 1:
            temp_data[0] = (pair, tpd[0], tpd[1])
        if tp[0] is not None and tp[1].value > 1:
            temp_data[1] = (pair, tp[0], tp[1])
        if d[0] is not None and d[1].value > 1:
            temp_data[2] = (pair, d[0], d[1])
        results.append(temp_data)
    return results


def prepare_message(data):
    pass
