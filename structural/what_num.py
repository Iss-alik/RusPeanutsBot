import datetime
from bs4 import BeautifulSoup
import requests


# Переводим файл с искюлечниями в лист
my_file = open("exceptions.txt", "r") 
data = my_file.read() 
hasnt = data.split("\n") 
my_file.close() 

first_strip = datetime.datetime(1950,10,2) # Дата первого стрипа
final_exception = datetime.datetime(1951, 12, 30) # После этой даты больше нету исключений 

# Достаем кол-во дней от первога стрипа + 1 потому что нумерация стрипов начинается с одного. 
# То есть, если к примеру Cur_date = initial date => num = 0, а так нельзя
# Еще нужно учесть исключения итоговая формула: num = cur_date - first_strip - exception + 1 
def num_of_date(cur_date):
    exception = num_of_exceptions(cur_date)
    num = cur_date - first_strip - exception 
    num = str(num).split(' ')
    num = int(num[0]) + 1   # +1 пишем здесь что бы не мучится с переводом в тип datatime
    return num

# Подсчет количества исключений 
def num_of_exceptions(cur_date):
    if(cur_date > final_exception):
        num_of_exceptions = 65
    else:
        # Смотрим какой день недели, затем если не воксресенье доводим до последнего воскресенья  
        x = int(cur_date.strftime('%w'))
        if x != 0:
            delta = datetime.timedelta(days = x)
            cur_date -= delta
        num_of_exceptions = bin_search(find = cur_date.strftime("%Y-%m-%d")) + 1
    
    return datetime.timedelta(days = num_of_exceptions)

# Простой бин поиск по листу с датами исключений 
def bin_search(list = hasnt, find = 0):
    l = 0
    h = len(list)
    m = (l+h)//2
    while(l<=h and list[m] != find):

        if(list[m] < find):
            l = m+1
            m = (l+h)//2
        else:
            h = m-1
            m = (l+h)//2
    return m

# Парсим номер выпуска через выданую сылку 
def issueNumber(url):
    # Получаем код страницы 
    page = requests.get(url)
    soup = BeautifulSoup(page.text, "lxml") # Задаем параметры чтения 
    issueNumber = soup.find(class_='number').string # Обычнй парсинг по пораметру class_='number'
    num = issueNumber.split('/') # Делаем split('/') потому что issueNumber выдается в формате CurrentNumber/TotalNumber
    return int(num[0])

# Анологично приведущему парсим issueName выпуска, что посути дата выпуска, через выданую сылку 
def issueName(url):
    page = requests.get(url)
    soup = BeautifulSoup(page.text, "lxml")
    issueName = soup.find(class_='number-with-name').get_text()
    issueName = issueName[0:10]
    return issueName
