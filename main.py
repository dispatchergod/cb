from TelegramBot import tg_api
from apscheduler.schedulers.background import BackgroundScheduler
import db_manager as db
from BinanceParcer import get_all_data, prepare_message
from CryptoBot import prepare_message_data


def main():
    prepared_data = prepare_message_data()
    msg_data = prepared_data
    for item in msg_data:
        if item.count(None) != 3:
            print(f"[DATA] {item}")

    print(prepare_message(prepared_data))
    check_coin_data()
    # tg_api()
    while True:
        pass


def check_coin_data():
    bg_scheduler = BackgroundScheduler(job_defaults={'max_instances': 5})
    bg_scheduler.start()
    sch_id = bg_scheduler.add_job(get_all_data,
                                  'interval',
                                  minutes=10).id

    print("Job", sch_id, "began. Check started every hour")


if __name__ == "__main__":
    main()
