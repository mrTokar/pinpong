from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.vector import Vector
from kivy.clock import Clock
from kivy.properties import (
    NumericProperty, ReferenceListProperty, ObjectProperty, ListProperty
)
from kivy.core.window import Window
from random import randint
from sys import exit

Window.minimum_width = 650
Window.minimum_height = 535

class PinPongRacket(Widget):
    score = NumericProperty(0)

    def bounce_ball(self, ball):
        """Change ball's vecotr"""
        if self.collide_widget(ball):
            sx, sy = ball.speed
            offset = (ball.center_y - self.center_y) / (self.height / 2)
            bounced = Vector(-1 * sx, sy) * 1.1
            ball.speed = bounced.x, bounced.y + offset


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
    # link on ball in kv file
    ball = ObjectProperty(None)
    # link on rackets in kv file
    pc_racket = ObjectProperty(None)
    player_racket = ObjectProperty(None)
    menu = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._keyboard = Window.request_keyboard(lambda: None, self)
        if self._keyboard.widget:
            pass
        self._keyboard.bind(on_key_down=self._on_keyboard_down)

    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        if keycode[1] == "escape":
            self.menu.open()
        return True

    def restart_ball(self, vec=(5, 0)):
        """restart ball and give him start speed(vec)"""
        self.ball.center = self.center
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

        # bounce off left and right 
        elif self.ball.x < self.x:
            self.player_racket.score += 1
            self.restart_ball(vec=(5,0))
        elif self.ball.x > self.width:
            self.pc_racket.score += 1
            self.restart_ball(vec=(-5,0))

    def on_touch_move(self, touch):
        """Toch_move Event. Racket control"""
        h = self.player_racket.height / 2 
        if touch.x > self.width - self.width/3:
            if h <= touch.y <= self.height - h:
                self.player_racket.center_y = touch.y
            elif h > touch.y:
                self.player_racket.center_y = h
            else:
                self.player_racket.center_y = self.height - h
    

class Menu(BoxLayout):
    def init_root_widget(self):
        """Search root widget and save its link to attribute"""
        for w in self.walk_reverse(): 
            if isinstance(w, PinPongGame):
                self.game = w

    def start(self):
        """Start game"""
        self.pos = self.size[0] * -1, self.size[1] * -1  # move menu
        try:
            self.game.restart_ball()
        except AttributeError:
            self.init_root_widget()
            self.game.restart_ball()
        self.clock = Clock.schedule_interval(self.game.update, 1.0 / 100.0)

    def exit_app(self):
        exit(0)

    def setting(self):
        print(self.size, self.pos)
        print("window", Window.size)

    def open(self):
        """Pause game and open menu"""
        self.clock.cancel()
        self.game.restart_ball(vec=(0,0))
        self.pos = 0.05*self.game.width/2, 0.10*self.game.width/2


class PinPongApp(App):
    def build(self):
        game = PinPongGame()
        return game


if __name__ == '__main__':
    PinPongApp().run()