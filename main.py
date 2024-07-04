import telebot
import json
from telebot import types
import time

import resume_parsing
import filter_list
import vacancy_parsing
import bd

bot = telebot.TeleBot('*')

query = ''
text = ''
employment = ''
schedule = ''
experience = ''
education_level = ''
salary = ''

@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    if message.text == "/start" or message.text == 'Начать поиск':
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        button_vacancy = types.KeyboardButton(text='Вакансия')
        button_resume = types.KeyboardButton(text='Резюме')
        keyboard.add(button_vacancy, button_resume)
        bot.send_message(message.from_user.id, "Здравствуйте! Вы ищете вакансии или резюме?", reply_markup=keyboard)
        bot.register_next_step_handler(message, get_query)
    elif message.text == "/help":
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        button_start = types.KeyboardButton(text='Начать поиск')
        keyboard.add(button_start)
        bot.send_message(message.from_user.id, "Этот бот поможет Вам найти вакансии или резюме на сайте hh.ru. "
                                               "Чтобы начать, напишите /start или 'Начать поискю'", reply_markup=keyboard)
    else:
        bot.send_message(message.from_user.id, "Я Вас не понял. Напишите /help.")


def get_query(message):
    global query
    if message.text == 'Вакансия':
        query = 'vacancy'
    elif message.text == 'Резюме':
        query = 'resume'
    bot.send_message(message.from_user.id, 'Какая должность Вас интересует?', reply_markup=types.ReplyKeyboardRemove())
    bot.register_next_step_handler(message, get_name)


def get_name(message):
    global text
    text = message.text
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button_yes = types.KeyboardButton(text='Да')
    button_no = types.KeyboardButton(text='Нет')
    keyboard.add(button_yes, button_no)
    bot.send_message(message.from_user.id, 'Хотите ввести фильтры?', reply_markup=keyboard)
    bot.register_next_step_handler(message, get_filter)


def get_filter(message):
    if message.text == "Нет":
        bd.connect()
        bd.create_table()
        bot.send_message(message.from_user.id, "Начинаю поиск...", reply_markup=types.ReplyKeyboardRemove())
        if query == 'resume':
            for a in resume_parsing.get_resume_links(query, text, employment, schedule, experience, education_level,
                                                     salary):
                resume = resume_parsing.get_resume(a)
                if resume is not None:
                    bd.insert_data(query, resume["name"], resume["salary"], resume["experience"],
                               resume["skills"], resume["link"])
                time.sleep(1)
        else:
            for a in vacancy_parsing.get_vacancy_links(query, text, employment, schedule, experience, education_level,
                                                       salary):
                vacancy = vacancy_parsing.get_vacancy(a)
                bd.insert_data(query, vacancy["name"], vacancy["salary"], vacancy["experience"],
                               vacancy["company"], vacancy["link"])
                time.sleep(1)
        count = bd.count()
        if count == 0:
            keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
            button_start = types.KeyboardButton(text='Начать поиск')
            keyboard.add(button_start)
            bot.send_message(message.chat.id, 'К сожалению, по Вашему запросу ничего не найдено. '
                                                   'Попробуйте изменить запрос или фильтры.', reply_markup=keyboard)
        else:
            results = get_data()
            bot.send_message(message.chat.id, f"По вашему запросу найдено {count} "
                                      f"%s" % ("вакансий" if query == 'vacancy' else "резюме"))
            send_data(count, results, message.chat.id)
    elif message.text == "Да":
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        button_doesNotMatter = types.KeyboardButton(text='Неважно')
        button_noExperience = types.KeyboardButton(text='Нет опыта')
        button_between1And3 = types.KeyboardButton(text='От 1 года до 3 лет')
        button_between3And6 = types.KeyboardButton(text='От 3 до 6 лет')
        button_moreThan6 = types.KeyboardButton(text='Более 6 лет')
        keyboard.add(button_doesNotMatter, button_noExperience,
                     button_between1And3, button_between3And6, button_moreThan6)
        bot.send_message(message.from_user.id, 'Опыт работы:', reply_markup=keyboard)
        bot.register_next_step_handler(message, get_experience_filter)


def get_experience_filter(message):
    global experience
    experience = filter_list.experience[message.text]
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button_doesNotMatter = types.KeyboardButton(text='Неважно')
    button_full = types.KeyboardButton(text='Полная занятость')
    button_part = types.KeyboardButton(text='Частичная занятость')
    button_project = types.KeyboardButton(text='Проектная работа')
    button_probation = types.KeyboardButton(text='Стажировка')
    button_volunteer = types.KeyboardButton(text='Волонтерство')
    keyboard.add(button_doesNotMatter, button_full, button_part,
                 button_project, button_probation, button_volunteer)
    bot.send_message(message.from_user.id, 'Тип занятости:', reply_markup=keyboard)
    bot.register_next_step_handler(message, get_employment_filter)


def get_employment_filter(message):
    global employment
    employment = filter_list.employment[message.text]
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button_doesNotMatter = types.KeyboardButton(text='Неважно')
    button_fullDay = types.KeyboardButton(text='Полный день')
    button_flexible = types.KeyboardButton(text='Гибкий график')
    button_shift = types.KeyboardButton(text='Сменный график')
    button_remote = types.KeyboardButton(text='Удаленная работа')
    button_flyInFlyOut = types.KeyboardButton(text='Вахтовый метод')
    keyboard.add(button_doesNotMatter, button_fullDay, button_flexible,
                 button_shift, button_remote, button_flyInFlyOut)
    bot.send_message(message.from_user.id, 'График работы:', reply_markup=keyboard)
    bot.register_next_step_handler(message, get_schedule_filter)


def get_schedule_filter(message):
    global schedule
    schedule = filter_list.schedule[message.text]
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button_doesNotMatter = types.KeyboardButton(text='Неважно')
    button_not_required_or_not_specified = types.KeyboardButton('Не требуется или не указано')
    button_secondary = types.KeyboardButton(text='Среднее')
    button_special_secondary = types.KeyboardButton(text='Среднее специальное')
    button_unfinished_higher = types.KeyboardButton(text='Незаконченное высшее')
    button_higher = types.KeyboardButton(text='Высшее')
    button_bachelor = types.KeyboardButton(text='Бакалавр')
    button_master = types.KeyboardButton(text='Магистр')
    button_candidate = types.KeyboardButton(text='Кандидат наук')
    button_doctor = types.KeyboardButton(text='Доктор наук')
    if query == 'resume':
        keyboard.add(button_doesNotMatter, button_secondary, button_special_secondary,
                     button_unfinished_higher, button_higher, button_bachelor, button_master, button_candidate,
                     button_doctor)
    else:
        keyboard.add(button_not_required_or_not_specified, button_higher, button_special_secondary)
    bot.send_message(message.from_user.id, 'Образование:', reply_markup=keyboard)
    bot.register_next_step_handler(message, get_education_level_filter)


def get_education_level_filter(message):
    global education_level
    education_level = filter_list.education_level[message.text]
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button_doesNotMatter = types.KeyboardButton(text='Неважно')
    keyboard.add(button_doesNotMatter)
    bot.send_message(message.from_user.id, 'Зарплата:', reply_markup=keyboard)
    bot.register_next_step_handler(message, start)


def start(message):
    global salary
    salary = message.text
    bot.send_message(message.from_user.id, "Начинаю поиск...", reply_markup=types.ReplyKeyboardRemove())
    bd.connect()
    bd.create_table()
    if query == 'vacancy':
        for a in vacancy_parsing.get_vacancy_links(query, text, employment, schedule, experience, education_level,
                                                   salary):
            vacancy = vacancy_parsing.get_vacancy(a)
            if vacancy is not None:
                bd.insert_data(query, vacancy["name"], vacancy["salary"], vacancy["experience"],
                               vacancy["company"], vacancy["link"])
            time.sleep(1)
    else:
        for a in resume_parsing.get_resume_links(query, text, employment, schedule, experience, education_level,
                                                 salary):
            resume = resume_parsing.get_resume(a)
            if resume is not None:
                bd.insert_data(query, resume["name"], resume["salary"], resume["experience"],
                           resume["skills"], resume["link"])
            time.sleep(1)
    count = bd.count()
    if count == 0:
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        button_start = types.KeyboardButton(text='Начать поиск')
        keyboard.add(button_start)
        bot.send_message(message.chat.id, 'К сожалению, по Вашему запросу ничего не найдено. '
                                               'Попробуйте изменить запрос или фильтры.', reply_markup=keyboard)
    else:
        results = get_data()
        bot.send_message(message.chat.id, f"По вашему запросу найдено {count} "
                                      f"%s" %("вакансий" if query == 'vacancy' else "резюме"))
        send_data(count, results, message.chat.id)


def get_data():
    records = bd.read_data()
    results = []
    for row in records:
        result = (row[1] + "\n" + row[2] + "\n" + row[3] + "\n" + row[4].replace('{', '')
                  .replace('}', '').replace('\"', '').replace(',', ': ', 1).replace(',', '', 1).replace(',', ', ') + "\n" + row[5] + "\n")
        results.append(result)
    return results


def send_data(count, results, chat_id):
    page = 1
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text=f'{page}/{count}', callback_data=f' '),
               types.InlineKeyboardButton(text=f'>>',
                                    callback_data="{\"method\":\"pagination\",\"NumberPage\":" + str(
                                        page + 1) + ",\"CountPage\":" + str(count) + "}"))
    bot.send_message(chat_id, results[page-1], reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    req = call.data.split('_')
    results = get_data()
    if 'pagination' in req[0]:
        json_string = json.loads(req[0])
        count = json_string['CountPage']
        page = json_string['NumberPage']
        markup = types.InlineKeyboardMarkup()
        if page == 1:
            markup.add(types.InlineKeyboardButton(text=f'{page}/{count}', callback_data=f' '),
                       types.InlineKeyboardButton(text=f'>>',
                                            callback_data="{\"method\":\"pagination\",\"NumberPage\":" + str(
                                                page + 1) + ",\"CountPage\":" + str(count) + "}"))
        elif page == count:
            markup.add(types.InlineKeyboardButton(text=f'<<',
                                            callback_data="{\"method\":\"pagination\",\"NumberPage\":" + str(
                                                page - 1) + ",\"CountPage\":" + str(count) + "}"),
                       types.InlineKeyboardButton(text=f'{page}/{count}', callback_data=f' '))
        else:
            markup.add(types.InlineKeyboardButton(text=f'<<',
                                            callback_data="{\"method\":\"pagination\",\"NumberPage\":" + str(
                                                page - 1) + ",\"CountPage\":" + str(count) + "}"),
                       types.InlineKeyboardButton(text=f'{page}/{count}', callback_data=f' '),
                       types.InlineKeyboardButton(text=f'>>',
                                            callback_data="{\"method\":\"pagination\",\"NumberPage\":" + str(
                                                page + 1) + ",\"CountPage\":" + str(count) + "}"))
        bot.edit_message_text(results[page-1], reply_markup=markup, chat_id=call.message.chat.id,
                              message_id=call.message.message_id)



bot.polling(none_stop=True)
