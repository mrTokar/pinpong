from kivy.app import App
from kivy.uix.widget import Widget
from kivy.vector import Vector
from kivy.clock import Clock
from kivy.properties import NumericProperty, ReferenceListProperty, ObjectProperty

from random import randint


class PinPongBall(Widget):

    speed_x = NumericProperty(0)
    speed_y = NumericProperty(0)
    # shorthand for speed_x and speed_y
    speed = ReferenceListProperty(speed_x, speed_y)

    def move(self):
        """Will move the ball one step. This will be called 
        in equal intervals to animate the ball"""
        self.pos = Vector(*self.speed) + self.pos


class PinPongRacket(Widget):
    score = NumericProperty(0)

    def bounce_ball(self, ball):
        if self.collide_widget(ball):
            sx, sy = ball.speed
            bounced = Vector(-1 * sx, sy) * 1.1
            ball.speed = bounced.x, bounced.y


class PinPongGame(Widget):
    # link on ball in kv file
    ball = ObjectProperty(None)
    # link on rackets in kv file
    pc_racket = ObjectProperty(None)
    player_racket = ObjectProperty(None)

    def restart_ball(self, vec=(5, 0)):
        """restart ball and give him start speed(vec)"""
        self.ball.center = self.center
        self.ball.speed = Vector(vec).rotate(randint(-70, 70))

    def update(self, dt):
        """Call ball.move and other"""
        self.ball.move()

        # bounce off racket
        self.pc_racket.bounce_ball(self.ball)
        self.player_racket.bounce_ball(self.ball)
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
        if touch.x > self.width - self.width/3:
            self.player_racket.center_y = touch.y
        #===========DEL IT=======================
        if touch.x < self.width/3:
            self.pc_racket.center_y = touch.y   


class PinPongApp(App):
    def build(self):
        game = PinPongGame()
        game.restart_ball()
        Clock.schedule_interval(game.update, 1.0 / 60.0) 
        return game


if __name__ == '__main__':
    PinPongApp().run()