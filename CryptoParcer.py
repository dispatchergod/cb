import requests as req
import json
from datetime import datetime
import db_manager
import pandas

URL = "https://yobit.net/api/3"
IGNORE_INV = "ignore_invalid=1"


def get_info():
    response = req.get(url=f"{URL}/info/?{IGNORE_INV}")

    with open('info.json', 'w') as file:
        file.write(response.text)

    return get_pairs("_usd")


def get_pairs(key):
    with open('info.json', 'r') as file:
        text = file.read()
        data = json.loads(text)
        pairs = [key for _, key in enumerate(data["pairs"])]
        cur_pairs = [pair for pair in pairs if pair.find(key) > 0]
        print(pairs)
        return cur_pairs


def get_ticker(coin1="btc", coin2="usd"):
    response = req.get(url=f"{URL}/ticker/{coin1}_{coin2}?{IGNORE_INV}")
    return response.json()


def get_trades(pair):
    limit = 1000
    response = req.get(url=f"{URL}/trades/{pair}?limit={limit}&{IGNORE_INV}").json()
    # coins = pair.split('_')
    # cost_res = get_ticker(coin1=coins[0], coin2=coins[1])[pair]
    if not response:
        return
    date = int(datetime.now().timestamp())
    print(response)

    total_trade_ask = 0
    total_trade_bid = 0

    for item in response[pair]:
        total = item["price"] * item["amount"]
        if item["type"] == "ask":
            # want to SELL

            total_trade_ask += total
        else:
            # want to BUY
            total_trade_bid += total
    fields = ['pair', 'sell_total', 'buy_total', 'date', 'cost', ]
    values = [pair, round(total_trade_ask, 2), round(total_trade_bid, 2), date]

    return fields, values


def add_data_db(fields, values):
    db_manager.db_query(db_manager.add_data,
                        table='coindata',
                        fields=fields,
                        values=values)


def upload_data():
    try:
        with open("normal_pairs.txt", 'r') as file:
            pairs = [pair.replace("\n", "") for pair in file.readlines()]
            for pair in pairs:
                data = get_trades(pair)
                add_data_db(data[0], data[1])
    except Exception as ex:
        print(f"[ERROR] {ex}")
    finally:
        print("[SUCCESS] All pairs was loaded successfully")


def get_useful_data():
    fields = ['pair', 'sell_total', 'buy_total', 'date']
    with open("normal_pairs.txt", 'r') as file:
        pairs = [pair.replace("\n", "") for pair in file.readlines()]
        data = []
        for pair in pairs:
            data.append(db_manager.db_query(db_manager.search_data,
                                            table="coindata",
                                            fields=fields,
                                            condition=f"pair='{pair}'"))
        return data


def find_top_coins():
    with open("pairs.txt", "r") as file:
        for _ in range(0, 1496):
            line = file.readline().strip()
            coins = line.split("_")
            response = get_ticker(coins[0], coins[1])
            if response[line]["last"] > 100:
                print(response[line]["last"])
                print(line)
                with open("normal_pairs.txt", 'a') as n_file:
                    n_file.write(f"{line}\n")