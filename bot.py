import locale
import logging
from glob import glob
from random import choice, randint

import ephem
from emoji import emojize
from telegram.ext import CommandHandler, Filters, MessageHandler, Updater

import settings

# from importlib import import_module

# Будем записывать отчет о работе бота в файл bot.log
logging.basicConfig(format='%(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO,
                    filename='bot.log'
                    )

# Ставим локаль для русского формата даты
locale.setlocale(locale.LC_TIME, 'ru_RU')

# Настройки прокси
PROXY = {'proxy_url': settings.PROXY_URL,
         'urllib3_proxy_kwargs': {
             'username': settings.PROXY_USERNAME,
             'password': settings.PROXY_PASSWORD}}


def get_smile(user_data):  # get and return random emoji for each user
    if 'emoji' not in user_data:
        smile = choice(settings.USER_EMOJI)
        return emojize(smile, use_aliases=True)
    return user_data['emoji']  # or return existing emoji


def get_constellation(update, context):
    planet = update.message.text.split()[-1].title()
    user = ephem.Observer()

    try:
        if planet == 'Earth':
            update.message.reply_text(f'Cannot get constellation of {planet}')
        else:
            planet_class = getattr(ephem, planet)
            planet_compute = planet_class(user.date)
            constellation = ephem.constellation(planet_compute)[-1]
            update.message.reply_text(
                f'{planet.title()} is in the {constellation} constellation today')
    except AttributeError:
        update.message.reply_text(
            f'{planet} is not a valid planet. Please try again...')


def count_words(update, context):
    answer = ''
    if len(context.args) <= 0:
        answer = 'You haven\'t sent anything.'
    elif len(context.args) == 1:
        answer = 'You\'ve sent only 1 word.'
    else:
        answer = f'You\'ve sent {len(context.args)} words'
    update.message.reply_text(answer)


def greet_user(update, context):
    # Saving emoji for each user in context.data_user
    context.user_data['emoji'] = get_smile(context.user_data)
    update.message.reply_text(
        f"Привет, пользователь {context.user_data['emoji']}! Ты вызвал команду /start")


def get_next_full_moon(update, context):
    try:
        full_moon_date = ephem.next_full_moon(context.args[0]).datetime()
        update.message.reply_text(
            'Ближайшее полнолуние: ' + full_moon_date.strftime('%d %B %Y, примерно в %H:%M'))
    except ValueError:
        update.message.reply_text(
            'Некорректная дата! Введите дату в формате \"ГГГГ-ММ-ДД\"')


def talk_to_me(update, context):
    user_text = update.message.text
    user_name = update.effective_user.first_name
    context.user_data['emoji'] = get_smile(context.user_data)
    update.message.reply_text(
        f"{user_name}, что значит \"{user_text}\"?!{context.user_data['emoji']}")


def guess_number(update, context):
    if context.args:
        try:
            user_number = int(context.args[0])
            message = play_random_numbers(user_number)
        except(TypeError, ValueError):
            message = "Введите целое число"
    else:
        message = "Введите целое число"
    update.message.reply_text(message)


def play_random_numbers(user_number):
    bot_number = randint(user_number - 10, user_number + 10)
    if user_number > bot_number:
        message = f"Ты загадал {user_number}, я загадал {bot_number}, ты выиграл!"
    elif user_number == bot_number:
        message = f"Ты загадал {user_number}, я загадал {bot_number}, ничья!"
    else:
        message = f"Ты загадал {user_number}, я загадал {bot_number}, я выиграл!"
    return message


def send_dog_picture(update, context):
    dog_photos_list = glob('images/dog*.jp*g')
    dog_pic_filename = choice(dog_photos_list)
    chat_id = update.effective_chat.id  # get current chat.id for context
    context.bot.send_photo(chat_id=chat_id, photo=open(dog_pic_filename, 'rb'))


def main():
    # Создаем бота и передаем ему ключ для авторизации на серверах Telegram
    mybot = Updater(settings.API_KEY, use_context=True, request_kwargs=PROXY)

    dp = mybot.dispatcher
    dp.add_handler(CommandHandler("start", greet_user))

    dp.add_handler(CommandHandler("guess", guess_number))

    dp.add_handler(CommandHandler("planet", get_constellation))

    dp.add_handler(CommandHandler("dog", send_dog_picture))

    dp.add_handler(CommandHandler("wordcount", count_words))

    dp.add_handler(CommandHandler('next_fool_moon', get_next_full_moon))

    dp.add_handler(MessageHandler(Filters.text, talk_to_me))

    logging.info("Бот стартовал")

    # Командуем боту начать ходить в Telegram за сообщениями
    mybot.start_polling()
    # Запускаем бота, он будет работать, пока мы его не остановим принудительно
    mybot.idle()


if __name__ == "__main__":
    main()
