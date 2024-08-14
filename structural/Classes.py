import constants
import structural.what_num
from aiogram.types import *
lst_num = structural.what_num.issueNumber(url = constants.BASE)

class User:
    # Генерация клавиатуры 

    # Первый ряд кнопок 
    fisrt_bt = InlineKeyboardButton(text='⏪', callback_data= 'first delta',)
    previous_bt = InlineKeyboardButton(text='◀️', callback_data= 'previous delta')
    random_bt = InlineKeyboardButton(text='🔄', callback_data= 'random delta')
    next_bt = InlineKeyboardButton(text='▶️', callback_data= 'next delta')
    last_bt = InlineKeyboardButton(text='⏩', callback_data= 'last delta')

    # Второй ряд кнопок 
    add_favorite = InlineKeyboardButton(text='❤️', callback_data= 'add favorite')
    remove_favorite = InlineKeyboardButton(text='💔', callback_data= 'remove favorite')
    favorite_mode = InlineKeyboardButton(text='💕', callback_data= 'favorite mode')
    general_mode = InlineKeyboardButton(text='📖', callback_data= 'general mode')
    video_mode = InlineKeyboardButton(text='🎥', callback_data= 'video mode')

    # Кнопки для видео режима

    # Два вида клавиатур один для обычного режима второй для избранного 
    menu_general = [ 
        [fisrt_bt, previous_bt, random_bt, next_bt, last_bt],
        [add_favorite, favorite_mode, remove_favorite, video_mode] 
    ]
    menu_favorite = [ 
        [fisrt_bt, previous_bt, random_bt, next_bt, last_bt],
        [add_favorite, general_mode, remove_favorite, video_mode] 
    ] 

    menu_video =[[fisrt_bt, previous_bt, random_bt, next_bt, last_bt],
                 [general_mode, favorite_mode]] 
    
    def __init__(self, id, status = 'general'):
        self.id = id
        self.cur_num = lst_num
        self.mode = 'general'
        self.favorite_list = [101]
        self.cur_index = 0
        self.vmark = 0
        self.status = status
        self.sub = False
        self.menu = InlineKeyboardMarkup(inline_keyboard = User.menu_general)
        

    def change_mode(self, new_mode):
        self.cur_index = 0 # сбрасываем параметр потому что список любимых стрипов динамичен
        
        modes = {
        'general': [User.menu_general, self.cur_num],
        'favorite': [User.menu_favorite, self.favorite_list[self.cur_index]],
        'video': [User.menu_video, self.vmark]
        }

        mode = new_mode.split(" ")
        self.mode = mode[0]

        keyboard, content = modes.get(self.mode)

        self.menu = InlineKeyboardMarkup(inline_keyboard = keyboard)
        return content

class Film:
    def __init__(self, name = 'null', img_id = 'null', video_id = 'null'):
        self.name = name 
        self.video = video_id