import speech_recognition as sr
import webbrowser
from pyowm import OWM
from pyowm.utils.config import get_default_config
import os
import pyttsx3
from datetime import datetime

class Recognition():
    def __init__(self):
        self.root = sr.Recognizer()
        self.root.pause_threshold = 0.5
        self.engine = pyttsx3.init()
        rate = self.engine.getProperty('rate')
        self.engine.setProperty('rate', rate-5)
        self.engine.runAndWait()
    
    def clear(self):
        if os.name == 'nt':
            os.system('cls')
        else:
            os.system('clear')

class Assistent(Recognition):
    def __init__(self):
        super(Assistent, self).__init__()
        self.is_windows = False
        if os.name == "nt":
            self.is_windows = True
            from winotify import Notification
        self.command_runner()

    def command_runner(self):
        while True:
            try:
                with sr.Microphone() as self.mic:
                    self.root.adjust_for_ambient_noise(source=self.mic, duration=1)
                    self.audio = self.root.listen(source=self.mic)
                    text = self.root.recognize_google(audio_data=self.audio, language='ru-RU').lower()
                    text_new = text.replace(" точка", ".")
                    self.text_end = text_new.replace(" запятая", ",")

                    if self.text_end == "выключение" or self.text_end == "выключись":
                        self.engine.say("Выключаюсь")
                        self.engine.runAndWait()
                        print(f"\nλ ~ Выключаюсь")
                        exit()

                    elif "погода" in self.text_end:
                        if self.text_end == "погода":
                            print(f"\nλ ~ Погода Суходол")
                            Search_Weather()
                        else:
                            self.city = text.rsplit()[1]
                            print(f"\nλ ~ Погода {self.city.capitalize()}")
                            Search_Weather(city=self.city)
                        
                    elif "поиск в интернете" in self.text_end:
                        print('\nλ ~ Поиск в браузере')
                        Search_Browser()
            except:
                pass


class Search_Browser(Recognition):
    def __init__(self):
        super(Search_Browser, self).__init__() 
        self.yandex = "https://yandex.ru/search/?text="
        self.youtube = "https://youtube.com/results?search_query="
        self.google = "https://google.ru/search?q="
        self.input_platform()

    def search_google(self):
        print("Произвожу поиск в Google... открываю браузер")
        webbrowser.open_new(self.google + self.text_search)
        print("Готово")

    def search_yandex(self):
        print("Произвожу поиск в Yandex... открываю браузер")
        webbrowser.open_new(self.yandex + self.text_search)
        print("Готово")

    def search_youtube(self):
        print("Произвожу поиск в Youtube... открываю браузер")
        webbrowser.open_new(url=self.youtube + self.text_search)
        print("Готово")

    def input_search(self, platform):
        print("~Запрос~ ",)
        with sr.Microphone() as self.mic:
            self.root.adjust_for_ambient_noise(source=self.mic, duration=1)
            count = 0 
            while True:
                try:
                    self.search_audio = self.root.listen(source=self.mic)
                    self.text_search = self.root.recognize_google(audio_data=self.search_audio, language='ru-RU').lower()
                    print(f"\nПровожу поиск в {platform}.\nЗапрос: {self.text_search}")
                    if platform == ("google" or "гугл"):
                        self.search_google()
                    elif platform == ("яндекс" or "yandex"):
                        self.search_yandex()
                    elif platform == ("youtube" or "ютуб"):
                        self.search_youtube()
                    break
                except:
                    if count == 3:
                        print("Не расслышал запрос")
                    else:
                        count += 1 


    def input_platform(self):
        with sr.Microphone() as self.mic:
            self.root.adjust_for_ambient_noise(source=self.mic, duration=1)
            print("Где искать?(google, youtube, yandex)")
            count = 0
            while True:
                try:
                    self.audio = self.root.listen(source=self.mic)
                    self.platform = self.root.recognize_google(audio_data=self.audio, language='ru-RU').lower()
                    if self.platform in ["google", "yandex", "youtube", "гугл", "яндекс", "ютуб"]:
                        self.input_search(self.platform)
                        break
                except sr.UnknownValueError:
                    if count == 3:
                        count = 0
                        print("Повторите запрос")
                    else:
                        count += 1


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
            self.title = f'Погода {city.capitalize()}'
            self.message_notif = f"Температура ~ {self.t1} °C\nОщущения ~ {self.t2} °C\nСкорость ветра ~ {self.wi} м/c\nПогода ~ {self.dt}\nВлажность ~ {self.humi}%"
            print("-"*60, f"\n{self.title}\nТекущее время ~ {self.now.hour}:{self.now.minute}\n{self.message_notif}\n", "-"*60)
        except:
            self.msg_error = "Погода не найдена, повторите запрос."
            print("-"*60, f"\n{self.msg_error}\n", "-"*60)
            self.engine.say("Погода не найдена")
            self.engine.runAndWait()

    def get_weather_city_windows(self, city):
        self.icon_on = os.getcwd()+'files/cloud-on.png'
        self.icon_off = os.getcwd()+'files/cloud-off.png'
        try:
            self.weather_all = self.manager.weather_at_place(city).weather
            self.get_weather_param(self.weather_all)
            self.title = f'Погода {city.capitalize()}'
            self.message_notif = f"Температура ~ {self.t1} °C\nСкорость ветра ~ {self.wi} м/c\nПогода ~ {self.dt}"
            self.toaster = Notification(app_id="Погода", title=self.title, msg=self.message_notif, icon=self.icon_on) 
            self.toaster.show()
            self.engine.say("Готово")
            self.engine.runAndWait()
        except:
            self.title_error = "Погода"
            self.msg_error = "Погода не найдена, повторите запрос."
            self.toaster = Notification(app_id="Погода", title=self.title_error, msg=self.msg_error, icon=self.icon_off)
            self.toaster.show()
            self.engine.say("Погода не найдена")
            self.engine.runAndWait()
        
    def get_weather_param(self, we):
        self.t = we.temperature("celsius")
        self.t1 = self.t['temp'] # ~ температура
        self.t2 = self.t['feels_like'] # ~ ощущения
        self.t3 = self.t['temp_max'] # ~ максимальная температура
        self.t4 = self.t['temp_min'] # ~ минимальная температура
        self.wi = we.wind()['speed'] # ~ скорость ветра
        self.humi = we.humidity # ~ влажность
        self.cl = we.clouds # ~ облачность
        self.st = we.status # ~ статус погоды
        self.dt = we.detailed_status # ~ детальная погода
        self.pr = we.pressure['press'] # ~ давление
        self.vd = we.visibility_distance # ~ видимость



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
    main.run()