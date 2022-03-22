from pymorphy2 import MorphAnalyzer
import speech_recognition as sr
import webbrowser
from pyowm import OWM
from pyowm.utils.config import get_default_config
import os
import pyttsx3
from datetime import datetime
if os.name == 'nt':
    from winotify import Notification


class Recognition():
    def __init__(self):
        self.root = sr.Recognizer()
        self.root.pause_threshold = 0.5
        self.engine = pyttsx3.init()
        rate = self.engine.getProperty('rate')
        self.engine.setProperty('rate', rate-5)
        self.engine.runAndWait()
        if os.name == 'nt':
            self.is_windows = True

    def clear(self):
        if self.is_windows:
            os.system('cls')
        else:
            os.system('clear')


class Assistent(Recognition):
    def __init__(self):
        super(Assistent, self).__init__()
        self.clear()
        self.commands = {
            "выключись": "Stop",
            "выключение": "Stop",
            "закройся": "Stop",
            "поиск": "Search_Browser",
            "поиск в интернете": "Search_Browser",
            "погода": "Search_Weather",
        }
        self.commands_list = self.commands.keys()
        self.command_runner()

    def command_runner(self):
        while True:
            try:
                with sr.Microphone() as self.mic:
                    self.root.adjust_for_ambient_noise(
                        source=self.mic, duration=1)
                    self.text = self.root.recognize_google(
                        audio_data=self.root.listen(source=self.mic), language='ru-RU').lower()
                    if self.text in self.commands_list:
                        self.handler(self.text)
                    elif "погода" in self.text:
                        self.handler(self.text, is_weather=True)
            except:
                pass

    def handler(self, message, is_weather=False):
        if not is_weather:
            print("λ ~ ", message)
            try:
                self.item = self.commands.get(message)
                globals()[self.item]()
            except:
                os.abort()
        else:
            if " в " in message:
                checker = MorphAnalyzer()
                spliting = message.split(" в ")
                word = checker.parse(spliting[1])[0]
                self.city = word.normal_form
                print(f"λ ~ Погода {self.city.capitalize()}")
                self.engine.say(f"погода {self.city}")
                self.item = self.commands.get(spliting[0])
                globals()[self.item](self.city)

            else:
                spliting = message.split(" ")
                self.city = spliting[1]
                print(f"λ ~ Погода {self.city.capitalize()}")
                self.engine.say(f"погода {self.city}")
                self.item = self.commands.get(spliting[0])
                globals()[self.item](self.city)


class Stop():
    def __init__(self):
        print("Good bye...")
        os.abort()


class Search_Browser(Recognition):
    def __init__(self):
        super(Search_Browser, self).__init__()
        self.yandex = "https://yandex.ru/search/?text="
        self.youtube = "https://youtube.com/results?search_query="
        self.google = "https://google.ru/search?q="
        self.input_platform()

    def search_google(self):
        print(
            f"Произвожу поиск <{self.text_search}> в Google... открываю браузер")
        webbrowser.open_new(self.google + self.text_search)

    def search_yandex(self):
        print(
            f"Произвожу поиск <{self.text_search}> в Yandex... открываю браузер")
        webbrowser.open_new(self.yandex + self.text_search)

    def search_youtube(self):
        print(
            f"Произвожу поиск <{self.text_search}> в Youtube... открываю браузер")
        webbrowser.open_new(url=self.youtube + self.text_search)

    def input_search(self, platform):
        print(f"Запрос ")
        with sr.Microphone() as self.mic:
            self.root.adjust_for_ambient_noise(source=self.mic, duration=1)
            while True:
                try:
                    self.text_search = self.root.recognize_google(
                        audio_data=self.root.listen(source=self.mic), language='ru-RU').lower()

                    if platform == ("google" or "гугл"):
                        self.search_google()
                    elif platform == ("яндекс" or "yandex"):
                        self.search_yandex()
                    elif platform == ("youtube" or "ютуб"):
                        self.search_youtube()
                    break
                except:
                    pass

    def input_platform(self):
        with sr.Microphone() as self.mic:
            self.root.adjust_for_ambient_noise(source=self.mic, duration=1)
            print("Где искать?(google, youtube, yandex)")
            while True:
                try:
                    self.platform = self.root.recognize_google(
                        audio_data=self.root.listen(source=self.mic), language='ru-RU').lower()
                    if self.platform in ["google", "yandex", "youtube", "гугл", "яндекс", "ютуб"]:
                        self.input_search(self.platform)
                        break
                except:
                    pass


class Search_Weather(Recognition):
    def __init__(self, city="суходол"):
        super(Search_Weather, self).__init__()
        config_dict = get_default_config()
        config_dict['language'] = 'ru'
        self.owm = OWM('1f7d88e16e1906ce2a0ce4be53b020de', config=config_dict)
        self.manager = self.owm.weather_manager()
        self.root = sr.Recognizer()
        self.root.pause_threshold = 0.5
        self.now = datetime.now()
        if os.name == 'nt':
            self.get_weather_city_windows(city)
        else:
            self.get_weather_city_linux(city)

    def get_weather_city_linux(self, city):
        try:
            self.weather_all = self.manager.weather_at_place(city).weather
            self.get_weather_param(self.weather_all)
            self.title = f'λ ~ Погода {city.capitalize()}'
            self.message_notif = f"Температура ~ {self.t1} °C\nОщущения ~ {self.t2} °C\nСкорость ветра ~ {self.wi} м/c\nПогода ~ {self.dt}\nВлажность ~ {self.humi}%"
            print(
                "-"*60, f"\n{self.title}\nТекущее время ~ {self.now.hour}:{self.now.minute}\n{self.message_notif}\n", "-"*60)
        except:
            self.msg_error = "λ ~ Погода не найдена, повторите запрос."
            print("-"*60, f"\n{self.msg_error}\n", "-"*60)
            self.engine.say("Погода не найдена")
            self.engine.runAndWait()

    def get_weather_city_windows(self, city):
        self.icon_on = os.getcwd()+'files/cloud-on.png'
        self.icon_off = os.getcwd()+'files/cloud-off.png'
        try:
            self.weather_all = self.manager.weather_at_place(city).weather
            self.get_weather_param(self.weather_all)
            self.title = f'λ ~ Погода {city.capitalize()}'
            self.message_notif = f"Температура ~ {self.t1} °C\nСкорость ветра ~ {self.wi} м/c\nПогода ~ {self.dt}"
            self.toaster = Notification(
                app_id="Погода", title=self.title, msg=self.message_notif, icon=self.icon_on)
            self.toaster.show()
            self.engine.say("Готово")
            self.engine.runAndWait()
        except:
            self.title_error = "λ ~ Погода"
            self.msg_error = "Погода не найдена, повторите запрос."
            self.toaster = Notification(
                app_id="Погода", title=self.title_error, msg=self.msg_error, icon=self.icon_off)
            self.toaster.show()
            self.engine.say("Погода не найдена")
            self.engine.runAndWait()

    def get_weather_param(self, we):
        self.t = we.temperature("celsius")
        self.t1 = self.t['temp']  # ~ температура
        self.t2 = self.t['feels_like']  # ~ ощущения
        self.t3 = self.t['temp_max']  # ~ максимальная температура
        self.t4 = self.t['temp_min']  # ~ минимальная температура
        self.wi = we.wind()['speed']  # ~ скорость ветра
        self.humi = we.humidity  # ~ влажность
        self.cl = we.clouds  # ~ облачность
        self.st = we.status  # ~ статус погоды
        self.dt = we.detailed_status  # ~ детальная погода
        self.pr = we.pressure['press']  # ~ давление
        self.vd = we.visibility_distance  # ~ видимость


class OpenProgram():
    def __init__(self):
        pass


class NewFilms():
    def __init__(self, param):
        # param --> [ film, serial, mults ]
        self.parametr = param
        self.engine = pyttsx3.init()
        self.engine.runAndWait()
        self.url_films = ''
        self.url_serial = ''
        self.url_mults = ''
        if self.parametr == "mults":
            self.engine('Открываю новинки мультфильмов')
            self.open_mults()
        elif self.parametr == 'serial':
            self.engine('Открываю новинки сериалов')
            self.open_serials()
        elif self.parametr == 'films':
            self.engine('Открываю новинки фильмов')
            self.open_films()

    def open_films(self):
        webbrowser.open(self.url_films)

    def open_serials(self):
        webbrowser.open(self.url_serial)

    def open_mults(self):
        webbrowser.open(self.url_mults)


if __name__ == '__main__':
    main = Assistent()