import os
import telebot
import messages
import data_parser
import dbworker
import config
import utils
from exceptions import APIRequestException, ParsingException, DBException
import threading

bot = telebot.TeleBot(config.telegram_token)
parser = data_parser.get_parser()
db = dbworker.get_db_worker()


# Начало диалога
@bot.message_handler(commands=["start"])
def handle_start(message):
    try:
        bot.send_message(message.chat.id, messages.START_MESSAGE % message.from_user.username)
    except Exception as ex:
        bot.send_message(message.chat.id, messages.UNEXPECTED_ERROR % str(ex))


# Список команд
@bot.message_handler(commands=["menu"])
def handle_menu(message):
    try:
        bot.send_message(message.chat.id, messages.MENU_MESSAGE)
    except Exception as ex:
        bot.send_message(message.chat.id, messages.UNEXPECTED_ERROR % str(ex))


# Список команд
@bot.message_handler(commands=["info"])
def handle_info(message):
    try:
        bot.send_message(message.chat.id, messages.INFO_MESSAGE)
    except Exception as ex:
        bot.send_message(message.chat.id, messages.UNEXPECTED_ERROR % str(ex))


# Список городов
@bot.message_handler(commands=["citylist"])
def handle_city_list(message):
    try:
        send_rq_in_work(message)
        result = parser.get_city_list()
        if result.empty:
            bot.send_message(message.chat.id, messages.NO_DATA)
        else:
            bot.send_message(message.chat.id, utils.pretty_print_city_list(result))
    except (APIRequestException, ParsingException) as ex:
        bot.send_message(message.chat.id, messages.REQUEST_ERROR % str(ex))
    except Exception as ex:
        bot.send_message(message.chat.id, messages.UNEXPECTED_ERROR % str(ex))


# Город отправления для анализа
@bot.message_handler(commands=["setsrccity"])
def handle_set_src_city(message):
    try:
        force_reply = telebot.types.ForceReply(selective=False)
        replied_message = bot.send_message(message.chat.id, messages.SRC_CITY_RQ, reply_markup=force_reply)
        bot.register_next_step_handler(replied_message, handle_src_city)
    except Exception as ex:
        bot.send_message(message.chat.id, messages.UNEXPECTED_ERROR % str(ex))


# Сохранение города отправления
def handle_src_city(message):
    try:
        send_rq_in_work(message)
        city_name = message.text
        if parser.do_city_exist(city_name):
            db.set_user_src_city(message.chat.id, city_name)
            bot.reply_to(message, messages.SRC_CITY_RS)
        else:
            error = f'Город {city_name} не найден'
            bot.reply_to(message, messages.REQUEST_ERROR % error)
    except DBException as ex:
        bot.reply_to(message, messages.REQUEST_ERROR % str(ex))
    except Exception as ex:
        bot.send_message(message.chat.id, messages.UNEXPECTED_ERROR % str(ex))


# Популярные направления
@bot.message_handler(commands=["populardestinations"])
def handle_popular_destinations(message):
    try:
        send_rq_in_work(message)
        city_name = db.get_user_src_city(message.chat.id)
        if city_name:
            result = parser.get_popular_destinations(city_name)
            if result.empty:
                bot.send_message(message.chat.id, messages.NO_DATA)
            else:
                result = utils.wrap_pre(utils.pretty_print_popular_destinations(result))
                msg = messages.POPULAR_DESTINATIONS_RS % city_name
                bot.send_message(message.chat.id, msg + result, parse_mode='HTML')
        else:
            bot.send_message(message.chat.id, messages.SRC_CITY_EMPTY)
    except (APIRequestException, ParsingException, DBException) as ex:
        bot.send_message(message.chat.id, messages.REQUEST_ERROR % str(ex))
    except Exception as ex:
        bot.send_message(message.chat.id, messages.UNEXPECTED_ERROR % str(ex))


# Календарь самых высоких цен на следующий месяц (top 20)
@bot.message_handler(commands=["maxmonthprices"])
def handle_max_month_prices(message):
    try:
        city_name = db.get_user_src_city(message.chat.id)
        if city_name:
            force_reply = telebot.types.ForceReply(selective=False)
            replied_message = bot.send_message(message.chat.id, messages.DEST_CITY_RQ, reply_markup=force_reply)
            bot.register_next_step_handler(replied_message,
                                           lambda m: handle_max_month_prices_for_dest_city(m, city_name))
        else:
            bot.send_message(message.chat.id, messages.SRC_CITY_EMPTY)
    except (APIRequestException, ParsingException, DBException) as ex:
        bot.send_message(message.chat.id, messages.REQUEST_ERROR % str(ex))
    except Exception as ex:
        bot.send_message(message.chat.id, messages.UNEXPECTED_ERROR % str(ex))


# Календарь самых высоких цен на следующий месяц (top 20)
def handle_max_month_prices_for_dest_city(message, src_city_name):
    try:
        send_rq_in_work(message)
        dest_city_name = message.text
        result = parser.get_month_prices(src_city_name, dest_city_name)
        if result.empty:
            bot.reply_to(message, messages.NO_DATA)
        else:
            result = utils.wrap_pre(utils.pretty_print_month_prices(result))
            msg = messages.MAX_MONTH_PRICES_RS % (src_city_name, dest_city_name)
            bot.reply_to(message, msg + result, parse_mode='HTML')
    except (APIRequestException, ParsingException, DBException) as ex:
        bot.reply_to(message, messages.REQUEST_ERROR % str(ex))
    except Exception as ex:
        bot.send_message(message.chat.id, messages.UNEXPECTED_ERROR % str(ex))


# Календарь самых низких цен на следующий месяц (top 20)
@bot.message_handler(commands=["minmonthprices"])
def handle_min_month_prices(message):
    try:
        city_name = db.get_user_src_city(message.chat.id)
        if city_name:
            force_reply = telebot.types.ForceReply(selective=False)
            replied_message = bot.send_message(message.chat.id, messages.DEST_CITY_RQ, reply_markup=force_reply)
            bot.register_next_step_handler(replied_message,
                                           lambda m: handle_min_month_prices_for_dest_city(m, city_name))
        else:
            bot.send_message(message.chat.id, messages.SRC_CITY_EMPTY)
    except (APIRequestException, ParsingException, DBException) as ex:
        bot.send_message(message.chat.id, messages.REQUEST_ERROR % str(ex))
    except Exception as ex:
        bot.send_message(message.chat.id, messages.UNEXPECTED_ERROR % str(ex))


# Календарь самых низких цен на следующий месяц (top 20)
def handle_min_month_prices_for_dest_city(message, src_city_name):
    try:
        send_rq_in_work(message)
        dest_city_name = message.text
        result = parser.get_month_prices(src_city_name, dest_city_name, True)
        if result.empty:
            bot.reply_to(message, messages.NO_DATA)
        else:
            result = utils.wrap_pre(utils.pretty_print_month_prices(result))
            msg = messages.MIN_MONTH_PRICES_RS % (src_city_name, dest_city_name)
            bot.reply_to(message, msg + result, parse_mode='HTML')
    except (APIRequestException, ParsingException, DBException) as ex:
        bot.reply_to(message, messages.REQUEST_ERROR % str(ex))
    except Exception as ex:
        bot.send_message(message.chat.id, messages.UNEXPECTED_ERROR % str(ex))


# Самые низкие цены по месяцам (следующие 6 месяцев)
@bot.message_handler(commands=["minpricespermonth"])
def handle_min_prices_per_month(message):
    try:
        send_rq_in_work(message)
        city_name = db.get_user_src_city(message.chat.id)
        if city_name:
            force_reply = telebot.types.ForceReply(selective=False)
            replied_message = bot.send_message(message.chat.id, messages.DEST_CITY_RQ, reply_markup=force_reply)
            bot.register_next_step_handler(replied_message, lambda m: handle_min_prices_per_month_for_dest_city(m, city_name))
        else:
            bot.send_message(message.chat.id, messages.SRC_CITY_EMPTY)
    except (APIRequestException, ParsingException, DBException) as ex:
        bot.send_message(message.chat.id, messages.REQUEST_ERROR % str(ex))
    except Exception as ex:
        bot.send_message(message.chat.id, messages.UNEXPECTED_ERROR % str(ex))


# Самые низкие цены по месяцам (следующие 6 месяцев)
def handle_min_prices_per_month_for_dest_city(message, src_city_name):
    try:
        send_rq_in_work(message)
        dest_city_name = message.text
        data = parser.get_prices_per_month(src_city_name, dest_city_name, True)
        if data:
            result = utils.wrap_pre(utils.pretty_print_prices_per_month(data))
            msg = messages.MIN_PRICES_PER_MONTH_RS % (src_city_name, dest_city_name)
            bot.reply_to(message, msg + result, parse_mode='HTML')
            bot.send_photo(message.chat.id, utils.build_prices_per_month_bar(data, 'Самые низкие цены по месяцам'))
        else:
            bot.reply_to(message, messages.NO_DATA)
    except (APIRequestException, ParsingException, DBException) as ex:
        bot.reply_to(message, messages.REQUEST_ERROR % str(ex))
    except Exception as ex:
        bot.send_message(message.chat.id, messages.UNEXPECTED_ERROR % str(ex))


# Самые высокие цены по месяцам (следующие 6 месяцев)
@bot.message_handler(commands=["maxpricespermonth"])
def handle_max_prices_per_month(message):
    try:
        send_rq_in_work(message)
        city_name = db.get_user_src_city(message.chat.id)
        if city_name:
            force_reply = telebot.types.ForceReply(selective=False)
            replied_message = bot.send_message(message.chat.id, messages.DEST_CITY_RQ, reply_markup=force_reply)
            bot.register_next_step_handler(replied_message, lambda m: handle_max_prices_per_month_for_dest_city(m, city_name))
        else:
            bot.send_message(message.chat.id, messages.SRC_CITY_EMPTY)
    except (APIRequestException, ParsingException, DBException) as ex:
        bot.send_message(message.chat.id, messages.REQUEST_ERROR % str(ex))
    except Exception as ex:
        bot.send_message(message.chat.id, messages.UNEXPECTED_ERROR % str(ex))


# Самые высокие цены по месяцам (следующие 6 месяцев)
def handle_max_prices_per_month_for_dest_city(message, src_city_name):
    try:
        send_rq_in_work(message)
        dest_city_name = message.text
        data = parser.get_prices_per_month(src_city_name, dest_city_name)
        if data:
            result = utils.wrap_pre(utils.pretty_print_prices_per_month(data))
            msg = messages.MAX_PRICES_PER_MONTH_RS % (src_city_name, dest_city_name)
            bot.reply_to(message, msg + result, parse_mode='HTML')
            bot.send_photo(message.chat.id, utils.build_prices_per_month_bar(data, 'Самые высокие цены по месяцам'))
        else:
            bot.reply_to(message, messages.NO_DATA)
    except (APIRequestException, ParsingException, DBException) as ex:
        bot.reply_to(message, messages.REQUEST_ERROR % str(ex))
    except Exception as ex:
        bot.send_message(message.chat.id, messages.UNEXPECTED_ERROR % str(ex))


# Неизвестные входные команды
@bot.message_handler(func=lambda message: True)
def handle_unexpected_input(message):
    try:
        bot.send_message(message.chat.id, messages.UNKNOWN_CMD)
    except Exception as ex:
        bot.send_message(message.chat.id, messages.UNEXPECTED_ERROR % str(ex))


# Необрабатываемые форматы входных данных
@bot.message_handler(content_types=['sticker', 'pinned_message', 'photo', 'audio'])
def handle_unexpected_input(message):
    try:
        bot.send_message(message.chat.id, messages.UNKNOWN_CMD)
    except Exception as ex:
        bot.send_message(message.chat.id, messages.UNEXPECTED_ERROR % str(ex))


def send_rq_in_work(message):
    with open(os.getcwd() + config.in_work_pic, 'rb') as pic:
        bot.send_photo(message.chat.id, pic)


if __name__ == "__main__":
    bot.skip_pending = True
    bot.polling(none_stop=True, interval=0)
