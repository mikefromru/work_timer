#!/usr/bin/env python3.8
import os, sys
os.chdir(os.path.dirname(os.path.realpath(__file__)))
home = os.path.expanduser('~')
script_directory = os.path.dirname(os.path.abspath(__file__))
sys.path.append(home + '/bin/notify_work/env/lib/python3.8/site-packages')
#print(sys.path)

from icecream import ic

from kivymd.app import MDApp
import time

from kivy.core.audio import SoundLoader

######## uix
from kivy.uix.screenmanager import ScreenManager, Screen
from kivymd.uix.list import  TwoLineAvatarIconListItem
from kivymd.uix.snackbar import Snackbar
from kivy.uix.screenmanager import (
    NoTransition,
    FadeTransition,
    SlideTransition,
    CardTransition,
    SwapTransition,
    WipeTransition,
    FallOutTransition,
    RiseInTransition
)


from kivymd.uix.dialog import MDDialog
from kivy.uix.boxlayout import BoxLayout
from kivymd.uix.button import MDFlatButton

from kivy.properties import NumericProperty, StringProperty, BooleanProperty

from kivy.clock import Clock

from kivy.storage.jsonstore import JsonStore
from kivy.config import Config
from kivy.core.window import Window
from kivy.lang import Builder

Window.size = (400, 750)
Window.top = 100
Window.right = 10

from pydub import AudioSegment
from pydub.playback import play

class WindowManager(ScreenManager):

    pass

class DetailScreen(Screen):
    
    name_ = StringProperty()
    timer = NumericProperty()
    start = False
    one_hour = 0
    
    def __init__(self, **kwargs):
        super(DetailScreen, self).__init__(**kwargs)
        Window.bind(on_keyboard=self.close_escape) # by ESC
        App.get_running_app().bind(on_stop=self.on_stop_) # by a plus of window
        self.config = App.get_running_app().config

    def on_enter(self):

        self.sound_config = self.config.get('Settings', 'sound')

        self.ids.name_project.title = self.name_.capitalize()
        self.store = JsonStore("store.json")
        self.name_json = self.store.get(self.name_)

        try:
            self.sound = SoundLoader.load('sounds/tinkalink2.wav')
        except:
            pass

    def start_button(self):
        if self.start == False:
            self.even = Clock.schedule_interval(self.run, 1)
            self.start = True
        elif self.start:
            self.ids.start.text = 'start' if self.ids.start.text != 'start' else 'pause'

        if self.ids.start.text == 'pause':
            self.even.cancel()
        else:
            self.even()

    def run(self, i):
        self.timer += 1
        self.ids.timer.text = time.strftime('%H:%M:%S', time.gmtime(self.timer))

        if self.sound_config == 'True':
            self.one_hour += 1
            if self.one_hour == 3600:
                try:
                    self.sound = SoundLoader.load('sounds/tinkalink2.wav')
                except:
                    pass

                if self.sound:
                    self.sound.play()
                    self.one_hour = 0
               
    def go_back(self):
        self.put_to_json(self)
        self.manager.current = 'main_screen'

    def on_leave(self, *args):
        self.start = False
        try:
            if self.even:
                self.even.cancel()
        except:
            pass
        self.sound.stop()
        self.ids.timer.text = '00:00:00'
        self.ids.start.text = 'start'
        self.ids.name_project.title = ''
        self.timer = 0
        self.one_hour = 0

    def close_escape(self, window, key, *args):
        if key == 27:
            self.put_to_json(self)
            os.sys.exit()

    def on_stop_(self, *args):
        self.put_to_json(self)

    def put_to_json(self, *args):
        if self.name_:
            self.store = JsonStore("store.json")
            self.name_json = self.store.get(self.name_)
            time_from_json = self.name_json.get('time')
            total = time_from_json + self.timer
            self.store.put(self.name_, time=total)


class Content(BoxLayout):

    pass

class TwoLineAvatarIconListItemCustom(TwoLineAvatarIconListItem):
    
    def delete(self, insta):
        store = JsonStore('store.json')
        name = self.text
        store.delete(self.text.lower())
        self.parent.remove_widget(self)

class AddScreen(Screen):
        
    def add(self):
        store = JsonStore('store.json')
        name = self.ids.name.text
        name = name.lower()
        try:
            store.get(name)
            Snackbar(text='You have it already').open()
        except:
            store.put(name, time=0)
            self.manager.current = 'main_screen'
    
    def on_leave(self, *args):
        self.ids.name.text = ''

class SettingsScreen(Screen):

    active_sound = BooleanProperty()
    active_theme = BooleanProperty()

    def __init__(self, **kwargs):
        super(SettingsScreen, self).__init__(**kwargs) 
        self.config = App.get_running_app().config

        theme = self.config.get('Settings', 'theme')
        sound = self.config.get('Settings', 'sound')
        
        if sound == 'True':
            self.active_sound = True
        else:
            self.active_sound = False

        if theme == 'Dark':
            self.active_theme = True
        else:
            self.active_theme = False
    
    def sound(self, insta, value):
        if value == False:
            self.config.set('Settings', 'sound', False)
        else:
            self.config.set('Settings', 'sound', True)

        self.config.write()

    def theme(self, insta, value):
        if value == False:
            self.config.set('Settings', 'theme', 'Light')
            App.get_running_app().theme_cls.theme_style = 'Light'
        else:
            self.config.set('Settings', 'theme', 'Dark')
            App.get_running_app().theme_cls.theme_style = 'Dark'

        self.config.write()
        
class MainScreen(Screen):

    dialog = None

    def __init__(self, **kwargs):
        super(MainScreen, self).__init__(**kwargs)
        Clock.schedule_once(self.get_it, 1)

    def on_enter(self, *args):
        try:
            self.ids.container.clear_widgets()
            self.get_it(self) 
        except:
            pass

    def get_it(self, i):
        self.store = JsonStore('store.json')
        for x in self.store:
            time_ = self.store.get(x).get('time')
            var = time.gmtime(time_)
            time__ = time.strftime('%H:%M:%S', var)

            self.ids.container.add_widget(
                TwoLineAvatarIconListItemCustom(text=f"{x.capitalize()}", 
                    secondary_text=str(time__), 
                    on_press=self.callback_1,
                )
            )

    def callback_0(self, instance):
        self.manager.current = 'add_screen'

    def settings(self):
        self.manager.current = 'settings_screen'

    def callback_1(self, instance):
        DetailScreen.name_ = instance.text.lower()
        self.manager.current = 'detail_screen'
 
class App(MDApp):
    
    templates = (
        'templates/index.kv',    
    )

    def build(self):
        config = self.config
        theme = config.get('Settings', 'theme')
        ic(theme)
        App.get_running_app().theme_cls.primary_palette = 'Purple'
        App.get_running_app().theme_cls.theme_style = theme
        for x in self.templates:
            root = Builder.load_file(x)
        self.window_manager = WindowManager(transition=SlideTransition(duration=.2))
        return self.window_manager
     
    def on_stop(self, *args):
        os.sys.exit()
    
    def build_config(self, config):
        self.config.setdefaults('Settings', 
        {
            'theme': 'Light',
            'sound': False
        })
    
    def go_back(self):
        App.get_running_app().window_manager.current = 'main_screen'

App().run()
