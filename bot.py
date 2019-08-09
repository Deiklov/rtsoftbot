import telebot, requests, datetime, sqlite3
import urllib.request
from xml.etree import ElementTree as ET

bot = telebot.TeleBot('983591267:AAHaXYC_hwsHD0V_2imXNwah9FQ7Rga8qMk')


@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, 'Привет, ты написал мне /start')


@bot.message_handler(commands=['register','commands'])
def register(message):
    if message.text=='/register':
        bot.send_message(message.chat.id, 'Введите логин и пароль через пробел')
        bot.register_next_step_handler(message, get_login)
    else:
        bot.send_message(message.chat.id,'1)Enter word, я переведу его')
        bot.send_message(message.chat.id,'2)/register для регистрации или авторизации')
        bot.send_message(message.chat.id, '3) money для текущего курса доллара/евро')
        bot.send_message(message.chat.id, '4) born статистика рождаемости в Москве')
        bot.send_message(message.chat.id,'5) Брать ли мне завтра с собой зонтик?')


def get_login(message):
    # global login
    login = message.text.split()[0]
    password = message.text.split()[1]
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    params = (login, password)
    # cursor.execute('''select name,password from users where password='kkk' and name='Like';''')
    cursor.execute('''select name,password from users where name=? and password=?;''', params)
    result = cursor.fetchall()
    if result == []:
        cursor.execute('''select name from users where  name=?;''', (login,))
        if cursor.fetchall() == []:
            cursor.execute('''insert into users ( name, password) values ( ?, ?);''', params)
            bot.send_message(message.chat.id, 'Спасибо за регистрацию ' + login)
        else:
            bot.send_message(message.chat.id, 'Неверный пароль или логин уже занят')
    else:
        bot.send_message(message.chat.id, 'Привет ' + login)
    conn.commit()
    conn.close()
    # bot.register_next_step_handler(message, check_login)


@bot.message_handler(content_types=['text'])
def send_text(message):
    if message.text.lower() == 'money':
        dollar, euro = valutes()
        bot.send_message(message.chat.id, '1 доллар=' + dollar + 'руб.')
        bot.send_message(message.chat.id, '1 евро=' + euro + 'руб.')
    elif message.text.lower() == 'born':
        for year in data():
            temp = year['Cells']
            bot.send_message(message.chat.id,
                             'Год=' + str(temp['Year']) + ' Мальчиков=' + str(temp['NumberOfBoys']) + ' Девочек=' + str(
                                 temp['NumberOfGirls']))
    elif message.text == 'Брать ли мне завтра с собой зонтик?':
        url='http://api.openweathermap.org/data/2.5/weather?q=Moscow&APPID=78013c5573febd2abe21cbdcd4c75943'
        r=requests.get(url).json()
        description=str(r['weather'][0]['description'])
        rain=description.split()
        for word in rain:
            if word.lower()=='rain':
                bot.send_message(message.chat.id,"Вам следует взять зонт")
                break
        else:
            bot.send_message(message.chat.id, "Дождя не будет")
    else:
        response = translate(message.text, 'ru-en')['text']
        bot.send_message(message.chat.id, response)


def weather():
    bolik = True
    return bolik


def data():
    codedatasets = '2008'
    URL = 'https://apidata.mos.ru/v1/datasets/' + codedatasets + '/rows?api_key=3f7cdb4038b4ea1dd04d2eaba207d424'
    r = eval(requests.get(URL).content)
    return r


def valutes():
    now = datetime.datetime.today().strftime("%m/%d/%Y")
    URL = 'http://www.cbr.ru/scripts/XML_daily.asp?date_req=' + now
    root = ET.parse(urllib.request.urlopen(URL)).getroot()
    dollar = root.findall("./Valute[@ID='R01235']/Value")[0].text
    euro = root.findall("./Valute[@ID='R01239']/Value")[0].text
    return dollar, euro


def translate(text, lang):
    URL = 'https://translate.yandex.net/api/v1.5/tr.json/translate?'
    KEY = 'trnsl.1.1.20190804T184033Z.6f90394bf1ca2818.bb8aef70b4b527f1b3689cd5d97658ea3d7b852b'
    TEXT = text
    LANG = lang
    r = requests.post(URL, data={'key': KEY, 'text': TEXT, 'lang': LANG})
    return eval(r.text)


bot.polling()
