from os import system, getlogin, name, getcwd, listdir, path
from webbrowser import open_new
from datetime import datetime
from difflib import SequenceMatcher
from subprocess import run

try:
    import keyboard
    import pyttsx3
    from speech_recognition import Recognizer, Microphone
    from prettytable import PrettyTable
    from pymorphy2 import MorphAnalyzer
    from pyowm import OWM
    from pyowm.utils.config import get_default_config
    if name == 'nt':
        from winotify import Notification
except ImportError:
    system("pip install -r requirements.txt")


class Recognition():
    def __init__(self):
        self.token_OWM = "1f7d88e16e1906ce2a0ce4be53b020de"
        self.root = Recognizer()
        self.root.pause_threshold = 0.1
        self.engine = pyttsx3.init()
        rate = self.engine.getProperty('rate')
        self.engine.setProperty('rate', rate-20)
        self.engine.runAndWait()
        if name == 'nt':
            self.is_windows = True

    def clear(self):
        if self.is_windows:
            system('cls')
        else:
            system('clear')


class Assistent(Recognition):
    def __init__(self):
        super(Assistent, self).__init__()
        self.engine.say("Cлушаю")
        self.engine.runAndWait()
        self.clear()
        self.commands = {
            ("выключись", "выключение", "закройся", "пока", "удачи"): "Stop",
            "поиск": "Search_Browser",
            "погода": "Search_Weather",
            ("помощь", "просвяти", "объясни", "покажи", "сос"): "Help",
            "музыка": "Music",
            "список": "Printing_Programs",
            ("открой", "приложения"): "Start_Program",
            "браузер": "Open_Browser",
            "интернет": "Open_Browser",
        }
        self.command_runner()

    def command_runner(self):
        while True:
            try:
                with Microphone() as self.mic:
                    self.root.adjust_for_ambient_noise(
                        source=self.mic, duration=1)
                    self.text = self.root.recognize_google(
                        audio_data=self.root.listen(source=self.mic), language='ru-RU').lower()
                    for i in self.commands.keys():
                        if "браузер" in i:
                            globals()[self.commands.get(self.text.split(" ")[0])](
                                arr=self.text.split(" "))
                        '''except:
                            print("Fail 443...")
                            exit()'''
                break
            except:
                pass


class Stop():
    def __init__(self):
        print("Сам закройся...")
        exit()


class Search_Browser(Recognition):
    def __init__(self, platform=None, arr=[]):
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
        open_new(self.google + self.text_search)

    def search_yandex(self):
        print(
            f"Произвожу поиск <{self.text_search}> в Yandex... открываю браузер")
        open_new(self.yandex + self.text_search)

    def search_youtube(self):
        print(
            f"Произвожу поиск <{self.text_search}> в Youtube... открываю браузер")
        open_new(url=self.youtube + self.text_search)

    def input_search(self, platform):
        print(f"Запрос ")
        with Microphone() as self.mic:
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
        with Microphone() as self.mic:
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


class Printing_Programs(Recognition):
    def __init__(self, arr=[], mode="full"):
        super(Printing_Programs, self).__init__()
        self.programs = Find_Programs().programs
        self.clear()
        if mode == "low":
            self.low_mode()
        else:
            self.full_mode()

    def low_mode(self):
        self.clear()
        print(f"\033[32mНайдено {len(self.programs.values())} программ\033[0m")
        print("-"*100)
        count = 0
        for i in self.programs:
            if count == 0 or count == 1:
                print(f"\033[32m{i}\033[0m".ljust(40), end='')
                count += 1
            else:
                print(f"\033[32m{i}\033[0m".ljust(40))
                count = 0

    def full_mode(self):
        self.clear()
        print(f"\033[32mНайдено {len(self.programs.values())} программ\033[0m")
        print("-"*100)
        for i in self.programs:
            print(f"\033[32m{i}\033[0m".ljust(40), end='')
            print(f"{self.programs[i]}".ljust(40))


class Search_Weather(Recognition):
    def __init__(self, city="суходол", arr=["погода"]):
        super(Search_Weather, self).__init__()
        config_dict = get_default_config()
        config_dict['language'] = 'ru'
        self.owm = OWM(self.token_OWM, config=config_dict)
        self.manager = self.owm.weather_manager()
        self.root = Recognizer()
        self.root.pause_threshold = 0.5
        if len(arr) > 1:
            checker = MorphAnalyzer()
            if "в" in arr:
                city_old = arr[2]
            else:
                city_old = arr[1]
            word = checker.parse(city_old)[0]
            city = word.normal_form
        self.now = datetime.now()
        if not self.is_windows:
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
        self.icon_on = getcwd()+'icons/cloud-on.png'
        self.icon_off = getcwd()+'icons/cloud-off.png'
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
    def __init__(self, arr=[]):
        pass


class Help(Recognition):
    def __init__(self, arr=[]):
        super(Help, self).__init__()
        self.clear()
        self.engine.say("Что непонятного в моих командах?")
        self.engine.runAndWait()
        self.title = "λ ~ Список команд"
        print(self.title)
        print(self.constructor())

    def constructor(self):
        self.tabl = PrettyTable()
        self.tabl.field_names = [
            "\033[32mКоманда\033[0m", "\033[32mОписание\033[0m"]
        self.tabl.add_row(
            ["Выключение", "\033[31mВыключение программы\033[0m"])
        self.tabl.add_row(["Закройся", "\033[31mВыключение программы\033[0m"])
        self.tabl.add_row(["Выключись", "\033[31mВыключение программы\033[0m"])
        self.tabl.add_row(["Поиск {\033[32m__\033[0m}",
                          "\033[31mПоиск в интернете\033[0m"])
        self.tabl.add_row(["Погода {\033[32m__\033[0m}",
                          "\033[31mПоиск погоды\033[0m"])
        self.tabl.add_row(["Помощь", "\033[31mПомощь в работе\033[0m"])
        self.tabl.add_row(["Просвяти", "\033[31mПомощь в работе\033[0m"])
        self.tabl.add_row(["Объясни", "\033[31mПомощь в работе\033[0m"])
        self.tabl.add_row(["Покажи", "\033[31mПомощь в работе\033[0m"])
        self.tabl.add_row(["Музыка", "\033[31mОткрыть музыку\033[0m"])
        self.tabl.add_row(["Список программ",
                          "\033[31mВывести список программ\033[0m"])
        self.tabl.add_row(["Приложения", "\033[31mОткрыть программу\033[0m"])
        self.tabl.add_row(["Программы", "\033[31mОткрыть программу\033[0m"])
        self.tabl.add_row(["Браузер", "\033[31mОткрыть браузер\033[0m"])
        self.tabl.add_row(["Интернет", "\033[31mОткрыть браузер\033[0m"])
        self.tabl.align = "l"
        return self.tabl


class Open_Browser():
    def __init__(self):
        print("λ ~ Oткрываю браузер")
        open_new(" ")


class Music(Recognition):
    def __init__(self, arr=[]):
        super(Music, self).__init__()
        self.clear()
        self.sites = {
            "vk": "https://vk.com/audio",
            "вк": "https://vk.com/audio",
            "spotify": "https://open.spotify.com",
            "спотифай": "https://open.spotify.com",
        }
        self.is_vk, self.is_spotify = False, False
        self.path_to_spotify = f"C:\\Users\\{getlogin()}\\AppData\\Roaming\\Spotify\\Spotify.exe"
        self.path_to_vk = f"C:\\Users\\{getlogin()}\\AppData\\Roaming\\VK\\vk.exe"
        self.main()

    def open_programs(self):
        if (self.is_spotify == True) and (self.is_vk == True):
            with Microphone() as self.mic:
                self.root.adjust_for_ambient_noise(source=self.mic, duration=1)
                print("Какую программу открыть? <vk, spotify>", end='')
                while True:
                    try:
                        self.choice_prog = self.root.recognize_google(
                            audio_data=self.root.listen(source=self.mic), language='ru-RU').lower()
                        if ("вк" in self.choice_prog ) or (self.choice_prog == "vk") or ("в к" in self.choice_prog):
                            self.open_vk_music()
                        else:
                            self.open_spotify()
                    except:
                        pass

        elif self.is_spotify == True:
            self.engine.say("открываю спотифай")
            self.engine.runAndWait()
            run([self.path_to_spotify])

        elif self.is_vk == True:
            self.engine.say("открываю вконтакте музыка")
            self.engine.runAndWait()
            run([self.path_to_vk])

        else:
            self.open_sites()

    def open_sites(self):
        with Microphone() as self.mic:
            self.root.adjust_for_ambient_noise(source=self.mic, duration=1)
            print("Какой сайт открыть? <vk, spotify>")
            while True:
                try:
                    self.name = self.root.recognize_google(audio_data=self.root.listen(source=self.mic), language='ru-RU').lower()
                    if self.name in self.sites.keys():
                        print(f"λ ~ Открываю сайт <{self.name.capitilize()}>")
                        open(self.sites[self.name])
                except:
                    pass

    def check_programs(self):
        print(">>> Начинаю поиск программ...")
        for i in listdir(f"C:\\Users\\{getlogin()}\\AppData\\Roaming"):
            if i == "Spotify":
                self.is_spotify = True
            elif i == "VK":
                self.is_vk = True
            else:
                pass

    def print_out(self):
        if self.is_spotify:
            print(">>> \033[32mНайдена программа Spotify\033[0m")
        else:
            print(">>> \033[31mНе найдена программа Spotify\033[0m")
        if self.is_vk:
            print(">>> \033[32mНайдена программа Vk\033[0m")
        else:
            print(">>> \033[31mНе найдена программа Vk\033[0m")

    def main(self):
        print("λ ~ Включение музыки")
        self.check_programs()
        self.print_out()
        self.open_programs()
        return True


class Find_Programs():
    def __init__(self):
        self.programs = {}
        self.main()

    def main(self):
        self.dirs = ["C:\\Program Files\\", f"C:\\Users\\{getlogin()}\\AppData\\Roaming\\", f"C:\\Users\\{getlogin()}\\AppData\\Local\\",
                     'C:\\Program Files (x86)\\', f"C:\\Users\\{getlogin()}\\AppData\\Local\\Programs\\"]
        for dir in self.dirs:
            self.search_progs(dir)

    def search_progs(self, dir, name=None):
        if name != None:
            if not path.isfile(dir):
                try:
                    for i in listdir(dir+"\\"):
                        if path.isfile(dir+"\\"+i):
                            if (i in ["launcher.exe", name.lower()+".exe", name.capitalize()+".exe", name+".exe"]) or (self.similary(name, i.strip(".exe")) > 0.50):
                                self.programs[name] = dir+"\\"+name+".exe"
                except PermissionError:
                    pass
        else:
            if ".ini" not in dir:
                for i in listdir(dir):
                    self.search_progs(dir+i, i)

    def similary(self, dir, exe):
        return SequenceMatcher(None, dir.lower(), exe.lower()).ratio()


class OpenProgramError(FileNotFoundError):
    def __init__(self, txt):
        self.txt = txt


class Start_Program(Recognition):
    def __init__(self, name=''):
        super(Start_Program, self).__init__()
        Printing_Programs()
        self.name = input("λ ~ Введите приложение: ")
        self.programs = Find_Programs().programs
        self.start(self.name)

    def start(self, name):
        for i in self.programs.keys():
            if name.lower() in i.lower():
                try:
                    if run(self.programs[i]).returncode != 0:
                        assert OpenProgramError(
                            "λ ~ Ошибка при открытие программы")
                except OpenProgramError as e:
                    print(e)
                except FileNotFoundError as e:
                    print(e)


if __name__ == '__main__':
    '''keyboard.add_hotkey("Ctrl+K", Assistent)
    keyboard.wait()'''
    Search_Weather(city="ташкент")
    