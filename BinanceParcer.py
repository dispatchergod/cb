from binance import Client
from auth_data import api_key, secret_key
import pandas
import db_manager as db
from datetime import datetime
from CryptoBot import prepare_message_data, Operation

client = Client(api_key, secret_key)
fields = ['pair',
          'price',
          'sell_total',
          'buy_total',
          'sell_mean',
          'buy_mean',
          'date']


def get_all_data():
    write_pairs()
    data = []
    with open('pairs.txt', 'r') as file:
        for line in file.readlines():
            split_line = line.strip().split(":")
            pair = split_line[0]
            price = float(split_line[1].replace("\n", ""))
            ab = get_asks_bids(pair)
            if ab is None:
                continue
            res = [pair, price]
            [res.append(i) for i in ab]
            data.append(res)

    add_to_database(data)
    prepare_message(prepare_message_data())


def prepare_message(data):
    buy_msg = "[BUY] \n"
    sell_msg = "[SELL] \n"

    for item in data:
        if item.count(None) < 2:
            flag = True
            res = [i for i in item if i is not None]
            tag = res[0][1]
            for i in range(len(res) - 2):
                if res[i][1] != res[i + 1][1]:
                    flag = False
            if flag:
                if tag == Operation.BUY:
                    buy_msg = buy_msg + res[0][0] + "\n"
                else:
                    sell_msg = sell_msg + res[0][0] + "\n"

    return buy_msg + sell_msg







def get_asks_bids(pair):
    order_book = client.get_order_book(symbol=pair, limit=500)
    date = int(datetime.now().timestamp())
    if not order_book['bids'] or not order_book['asks']:
        return

    bids = []
    total_bids = 0
    for item in order_book['bids']:
        total_bids += float(item[0]) * float(item[1])
        bids.append(float(item[0]))
    avg_bids_price = list(pandas.DataFrame(bids).mean())[0]

    asks = []
    total_asks = 0
    for item in order_book['asks']:
        total_asks += float(item[0]) * float(item[1])
        asks.append(float(item[0]))
    avg_asks_price = list(pandas.DataFrame(asks).mean())[0]

    return total_bids, total_asks, avg_bids_price, avg_asks_price, date


def write_pairs():
    tickers = client.get_all_tickers()
    pairs = [pair for pair in tickers
             if not pair['symbol'].startswith("USDT")
             and pair['symbol'].find("USDT") > 0
             and float(pair["price"]) < 10]
    with open('pairs.txt', 'w') as file:
        file.write("")
    with open('pairs.txt', 'a') as file:
        for pair in pairs:
            file.write(f"{pair['symbol']}:{pair['price']}\n")


def add_to_database(data):
    for values in data:
        db.db_query(db.add_data,
                    table='coinsdata',
                    fields=fields,
                    values=values)
