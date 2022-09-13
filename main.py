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


class PinPongGame(Widget):
    # link on ball in kv file
    ball = ObjectProperty(None)

    def restart_ball(self):
        """restart ball and give him random speed"""
        self.ball.center = self.center
        self.ball.speed = Vector(4,0).rotate(randint(0, 360))

    def update(self, dt):
        """Call ball.move and other"""
        self.ball.move()

        # bounce off top and bottom
        if (self.ball.y < 0) or (self.ball.top > self.height):
            self.ball.speed_y *= -1

        # bounce off left and right 
        if (self.ball.x < 0) or (self.ball.right > self.width):
            self.ball.speed_x *+ -1


class PinPongApp(App):
    def build(self):
        game = PinPongGame()
        game.restart_ball()
        Clock.schedule_interval(game.update, 1.0 / 60.0) 
        return game


if __name__ == '__main__':
    PinPongApp().run()