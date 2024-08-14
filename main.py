from aiogram import Bot, Dispatcher
from aiogram.types import *
from aiogram.filters import Command
from aiogram import F
from apscheduler.schedulers.asyncio import AsyncIOScheduler

import structural.adapter
import constants
import structural.what_num
from datetime import datetime
import random
import pickle
import structural.Classes as cls

# Вставляем токен из файла с константами
BOT_TOKEN = constants.TOKEN

bot = Bot(BOT_TOKEN)
dp = Dispatcher()

# Создаем scheduler котрый будет периодически выполнять задания
scheduler = AsyncIOScheduler()
scheduler_on = False #

delta = 1 
lst_num = structural.what_num.issueNumber(url = constants.BASE)  # Присваиваем дату последнего стрипа с acomics

# Подгружаем словарь с пользователем
UsersDictionary = open('Users.pkl', 'rb')
Users = pickle.load(UsersDictionary)

# Подгружаем массив с фильмами
FilmsArray = open('Films.pkl', 'rb')
Films = pickle.load(FilmsArray)

# Подгружаем стрикеры
sticker_list = constants.STICKERS

@dp.message(Command("help"))
async def help(msg:Message):
    await msg.answer(("/start и /continue - стрип на котором вы остановились" 
                      "/date - Стрип по определенной дате" 
                      "/last - послдений переведенный стрип"))

# Реагирует на /start и /continue, выдавая стрип на котором остановился пользователь
@dp.message(Command(commands=['start', 'continue']))
async def start(msg:Message):
    # Достаем запись о пользователе с словаря
    chat_id = msg.chat.id
    user = Users.setdefault(chat_id, cls.User(id = chat_id))

    # Высылаем стрип на котором остановился пользователь в зависимотси от его режима
    if(user.mode == 'general'):
        strip_number = user.cur_num
    
    elif(user.mode == 'favorite'):
        strip_number = user.favorite_list[user.cur_index]

    # Стикер высылается только при команде /start
    if(msg.text == '/start'):
        # Выбираем случайны стикер и отправляем его
        choised_sticker = random.choices(sticker_list, weights=[24,23,24,24,5], k=1) # random.choices всегда возвращает список
        await msg.answer_sticker(choised_sticker[0]) # А данная фунция принимает только строку, поэтому приходится изощератся 

    structural.adapter.url_to_square(url = constants.BASE + '/' + str(strip_number)) # Парсим стрип из акомикса
    request = FSInputFile(constants.RESULT) # Открываем файл 
    issueName = structural.what_num.issueName(url=constants.BASE + '/' +str(strip_number)) # Достаем дату выпуска стрипа который выслан пользователю
    await msg.answer_photo(request, reply_markup = user.menu, caption = issueName) # Высылаем стрип

    # Обновляем словарь
    Users.update({chat_id: user})

# Реагирует на /last, выдавая последний стрип на acomics
@dp.message(Command('last'))
async def last(msg:Message):
    # Обнавляем дату последнего стрипа с acomics потому что она может поменятся
    global lst_num
    lst_num = structural.what_num.issueNumber(url=constants.BASE)  

    # Достаем запись о пользователе с словаря
    chat_id = msg.chat.id 
    user = Users.setdefault(chat_id, cls.User(id = chat_id)) 

    # Обновляем словарь
    user.cur_num = lst_num
    Users.update({chat_id: user})

    strip_number = user.change_mode(new_mode = 'general')
    
    structural.adapter.url_to_square(url = constants.BASE + '/' + str(strip_number)) # Парсим стрип из акомикса
    request = FSInputFile(constants.RESULT) # Открываем файл 
    issueName = structural.what_num.issueName(url=constants.BASE) # Достаем дату выпуска последнего стрипа acomics
    await msg.answer_photo(request, reply_markup = user.menu, caption = issueName) # Высылаем сам стрип

@dp.message(Command('film'))
async def video_mode(msg:Message):
    # Достаем запись о пользователе с словаря
    chat_id = msg.chat.id 
    user = Users.setdefault(chat_id, cls.User(id = chat_id))

    content = user.change_mode(new_mode = 'video')
    film = Films[content]
    await msg.answer_video(video = film.video, reply_markup = user.menu, caption = film.name)

# Логика кнопок работающие с измменением номера контента
@dp.callback_query(F.data.contains('delta')) 
async def delta_button(query: CallbackQuery):
    # Достаем запись о пользователе с словаря
    chat_id= query.message.chat.id
    user = Users.setdefault(chat_id, cls.User(id = chat_id))

    action = query.data.split(" ")
    action = action[0]
    user.cur_num, user.cur_index, user.vmark = button_delta(action = action, mode = user.mode, 
                                                number = user.cur_num, findex = user.cur_index, vmark = user.vmark,
                                                fav_len = len(user.favorite_list), film_len = len(Films))
    
    Users.update({chat_id: user}) # Обнавляем словарь 
    
    if(user.mode != 'video'):
        strip_number = user.cur_num if user.mode == 'general' else user.favorite_list[user.cur_index] # В зависимости от режима менятся конетент
                                                                                                  # который будет выводится пользователю
     
        structural.adapter.url_to_square(url=constants.BASE + '/' +str(strip_number)) # Достаем стрип с номером = strip_number
        request = FSInputFile(constants.RESULT) # Открываем файл
        issueName = structural.what_num.issueName(url=constants.BASE + '/' +str(strip_number)) # Достаем дату выпуска

        await query.message.answer_photo(request, reply_markup = user.menu, caption= issueName) # Отправляем стрип
    else:
        film = Films[user.vmark]
        await query.message.answer_video(video = film.video, reply_markup = user.menu, caption = film.name)
    await query.message.delete() # Удаляем предыдущие сообщение 

# Логика кнопок отвественных за смену режима 
@dp.callback_query(F.data.contains('mode'))
async def mode_button(query: CallbackQuery):
    # Достаем запись о пользователе с словаря
    chat_id= query.message.chat.id
    user = Users.setdefault(chat_id, cls.User(id = chat_id))

    # Смена режима  
    content_number = user.change_mode(new_mode = query.data)

    Users.update({chat_id: user}) # Обнавляем словарь 
    if(user.mode != 'video'):
        structural.adapter.url_to_square(url=constants.BASE + '/' +str(content_number)) # Достаем стрип с номером = strip_number
        request = FSInputFile(constants.RESULT) # Открываем файл
        issueName = structural.what_num.issueName(url=constants.BASE + '/' +str(content_number)) # Достаем дату выпуска

        await query.message.answer_photo(request, reply_markup = user.menu, caption = issueName) # Отправляем стрип
    else:
        film = Films[content_number]
        await query.message.answer_video(video = film.video, reply_markup = user.menu, caption = film.name)
    await query.message.delete() # Удаляем предыдущие сообщение

# Логика кнопок работающие со списком любимых стрипов 
@dp.callback_query(F.data.contains('favorite'))
async def fav_button(query: CallbackQuery):
    # Достаем запись о пользователе с словаря
    chat_id= query.message.chat.id
    user = Users.setdefault(chat_id, cls.User(id = chat_id))

    if (query.data == 'add favorite'):
        try:
            user.favorite_list.remove(user.cur_num) # Убераем стрип из любимого, что бы не копились дубликаты
        except:
            answer = "Ошибка добавления избраного" 

        user.favorite_list.append(user.cur_num) # Добавляем в конец списка еще один любимый стрип
        user.favorite_list.sort() # Затем его сортируем
        answer = "Стрип добавлен в избраное"

        Users.update({chat_id: user}) # Обнавляем словарь
        await query.message.answer(answer) # Отправляем обратную связь

    elif (query.data == 'remove favorite'):
        try:
            if(user.mode == 'general'):
                strip_number = user.cur_num
            
            elif(user.mode == 'favorite'):
                strip_number = user.favorite_list[user.cur_index]

            user.favorite_list.remove(strip_number) # Убераем стрип из любимого
            answer = "Стрип убран из избраного"
        except:
            answer = "Данного стрипа изначально не было в избраных"

        Users.update({chat_id: user}) # Обнавляем словарь
        await query.message.answer(answer) # Отправляем обратную связь

# Выводит стрип по определенной дате 
@dp.message(Command("date"))
async def date(msg:Message):
    # Достаем запись о пользователе с словаря
    chat_id = msg.chat.id
    user = Users.setdefault(chat_id,cls.User(id = chat_id))
 
    # Разделяем запрос по пробелу
    query = msg.text.split(" ")
    
    # Если пользователь не написал дату
    if(len(query)==1):
        await msg.answer("Вы не написали дату стрипа. Напишите её в формате YYYY-MM-DD")
    
    else:
        try:
            q_date = datetime.strptime(query[1], '%Y-%m-%d') # Переводим текст в формат datatime 
            user.cur_num = structural.what_num.num_of_date(cur_date = q_date) # Достаем номер за эту дату

            # При использование команды /date режим всегда меняестя на стандартный 
            strip_number = user.change_mode(new_mode = 'general', strip_number = user.cur_num)

            structural.adapter.url_to_square(url=constants.BASE + '/' +str(strip_number)) # Достаем стрип с номером = cur_num
            request = FSInputFile(constants.RESULT) # Открываем файл 
            issueName = structural.what_num.issueName(url=constants.BASE + '/' +str(strip_number)) # Достаем дату выпуска
            await msg.answer_photo(request, reply_markup = user.menu, caption = issueName) # Отправляем стрип

            # Обновляем словарь
            Users.update({chat_id: user}) 
       
        except:
            await msg.answer("Возможно вы не правильно написали дату стрипа или стрипа за эту дату нету. Напишите дату в формате YYYY-MM-DD")

# Подписывает пользователя на уведомления
@dp.message(Command('sub'))
async def subscribe(msg:Message):
    # Достаем запись о пользователе с словаря
    chat_id = msg.chat.id
    user = Users.setdefault(chat_id, cls.User(id = chat_id))

    user.sub = True # Подписываем на уведомления

    Users.update({chat_id: user}) # Обновляем словарь

# Дальше идет только административынй блок кода

# Сохранение словарей
@dp.message(Command("save_dictionary"))
async def save_dictionary(msg:Message):
    # Подключаем базу пользователей
    chat_id = msg.chat.id
    user = Users.setdefault(chat_id, cls.User(id = chat_id))

    # Если пользователей обладает статусом админ, сохраняем словари
    if (user.status == 'admin'):
        # Сохраняем словарь с пользователями
        SaveUsersDictionary = open('Users.pkl', 'wb')
        pickle.dump(Users, SaveUsersDictionary)
        await msg.answer("Словарь сохранен успешно") # Высылаем обратную связь

    else:
        await msg.answer("К сожалению я вас не понимаю")
    
# Узнаем длину словарей
@dp.message(Command("report"))
async def report(msg:Message):
    # Подключаем базу пользователей
    chat_id = msg.chat.id
    user = Users.setdefault(chat_id, cls.User(id = chat_id))

    # Если пользователей обладает статусом админ высылаем длину словаря
    if (user.status == 'admin'):
        length = str(len(Users)) # Указывает количество пользователей 
        dictionary = str(Users.keys()) # Список chat id пользователей 

        # Все это высылаем
        await msg.answer("Длина словаря - " + length)
        await msg.answer(dictionary)
    
    else:
        await msg.answer("К сожалению я вас не понимаю")

# Создаем работы и запускаем все schedulers
@dp.message(Command("launch_schedulers"))
async def launch_schedulers(msg:Message):
    # Подключаем базу пользователей
    chat_id = msg.chat.id
    user = Users.setdefault(chat_id, cls.User(id = chat_id))

    # Если пользователей обладает статусом админ и schedulers не были запущены, выполняем команду
    if user.status == 'admin' and not scheduler_on:
        scheduler.add_job(func = notify, trigger = "cron",  hour = 13, minute = 30, timezone = "Europe/Moscow") # Добавляем работу в scheduler
        scheduler.start() # Запускаем наш scheduler
        scheduler_on = True

    else:
        await msg.answer("К сожалению я вас не понимаю")

# Вручную через команду можно вызывать высылку уведомлений 
@dp.message(Command("notify"))
async def send_notification(msg:Message):
    # Подключаем базу пользователей
    chat_id = msg.chat.id
    user = Users.setdefault(chat_id, cls.User(id = chat_id))

    # Если пользователей обладает статусом админ, выполняем команду
    if user.status == 'admin':
        await notify()
    else:
        await msg.answer("К сожалению я вас не понимаю")

# Блок добавление фильма 
@dp.message(Command("add_movie"))
async def add_movie(msg:Message):
    # Подключаем базу пользователей
    chat_id = msg.chat.id
    user = Users.setdefault(chat_id, cls.User(id = chat_id))

    # Если пользователей обладает статусом админ, выполняем команду
    if(user.status == 'admin'):
        new_film = cls.Film() # Создаем экземпляр класса Film
        Films.append(new_film) # Добавляем его в конец массива
        await msg.answer("Вышлите название для фильма ('Название: xxx')")

    else:
        await msg.answer("К сожалению я вас не понимаю")

# Добавляем имя фильму
@dp.message(F.text.startswith('Название: '))
async def name_film(msg:Message):
    name = msg.text[10:] # Делим сообщение по проблему что бы узнать название фильма
    if(Films[-1].name == 'null'):
        Films[-1].name = name
        await msg.answer("А теперь вышлите фильм")
    else:
        await msg.answer("К сожалению я вас не понимаю")

# Добавляем сам фильм    
@dp.message(F.video)
async def video_film(msg:Message):
    if(Films[-1].video == 'null' and Films[-1].name != 'null'):
        Films[-1].video = msg.video.file_id # Достаем айди видео 

        SaveFilmArray = open('Films.pkl', 'wb')
        pickle.dump(Films, SaveFilmArray) # Сохраняем массив с фильмами

        await msg.answer("Фильм добавлен") # Высалаем обратную связь

    else:
        await msg.answer("К сожалению я вас не понимаю")

# Отвечает за удаление фильма из списка 
@dp.message(Command('delete_film'))
async def delete_film(msg:Message):
    # Подключаем базу пользователей
    chat_id = msg.chat.id
    user = Users.setdefault(chat_id, cls.User(id = chat_id))

    # Разделяем запрос по пробелу
    query = msg.text.split(' ')

    # Если пользователь админ и отправил команду без индекса фильма, тогда выводим список 
    if len(query) == 1 and user.status == 'admin':
        film_lst = structural.adapter.array_to_text(array = Films)
        await msg.answer('Какой из фильмов удалить:' + film_lst)

    # Если пользователь админ и отправил команду с индексом фильма, тогда удаляем фильм по индексу
    elif user.status == 'admin':
        try:
            film_index = int(query[1])-1
            del Films[film_index]

            film_lst = structural.adapter.array_to_text(array = Films)
            SaveFilmArray = open('Films.pkl', 'wb')
            pickle.dump(Films, SaveFilmArray) # Сохраняем массив с фильмами

            await msg.answer('Конечный список:' + film_lst)
        except:
            await msg.answer('Ошибка в удаления фильма')

    else: 
        await msg.answer("К сожалению я вас не понимаю")

# Этот хэндлер будет срабатывать на все остальные сообщения
@dp.message()
async def send_echo(msg: Message):
    await msg.answer("К сожалению я вас не понимаю")

# Логика кнопок меняющие дату стрипа 
def button_delta(action, mode, number, findex, vmark, fav_len, film_len):
    # Это словарь в словаре где, первый ключ это запрос веденый в функцию
    # Второй ключ это режим пользователя
    # А значекие это список из двух элеметнов
    # номер стрипа и индекса списка любимых стрипов
    actions = {
        'first': {'general': (1, findex, vmark), 
                  'favorite': (number, 0, vmark),
                  'video': (number, findex, 0)},
        'previous': {
            'general': (number - delta if number > 1 else number, findex, vmark),
            'favorite': (number, findex - delta if findex > 0 else findex, vmark),
            'video':(number, findex, vmark - delta if vmark > 0 else vmark)
        },
        'random': {
            'general': (random.randint(1, lst_num - 1), findex, vmark),
            'favorite': (number, random.randint(0, fav_len - 1), vmark),
            'video': (number, findex, random.randint(0, film_len - 1))
        },
        'next': {
            'general': (number + delta if number < lst_num else number, findex),
            'favorite': (number, findex + delta if findex < fav_len - 1 else findex),
            'video': (number, findex, vmark + delta if vmark < film_len - 1 else vmark)
        },
        'last': {'general': (lst_num, findex, vmark), 
                 'favorite': (number, fav_len - 1, vmark),
                 'video': (number, findex, film_len -1)}
    }
    
    number, findex, vmark = actions.get(action, {}).get(mode, (number, findex, vmark)) # В случае чего возвращаются изначальные значения 
    return number, findex, vmark

# Логика уведомлений
async def notify(handmade = False, text = ""):
    list_of_users = list(Users.values()) # Достаем список пользователей из словаря
    for user in list_of_users: # Перебираем каждого пользователя в списке 
        if user.sub and user.cur_num < lst_num: # Если он подписан и он остановлися на последнем стрипе
                                                # то высылаем уведомление со следующим стрипы

            # Переходим на следющий стрип и меняем режим на обычный                                   
            user.cur_num += 1 
            strip_number = user.change_mode(new_mode = 'general')

            structural.adapter.url_to_square(url = constants.BASE + '/' + str(strip_number)) # Парсим стрип из акомикса
            request = FSInputFile(constants.RESULT) # Открываем файл 
            issueName = structural.what_num.issueName(url=constants.BASE + '/' +str(strip_number)) # Достаем дату выпуска стрипа который высылается юзер
            
            # Высылаем стрип и уведомление
            await bot.send_message(chat_id= user.id, text = "А вот и ваш стрип!")
            await bot.send_photo( chat_id= user.id, photo = request, reply_markup = user.menu, caption = issueName)

            # Обновляем словарь
            Users.update({user.id: user})

if __name__ == '__main__':
    dp.run_polling(bot)
