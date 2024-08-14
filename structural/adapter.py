from wand.image import Image
from bs4 import BeautifulSoup
import requests


# Переобразуем ссылку в квадратный стрип 
def url_to_square(url):
    src = find_src(url = url)
    src =  requests.get(src, stream = True).raw # Достаем стрип из ссылки 
    img = Image(file = src)
    if(img.height < 500):
        squared = square(image = img)
    else: # Если высота стрипа больше 500, следовательно это воскресный стрип который не нужно переобразовывать 
         squared = img
    squared.save(filename='request.png') # Сохраняем 

def array_to_text(array, counter = 1):
        film_lst = ''
        for film in array:
            film_lst += '\n' + str(counter) + ') ' + film.name
            counter += 1
        return film_lst

# На вход идет изображение, выход квадратный стрип 
def square(image):
        # По этим параметрам будем резать стрип
        w = int(image.width / 2)
        h = image.height

        # Деламе двух клонов потому что дальше будем резать 
        clone_1 = image.clone()
        clone_2 = image.clone()

        # Находим координаты с которых будет резать первую половину стрипа 
        x,y = upper_left(check=image, x= 0, y=30)

        # Режим стрип начиная с координаты (x,y) шириной равной = w, ну и высытой = h
        clone_1.crop(x,y, width = w, height = h)

        # x присваиваем середину стрипа 
        x = w

        # С середины стрип ищем началу воторой половины стрипа 
        x,y = upper_left(check=image, x= x, y=30)

        # Режим стрип начиная с координаты (x,y) шириной равной = w, ну и высытой = h
        clone_2.crop(x,y, width = w, height = h)
        
        w1 = clone_1.width
        w2 = clone_2.width

        # Считаем конечную ширину и высоту квадратного стрипа 
        w_res = min(w1,w2) # Берем минимальную что бы отсечь лишнее 
        h_res = clone_1.height + clone_2.height

        # Берем контрольную точку по которой будем ложить нижнию часть 
        cntrl_point = h
        
        res = Image(width=w_res +5, height= h_res, background="white") # Создаем "чистое" изображение
        res.composite(image= clone_2, left=5, top= cntrl_point) # Сначала ложим вторую половину стрипа в низ, что бы потом своей верхней белой частью первую половину стрипа
        res.composite(image=clone_1, left=5,top=0) # Затем ложим первую половину стрипа уже в верхнию часть изображения

        return res

def upper_left(check, x,y):

    img_inverted = check.clone() # Делаем клона   
    img_inverted.level(0.6, 0.5, gamma=1) # Инвиртируем его что бы дальше было удобнее искать границы стрипа  

    while(img_inverted[x,y].string<'srgb(250,250,250)'):
            x+=1
    
    y=0 # y=0 потому что так можно избежать ошибок с подписью + при переводе в квдаратный формат параметр "y" не так важен

    return x,y 

# Достаем ссылку на стрип с страницы acomics
def find_src(url):
    # Получаем код страницы 
    page = requests.get(url)
    soup = BeautifulSoup(page.text, "lxml") # Задаем параметры чтения
    src = soup.find(class_='issue').get('src') # Обычнй парсинг по пораметру class_='issue'. Потом достаем атрибут 'src'
    src = 'https://acomics.ru' + src 
    return src # Отправляем ссылку на стрип



