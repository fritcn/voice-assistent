from time import sleep
from pymorphy2 import MorphAnalyzer
from prettytable import PrettyTable
import speech_recognition as sr
import webbrowser
from pyowm import OWM
from pyowm.utils.config import get_default_config
import os
import pyttsx3
from datetime import datetime
import keyboard
import winapps
if os.name == 'nt':
    from winotify import Notification


class Recognition():
    def __init__(self):
        self.root = sr.Recognizer()
        self.root.pause_threshold = 0.5
        self.engine = pyttsx3.init()
        rate = self.engine.getProperty('rate')
        self.engine.setProperty('rate', rate-20)
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
        self.engine.say("Cлушаю")
        self.engine.runAndWait()
        self.clear()
        self.commands = {
            "выключись": "Stop",
            "выключение": "Stop",
            "закройся": "Stop",
            "поиск": "Search_Browser",
            "поиск в интернете": "Search_Browser",
            "погода": "Search_Weather",
            "помощь": "Help",
            "просвяти": "Help",
            "объясни": "Help",
            "покажи": "Help",
            "музыка": "Music"
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
                    elif "поиск" in self.text:
                        self.handler(self.text, is_search=True)
                break
            except:
                pass

    def handler(self, message, is_weather=False, is_search=False):
        if is_weather:
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

        elif is_search:
            if " в " in message:
                checker = MorphAnalyzer()
                spliting = message.split(" в ")
                word = checker.parse(spliting[1])[0]
                self.platform = word.normal_form
                print(f"λ ~ поиск {self.platform}")
                self.engine.say(f"поиск {self.platform}")
                self.item = self.commands.get(spliting[0])
                globals()[self.item](self.platform)

            else:
                spliting = message.split(" ")
                self.platform = spliting[1]
                print(f"λ ~ поиск {self.platform}")
                self.engine.say(f"поиск {self.platform}")
                self.item = self.commands.get(spliting[0])
                globals()[self.item](self.platform)

        else:
            print("λ ~ ", message)
            try:
                self.item = self.commands.get(message)
                globals()[self.item]()
            except:
                print("Неудача")
                os.abort()


class Stop():
    def __init__(self):
        print("Сам закройся...")
        os.abort()


class Search_Browser(Recognition):
    def __init__(self, platform=None):
        super(Search_Browser, self).__init__()
        self.yandex = "https://yandex.ru/search/?text="
        self.youtube = "https://youtube.com/results?search_query="
        self.google = "https://google.ru/search?q="
        if platform == None:
            self.input_platform()
        else:
            self.platform = platform
            self.input_search(self.platform)

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
                    self.platform = self.root.recognize_google(audio_data=self.root.listen(source=self.mic), language='ru-RU').lower()
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
        if self.is_windows:
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
        self.icon_on = os.getcwd()+'icons/cloud-on.png'
        self.icon_off = os.getcwd()+'icons/cloud-off.png'
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


class Help(Recognition):
    def __init__(self):
        super(Help, self).__init__()
        self.clear()
        self.engine.say("Что непонятного в моих командах?")
        self.engine.runAndWait()
        self.title = "λ ~ Список команд"
        print(self.title)
        print(self.constructor())
            
    def constructor(self):
        self.tabl = PrettyTable()
        self.tabl.field_names = ["\033[32mКоманда\033[0m", "\033[32mОписание\033[0m"]
        self.tabl.add_row(["Выключение", "\033[31mВыключение программы\033[0m"])
        self.tabl.add_row(["Закройся", "\033[31mВыключение программы\033[0m"])
        self.tabl.add_row(["Выключись", "\033[31mВыключение программы\033[0m"])
        self.tabl.add_row(["Поиск {...}", "\033[31mПоиск в интернете\033[0m"])
        self.tabl.add_row(["Погода {...}", "\033[31mПоиск погоды\033[0m"])
        self.tabl.add_row(["Помощь", "\033[31mПомощь в работе\033[0m"])
        self.tabl.add_row(["Просвяти", "\033[31mПомощь в работе\033[0m"])
        self.tabl.add_row(["Объясни", "\033[31mПомощь в работе\033[0m"])
        self.tabl.add_row(["Покажи", "\033[31mПомощь в работе\033[0m"])
        self.tabl.add_row(["Музыка", "\033[31mОткрыть музыку\033[0m"])
        return self.tabl


class Music(Recognition):
    def __init__(self):
        super(Music, self).__init__()
        self.clear()
        self.sites = {
            "vk": "https://vk.com/audio",
            "вк": "https://vk.com/audio",
            "spotify": "https://open.spotify.com",
            "спотифай": "https://open.spotify.com",
        }
        print("λ ~ Включение музыки")
        self.path_to_spotify = f"C:\\Users\\{os.getlogin()}\\AppData\\Roaming\\Spotify\\Spotify.exe"
        self.path_to_vk = f"C:\\Users\\{os.getlogin()}\\AppData\\Roaming\\VK\\vk.exe"
        self.check_programs()
        if (self.spotify_en == True) and (self.vk_en == True):
            self.two_programs()
        elif self.spotify_en == True:
            self.open_spotify()
        elif self.vk_en == True:
            self.open_vk_music()
        else:
            self.open_sites()

    def open_spotify(self):
        self.engine.say("открываю спотифай")
        self.engine.runAndWait()
        os.system(f"start {self.path_to_spotify}")
        
    def open_vk_music(self):
        self.engine.say("открываю вконтакте музыка")
        self.engine.runAndWait()
        os.system(f"start {self.path_to_vk}")

    def two_programs(self):
        with sr.Microphone() as self.mic:
            self.root.adjust_for_ambient_noise(source=self.mic, duration=1)
            print("Какую программу открыть? <vk, spotify>")
            while True:
                try:
                    self.choice_prog = self.root.recognize_google(audio_data=self.root.listen(source=self.mic), language='ru-RU').lower()
                    if (self.choice_prog == "вк") or (self.choice_prog == "vk"):
                        self.open_vk_music()
                    else:
                        self.open_spotify()
                except:
                    pass

    def open_sites(self):
        with sr.Microphone() as self.mic:
            self.root.adjust_for_ambient_noise(source=self.mic, duration=1)
            print("Какой сайт открыть? <vk, spotify>")
            while True:
                try:
                    self.name = self.root.recognize_google(audio_data=self.root.listen(source=self.mic), language='ru-RU').lower()
                    if self.name in self.sites.keys():
                        print(f"λ ~ Открываю сайт <{self.name.capitilize()}>")
                        webbrowser.open(self.sites[self.name])
                except:
                    pass

    def check_programs(self):
        print(">>> Начинаю поиск программ...")
        for i in os.listdir(f"C:\\Users\\{os.getlogin()}\\AppData\\Roaming"):
            if "Spotify" in i:
                self.spotify_en = True
                print(">>> \033[32mНайдена программа Spotify\033[0m")
            elif "VK" in i:
                self.vk_en = True
        if self.vk_en == True:
            print(">>> \033[32mНайдена программа Vk\033[0m")
        if self.spotify_en == False and self.vk_en == False:
            print(">>> \033[31m Не найдено программ для включения музыки\033[0m")
        print()



if __name__ == '__main__':
    keyboard.add_hotkey("Ctrl+Shift+F", Assistent)
    keyboard.wait()