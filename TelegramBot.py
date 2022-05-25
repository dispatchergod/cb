from apscheduler.schedulers.background import BackgroundScheduler
import telebot

from auth_data import token
import db_manager

answers = {
    "start": "Hi, Bro! Write 'begin' to work with me. I will send you info every 10 minutes",
    "begin": "Let's go! Write 'break' to stop me.",
    "break": "Bye! Write 'begin' to start me again!"
}


def tg_api():
    bot = telebot.TeleBot(token)
    bg_scheduler = BackgroundScheduler(job_defaults={'max_instances': 20})
    bg_scheduler.start()

    users = [v2 for v1, v2 in db_manager.db_query(db_manager.get_all_data,
                                                  table='users')]
    jobs = [None for _ in users]

    @bot.message_handler(commands=['start'])
    def start_message(message):
        chat_id = message.chat.id
        bot.send_message(chat_id, answers["start"])
        if chat_id not in users:
            users.append(chat_id)
            jobs.append(None)
            db_manager.db_query(db_manager.add_data,
                                table='users',
                                fields=['chat_id'],
                                values=[chat_id])

    @bot.message_handler(content_types=['text'])
    def send_message(message):
        msg = message.text.lower()
        chat_id = message.chat.id
        user_index = users.index(chat_id)
        if msg in answers:
            if jobs[user_index] is None:
                sch_id = bg_scheduler.add_job(send_data,
                                              'interval',
                                              args=(chat_id,),
                                              minutes=15).id
                jobs[user_index] = sch_id
            bg_scheduler.pause_job(jobs[user_index])
            send_text(chat_id, answers[msg])
            if msg == "begin":
                bg_scheduler.resume_job(jobs[user_index])
            elif msg == "break":
                bg_scheduler.pause_job(jobs[user_index])
        else:
            send_text(chat_id, "I don't know this command, check plz!")

    def send_text(chat_id, text):
        try:
            bot.send_message(
                chat_id,
                text
            )
        except Exception as ex:
            print(f"ERRoR: {ex}")

    def send_data(chat_id):
        send_text(chat_id, "")

    def get_data():
        db_manager.db_query(db_manager.get_all_data,
                            table="coinbase")

    bot.infinity_polling()
    # def poll():
    #     bot.polling()
    #
    # try:
    #     poll()
    #
    # except Exception as ex:
    #     print(f"[ERROR] {ex}")
    #     poll()
