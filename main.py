#!/usr/bin/env python3.8
import os, sys
os.chdir(os.path.dirname(os.path.realpath(__file__)))
home = os.path.expanduser('~')
script_directory = os.path.dirname(os.path.abspath(__file__))
sys.path.append(home + '/bin/env/lib/python3.8/site-packages')
#print(sys.path)

from kivymd.app import MDApp
import time

from kivy.core.audio import SoundLoader

######## uix
from kivy.uix.screenmanager import ScreenManager, Screen
from kivymd.uix.list import  TwoLineAvatarIconListItem

from kivymd.uix.dialog import MDDialog
from kivy.uix.boxlayout import BoxLayout
from kivymd.uix.button import MDFlatButton

from kivy.properties import NumericProperty, StringProperty

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
    tmp = StringProperty()
    start = False

    def on_enter(self):
        self.store = JsonStore("Items.json")
        var = self.store.get(self.name_)
        self.timer = var.get('time')
        self.tmp = time.strftime('%H:%M:%S', time.gmtime(self.timer))
        #self.sound = SoundLoader.load('sound.ogg')
        
        self.sound = SoundLoader.load('name.mp3')

    def start_button(self):
        if self.start == False:
            self.even = Clock.schedule_interval(self.run, 1)
            self.start = True
        elif self.start:
            self.ids.start.text = 'start' if self.ids.start.text != 'start' else 'pause'

        if self.ids.start.text == 'start':
            self.even()
        else:
            self.even.cancel()
     
    def stop_button(self):
        self.ids.stop.state = 'down' if self.ids.stop.state != 'down' else 'normal'
        print(self.ids.stop.state)
        self.sound.stop()
           
    def run(self, i):
        self.timer -= 1
        var = time.gmtime(self.timer)
        self.ids.timer.text = time.strftime('%H:%M:%S', var)

        #sound = AudioSegment.from_file(os.path.join(script_directory, 'name.mp3'))
        #play(sound)
        #self.sound = SoundLoader.load('sound.ogg')
        if self.timer == 0: # 3595:
            os.system('notify-send Take_a_small_break')
            self.ids.timer.text = '00:00:00'
            self.even.cancel()
            if self.sound:
                self.sound.play()


    def delete(self):
        pass

    def go_back(self):
        self.manager.current = 'main_screen'

    def on_leave(self, *args):
        self.start = False
        try:
            if self.even:
                self.even.cancel()
        except:
            pass
        self.sound.stop()
        self.tmp = ''
        self.ids.start.text = 'start'

class Content(BoxLayout):

    pass

class TwoLineAvatarIconListItemCustom(TwoLineAvatarIconListItem):

    pass

class MainScreen(Screen):

    dialog = None

    def __init__(self, **kwargs):
        super(MainScreen, self).__init__(**kwargs)
        Clock.schedule_once(self.get_it, 1)
        self.store = JsonStore('Items.json')
        for x in self.store:
            print(self.store.get(x), '< --')

    def get_it(self, i):
        for x in self.store:
            time_ = self.store.get(x).get('time')
            var = time.gmtime(time_)
            time__ = time.strftime('%H:%M:%S', var)

            self.ids.container.add_widget(
                TwoLineAvatarIconListItemCustom(text=f"{x}", 
                    secondary_text=str(time__), 
                    on_press=self.callback_1,
                )
            )

    def callback_0(self, instance):
        if not self.dialog:
            self.dialog = MDDialog(
                title='Create Item',
                type='custom',
                content_cls=Content(),
                buttons=[
                    MDFlatButton(
                        text='CANCEL', on_release=self.close_dialog
                    ),
                    MDFlatButton(
                        text='PUT', on_release=self.get_items
                    ),
                ],
            )    
        self.dialog.open()

    def get_items(self, *args):
        name = self.dialog.content_cls.ids.t1.text
        time_ = self.dialog.content_cls.ids.t2.text

        try:
            time_ = int(time_) * 3600
        except:
            time_ = 3600

        self.store.put(name, time=time_) 
        self.ids.container.clear_widgets()
        Clock.schedule_once(self.get_it, 0.1)
        self.close_dialog(self)


    def callback_1(self, instance):
        DetailScreen.name_ = instance.text
        self.manager.current = 'detail_screen'
 
    def close_dialog(self, instance):
        self.dialog.content_cls.ids.t1.text = ''
        self.dialog.content_cls.ids.t2.text = ''
        self.dialog.dismiss()

class App(MDApp):
    
    templates = (
        'templates/index.kv',    
    )

    def build(self):
        config = self.config
        for x in self.templates:
            root = Builder.load_file(x)
        self.window_manager = WindowManager()
        return self.window_manager
    
    #def build_config(self, config):
        #self.config.setdefaults('Items': {})

App().run()
