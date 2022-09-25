from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.vector import Vector
from kivy.properties import (
    NumericProperty, ReferenceListProperty, ObjectProperty, ListProperty
)

from kivy.clock import Clock
from kivy.core.window import Window
from kivy.core.audio import SoundLoader

from random import randint
import os, sys
from kivy.resources import resource_add_path, resource_find


class PinPongRacket(Widget):
    score = NumericProperty(0)
    vec = 7    
    pong = SoundLoader.load("source\pong.mp3")
    pong.volume = 0.8

    def bounce_ball(self, ball):
        """Change ball's vecotr"""
        if self.collide_widget(ball):
            self.pong.play()
            sx, sy = ball.speed
            offset = (ball.center_y - self.center_y) / (self.height / 2)
            bounced = Vector(-1 * sx, sy) * 1.1
            ball.speed = bounced.x, bounced.y + offset
            self.vec *= 1.1

class ComputerPlayer:
    def __init__(self, racket: PinPongRacket):
        self.racket = racket

    def change_flag(self, speed_x, speed_y):
        """On/Off moving racket"""
        if speed_x < 0:
            self.flag_move = True
            self.speed = speed_y
        else:
            self.flag_move = False

    def change_speed(self, speed_y):
        """Change speed PC_racket"""
        self.speed = 0.7 * speed_y

    def move_racket(self):
        """Move racket"""
        if self.flag_move:
            move = self.speed + self.racket.center_y
            h = self.racket.height / 2
            if h < move < Window.height - h:
                self.racket.center_y = move
            elif h > move:
                self.racket.center_y = h
            else:
                self.racket.center_y = Window.height - h


class PinPongBall(Widget):
    speed_x = NumericProperty(0)
    speed_y = NumericProperty(0)
    # shorthand for speed_x and speed_y
    speed = ReferenceListProperty(speed_x, speed_y) 

    def move(self):
        """Will move the ball one step. This will be called 
        in equal intervals to animate the ball"""
        self.pos = Vector(*self.speed) + self.pos

    def create_ref(self, pc: ComputerPlayer):
        """Create link to ComputerPlayer class"""
        self.pc = pc

    def on_speed_x(self, refproperty, value):
        """Observation of the value speed_x. 
        Switch for ComputerPlayer"""
        self.pc.change_flag(value, self.speed_y)

    def on_speed_y(self, refpropert, value):
        """Observation of the value speed_y.
        Change speed racket."""
        if self.pc.flag_move:
            self.pc.change_speed(self.speed_y)


class PinPongGame(Widget):
    # link on kvy file
    ball = ObjectProperty(None)
    pc_racket = ObjectProperty(None)
    player_racket = ObjectProperty(None)

    menu = ObjectProperty(None)
    setting = ObjectProperty(None)

    soundtreck = SoundLoader.load("source\soundtreck.wav")
    jump = SoundLoader.load("source\jump.wav")
    jump.volume = 0.8

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._keyboard = Window.request_keyboard(lambda: None, self)
        self._keyboard.bind(on_key_down=self._on_keyboard_down)
        Window.bind(on_touch_move=self.move_by_using_touch)
        if self.soundtreck:
            self.soundtreck.loop = True
            self.soundtreck.play()

    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        if self.setting.keymode and keycode[0] in (273, 274):
            self.move_by_using_keyboard(keycode[0])
        elif keycode[1] == "escape":
            self.menu.open()
        return True

    def restart_ball(self, vec=(5, 0)):
        """restart ball and give him start speed(vec)"""
        self.ball.center = self.center
        self.player_racket.vec = 7
        self.pc = ComputerPlayer(self.pc_racket)
        self.ball.create_ref(self.pc)
        self.ball.speed = Vector(vec).rotate(randint(-70, 70))

    def update(self, dt):
        """Call ball.move and other"""
        self.ball.move()
        # bounce off racket
        self.pc_racket.bounce_ball(self.ball)
        self.player_racket.bounce_ball(self.ball)
        self.pc.move_racket()
        # bounce off top and bottom
        if (self.ball.y < 0) or (self.ball.top > self.height):
            self.ball.speed_y *= -1
            self.jump.play()

        # bounce off left and right 
        elif self.ball.x < self.x:
            self.player_racket.score += 1
            self.restart_ball(vec=(5,0))
        elif self.ball.x > self.width:
            self.pc_racket.score += 1
            self.restart_ball(vec=(-5,0))

    def move_by_using_touch(self, some, touch):
        """Racket control by used touch (mouse)"""
        h = self.player_racket.height / 2 
        if touch.x > self.width - self.width/3:
            if h <= touch.y <= self.height - h:
                self.player_racket.center_y = touch.y
            elif h > touch.y:
                self.player_racket.center_y = h
            else:
                self.player_racket.center_y = self.height - h

    def move_by_using_keyboard(self, key):
        h = self.player_racket.height / 2
        if key == 273:
            res = self.player_racket.center_y + self.player_racket.vec
            if res <= self.height-h:
                self.player_racket.center_y = res
            else:
                self.player_racket.center_y = self.height - h
        else:
            res = self.player_racket.center_y - self.player_racket.vec
            if res >= h:
                self.player_racket.center_y = res
            else:
                self.player_racket.center_y = h


class SettingsMenu(BoxLayout):
    mypos = [-10*Window.size[0], -10*Window.size[1]]
    haveroot = False
    keymode = False

    def init_root_widget(self):
        """Search root widget and save its link to attribute"""
        if not self.haveroot:
            self.haveroot = True
            for w in self.walk_reverse(): 
                if isinstance(w, PinPongGame):
                    self.root = w
            
    def on_chkb_mouse_active(self, value):
        """Switch On/Off mouse control"""
        if value: 
            Window.bind(on_touch_move=self.root.move_by_using_touch)
        else:
            Window.unbind(on_touch_move=self.root.move_by_using_touch)

    def on_chkb_keyboard_active(self, value):
        """Switch On/Off keyboard control"""
        self.keymode = value

    def on_volume(self, value):
        """Binded changing volum"""
        self.root.pc_racket.pong.volume = 0.8 * value/100
        self.root.player_racket.pong.volume = 0.8 * value/100
        self.root.jump.volume = 0.8 * value/100
        self.root.soundtreck.volume = value/100
        

class Menu(BoxLayout):
    mypos = [0.05*Window.size[0]/2, 0.15*Window.size[1]/2]

    def init_root_widget(self):
        """Search root widget and save its link to attribute"""
        for w in self.walk_reverse(): 
            if isinstance(w, PinPongGame):
                self.game = w
        self.setting = self.game.setting

    def move_widget(self, object, action: bool):
        """Change object.pos   Object is instance Menu or SettingMenu\n
        True <=> show\n
        False <=> hide"""
        try:
            if action:
                object.pos = 0.05*self.game.width/2, 0.15*self.game.height/2
            else: 
                object.pos = -10*self.game.width, -10*self.game.height
        except AttributeError:
            self.init_root_widget()
            if action:
                object.pos = 0.05*self.game.width/2, 0.15*self.game.height/2
            else: 
                object.pos = -10*self.game.width, -10*self.game.height

    def start(self):
        """Start game"""
        self.move_widget(self, False)
        try:
            self.game.restart_ball()
        except AttributeError:
            self.init_root_widget()
            self.game.restart_ball()
        self.clock = Clock.schedule_interval(self.game.update, 1.0 / 200.0)

    def exit_app(self):
        sys.exit(0)

    def open_setting(self):
        try:
            self.move_widget(self, False)
            self.move_widget(self.setting, True)
        except AttributeError:
            self.init_root_widget()
            self.move_widget(self, False)
            self.move_widget(self.setting, True)
        self.setting.init_root_widget()
       

    def open(self):
        """Pause game and open menu"""
        try:
            self.clock.cancel()
        except AttributeError:
            # the case when the clock has not yet been created
            self.init_root_widget()
        self.game.restart_ball(vec=(0,0))
        self.move_widget(self, True)
        self.move_widget(self.setting, False)


class PinPongApp(App):
    def build(self):
        game = PinPongGame()
        Window.minimum_width = 650
        Window.minimum_height = 535
        return game


if __name__ == '__main__':
    if hasattr(sys, '_MEIPASS'):
        resource_add_path(os.path.join(sys._MEIPASS))
    PinPongApp().run()