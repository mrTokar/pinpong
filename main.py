from kivy.config import Config

Config.read("config.ini")

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button

from kivy.properties import (ObjectProperty, ListProperty, StringProperty, NumericProperty, 
        ColorProperty)

from kivy.clock import Clock
from kivy.vector import Vector

from kivy.core.window import Window
from kivy.core.audio import SoundLoader

from random import choice
from math import sqrt
from pickle import load, dump

LBM = [-1, "ЛКМ"]
RBM = [-2, "ПКМ"]

MOVE_MOUSE = "Передвижение мышкой"
ARROWS_KEY = "Стрелки на клавиатуре"

AUTO = "Автоматически"
SPACE = "Пробел"


def load_db(difficulty: str) -> list:
    "Load table records"
    try:
        with open("table.data", "rb") as file:
            data_dict = load(file)
            if difficulty in data_dict.keys():
                data = data_dict[difficulty]
            else:
                data = []
    except FileNotFoundError:
        data = []
    return data


def save_db(data: list, difficulty: str):
    "Save table records"
    try:
        with open("table.data", "rb") as file:
            data_dict = load(file)
    except FileNotFoundError:
        data_dict = {}
    data_dict[difficulty] = data    
    with open("table.data", "wb") as file:
        dump(data_dict, file)


class MyKeyboardListener(Widget):
    shoot_event = ListProperty()

    def __init__(self, target: Widget, mods: list or str, **kwargs):
        """Listener keyboard. Parametr mode should take tuple of mods.\n
        To track the shot, you need to specify the keycode as shoot_event"""
        super(MyKeyboardListener, self).__init__(**kwargs)
        self._keyboard = Window.request_keyboard(
            None, target, 'text')
        self.target = target
        if mods == "set":
            self._keyboard.bind(on_key_down=self._on_keyboard_down_set)
        elif mods == "listen":
            self._keyboard.bind(on_key_down=self._on_keyboard_listen)
        else:
            for mod in mods:
                if mod == "shoot":
                    self._keyboard.bind(on_key_down=self._on_keyboard_down_shoot)
                elif mod == "aim":
                    self._keyboard.bind(on_key_down=self._on_keyboard_down_aim)
                elif mod == "change_color":
                    self._keyboard.bind(on_key_down=self._on_keyboard_down_color)


    def _on_keyboard_down_shoot(self, keyboard, keycode, text, mofifiers):
        "Shoot_event Reacting Method"
        if keycode[0] == self.shoot_event[0]:
            self.target.pushball.shoot()
        return True

    def _on_keyboard_down_aim(self, keyboard, keycode, text, modi):
        "Aim_event Reacting Method"
        if keycode[0] == 275:  # right
            self.target.aim.aim_right()
        elif keycode[0] == 276:  # left
            self.target.aim.aim_left()
        return True

    def _on_keyboard_down_color(self, keboard, keycode, text, modi):
        "Change_clor_event Reacting Method"
        if keycode[0] == 32:  # spacebar
            self.target.pushball.change_color()
        return True

    def _keyboard_closed(self):
        "Close keybaord"
        self._keyboard.unbind(on_key_down=self._on_keyboard_down_set)
        self._keyboard.unbind(on_key_down=self._on_keyboard_down_shoot)
        self._keyboard.unbind(on_key_down=self._on_keyboard_down_aim)
        self._keyboard.unbind(on_key_down=self._on_keyboard_down_color)
        self._keyboard.unbind(on_key_down=self._on_keyboard_listen)
        self._keyboard = None

    def _on_keyboard_down_set(self, keyboard, keycode, text, modifiers):
        "Keycode Recording"
        if keycode[0] != 32:
            self.target.get_resulat(keycode)
        return True

    def _on_keyboard_listen(self, keyboard, keycode, text, modifiers):
        "Listen all keyboard"
        self.target.close_me()
        return True

# ========================= GUI ==============================

class Menu(FloatLayout):
    """Based for Menus"""
    back_btn = ObjectProperty()

    def __init__(self, rootw: Widget, **kwargs):
        """rootw - link to Container"""
        super().__init__(**kwargs)
        self.rootw = rootw
        self.back_btn.bind(on_release=self.back)

    def back(self, *someone):
        """Return back page"""
        lib = {MainMenu: InputName, Settings: MainMenu, Rules: Settings, ControlSettings: Settings}
        self.rootw.clear_widgets()
        self.rootw.add_widget(lib[type(self)](rootw=self.rootw))


class InputName(FloatLayout):
    textinput = ObjectProperty()

    def __init__(self, rootw: Widget, **kwargs):
        """Set the root widget."""
        super().__init__(**kwargs)
        self.rootw = rootw

    def on_focus(self):
        """Hide help and return normal font color"""
        if self.textinput.text == "Введите имя...":
            self.textinput.text = ""
            self.textinput.foreground_color = (0,0,0,1)

    def text_validate(self, text):
        """Call when press enter"""
        if text:
            self.rootw.get_nickname(text)


class Settings(Menu):
    "Setting menu. Here you can adjust the sound, go to the rules and control settings."
    set_volume = NumericProperty()
    def __init__(self, rootw: Widget, **kwargs):
        super().__init__(rootw, **kwargs)
        self.set_volume = self.rootw.setting["volume"]

    def rule(self):
        """Open rule window"""
        self.rootw.clear_widgets()
        self.rootw.add_widget(Rules(rootw=self.rootw))

    def controlset(self):
        """Open control list"""
        self.rootw.clear_widgets()
        self.rootw.add_widget(ControlSettings(rootw=self.rootw,
                                            shoot_key=self.rootw.setting['shoot_key'],
                                            ball_direction = self.rootw.setting['ball_direction'],
                                            change_color=self.rootw.setting['change_color']))

    def on_volume(self, value):
        "Observation volume"
        self.rootw.load_new_settings("volume", value)


class MainMenu(Menu):
    """The main menu of the application. From here you can start the game,
    go to settings and exit from here"""

    def start(self):
        """Start game"""
        self.rootw.ask_difficulty()
    
    def open_setting(self):
        """Open Settings"""
        self.rootw.clear_widgets()
        self.rootw.add_widget(Settings(rootw=self.rootw))


class Rules(Menu):
    """A menu that spells out the rules of the game"""


class ControlSettings(Menu):
    "Control settings menu. You can change the binding of events to keys."
    shoot_key_btn = ObjectProperty()
    ball_direction_list = ObjectProperty()
    change_color_list = ObjectProperty()

    shoot_key = ListProperty()
    flag1 = True  # plug
    ball_direction = StringProperty()
    flag2 = True  # plug
    change_color = StringProperty()
    flag3 = True  # plug
    listen = False

    def __init__(self, rootw: Widget, **kwargs):
        """Specify the installed settings, how\n
        shoot_key = keycode,\n
        ball_direction = MOVE_MOUSE // ARROWS_KEY,\n
        change_color = AUTO // SPACE"""
        super().__init__(rootw, **kwargs)

    def change_shoot_key(self):
        """Del old bind to shoot. Enabel listening keyboard
        press to set new bind. Thereafter disable listening keyboard press."""
        self.listen = True
        self.shoot_key_btn.text = "Укажите клавишу..."
        self.shoot_key_btn.italic = True
        self.key_listener = MyKeyboardListener(target=self, mods="set")

    def get_resulat(self, keycode):
        """Read changed setting"""
        self.shoot_key = keycode 
        self.shoot_key_btn.italic = False
        self.shoot_key_btn.text = keycode[1].upper()
        self.listen = False
        self.key_listener._keyboard_closed()
        del self.key_listener

    def on_touch_down(self, touch):
        "Mouse click tracking"
        if self.listen:
            if touch.button == "right":
                self.shoot_key = RBM
                self.shoot_key_btn.text = RBM[1]
            elif touch.button == "left":
                self.shoot_key = LBM
                self.shoot_key_btn.text = LBM[1]

            try:
                self.key_listener._keyboard_closed()
                del self.key_listener
            except AttributeError:
                pass

            self.listen = False
            self.shoot_key_btn.italic = False   
        return super().on_touch_down(touch)


    def on_shoot_key(self, instance, value):
        "Observation shoot_key"
        if self.flag1:
            self.flag1 = False
        else:
            self.rootw.load_new_settings(setting="shoot_key",value=value)  

    def on_ball_direction(self, instance, value):
        "Observation ball_direction"
        if self.flag2:
            self.flag2 = False
        else:
            self.rootw.load_new_settings(setting="ball_direction",value=value)

    def on_change_color(self, instance, value):
        "Observation change_color"
        if self.flag3:
            self.flag3 = False
        else:
            self.rootw.load_new_settings(setting="change_color",value=value)


class DifficultySelection(FloatLayout):
    "Difficulty selection menu. The selected difficulty is transferred to the game."
    difficulty = StringProperty('')

    def on_difficulty(self, isinstance, value):
        "Observation difficulty"
        self.parent.init_game(value)

class YourScore(FloatLayout):
    "Game Summary"
    score = NumericProperty(0)
    table = ObjectProperty()
    dif = StringProperty('')
    
    def __init__(self, rootw: Widget, name: str, **kwargs):
        super().__init__(**kwargs)
        data = load_db(self.dif)
        self.rootw = rootw
        repeat = 0 
        for player in data:
            if player[0] == name:
                repeat = 1
            if player[1] <= self.score:
                data.insert(data.index(player), [name, self.score])
                break
        else:
            if len(data) < 5:
                data.append([name, self.score]) 

        if repeat: 
            for i in range(-1, -len(data)-1, -1):
                if data[i][0] == name:
                    data.pop(i)
                    break
    
        if len(data) > 5:
            data = data[:5]
    
        for i in range(5):
            self.table.add_widget(Label(text=str(i+1)+")", size_hint_x=None, width=50, font_size=30, halign='right'))
            try:
                if data[i][0] != name:
                    self.table.add_widget(Label(text=data[i][0], font_size=30, halign='left'))
                    self.table.add_widget(Label(text=str(data[i][1]), font_size=30, halign='left'))
                else:
                    self.table.add_widget(Label(text=data[i][0], font_size=30, halign='left', color=(250/255, 42/255, 42/255), outline_color=(1,1,1), outline_width=2))
                    self.table.add_widget(Label(text=str(data[i][1]), font_size=30, halign='left', color=(250/255, 42/255, 42/255), outline_color=(1,1,1), outline_width=2))

            except IndexError:
                self.table.add_widget(Label(text="--", font_size=30, halign='left'))
                self.table.add_widget(Label(text="--", font_size=30, halign='left'))

        save_db(data, self.dif)
        self.keyboard = MyKeyboardListener(self, "listen")

    def on_touch_down(self, touch):
        self.keyboard._keyboard_closed()
        del self.keyboard
        self.close_me()
        return super().on_touch_down(touch)
    
    def close_me(self, some=0):
        "Close this Menu"
        self.rootw.clear_widgets()
        self.rootw.add_widget(MainMenu(self.rootw))
    
# ========================= GAME ==============================

class Aiming(Widget):
    "Aim class. Described display and reading"
    sx = 500
    sy = 20
    end_coord = ListProperty([500, 100])
    mycolor = ColorProperty((1,1,1,1))
    
    def __init__(self, rootgame, set_control: str, **kwargs):
        """rootgame - link to GameBall \n
        set_control - takes MOVE_MOUSE or other"""
        super().__init__(**kwargs)
        self.rootgame = rootgame
        if set_control == MOVE_MOUSE:
            Window.bind(mouse_pos=self.moving)

    def moving(self, widget, pos):
        "Сalculates the coordinate of the point of the end of the sight line"
        l = sqrt((pos[0] - self.sx)**2 + (pos[1] - self.sy)**2)
        x = 80 * (pos[0] - self.sx) / l 
        x = x if -69.6 <= x <= 69.6 else 69.6 * x/abs(x)  # limit of spectr x 
        y = 80 * (pos[1] - self.sy) / l  
        y = y if y >= 40 else 40  # limit of spectr
        
        self.end_coord = (self.sx + x, self.sy + y)

    def stream_on(self):
        "Show canvas"
        self.mycolor = (1,1,1,1)
        
    def stream_off(self):
        "Hide canvas"
        self.mycolor = (1,1,1,0)

    def get_vector(self) -> Vector:
        "Return aiming Vector"
        return Vector(self.end_coord[0] - self.sx, self.end_coord[1] - self.sy) / 20

    def aim_right(self):
        "Move aim right"
        self.end_coord[0] += 1 if self.end_coord[0] + 1 <= 570 else 0
        self.end_coord[1] = sqrt(6400 - (self.end_coord[0] - 500)**2) + 20
    
    def aim_left(self):
        "Move aim left"
        self.end_coord[0] -= 1 if self.end_coord[0] - 1 >= 430 else 0
        self.end_coord[1] = sqrt(6400 - (self.end_coord[0] - 500)**2) + 20

class PushBall(Widget):
    "The class of the ball that the player is pushing"
    ismove = False
    start_pos = [480, 0]
    matrix_border = []
    color = ColorProperty(choice(['red', 'blue', 'green', 'yellow', 'orange', 'pink', "purple"]))

    def __init__(self, rootgame, setting_color, **kwargs):
        """root - link to GameBall \n
        setting_color - rule how to change color. Takes AUTO or SPACE \n
        volume - volume bounce_sound"""
        super().__init__(pos=self.start_pos, **kwargs)
        self.rootgame = rootgame
        self.bounce_sound = SoundLoader.load("source\jump.wav")
        self.bounce_sound.volume = 0.8 * (self.rootgame.volume / 100)
        self.ischange = True if setting_color is AUTO else False

    def shoot(self):
        "Start move this ball"
        if not self.ismove:
            self.ismove = True
            self.rootgame.aim.stream_off()
            self.matrix_border = self.rootgame.matrix.get_border()
            self.speed = self.rootgame.aim.get_vector()
            self.clock = Clock.schedule_interval(self.move, 1/1000)

    def move(self, some):
        "Moving this ball"
        self.pos[0] += self.speed[0]
        self.pos[1] += self.speed[1]

        if (self.pos[0] < 0) or (self.right > 1000):
            if self.bounce_sound:
                self.bounce_sound.play()
            self.speed[0] *= -1

        for ball in self.matrix_border:
            if self.collide_widget(ball):
                self.stop()

    def make_copy(self, color):
        "Make a Static copy of self"
        my_copy = StaticBall(self.rootgame, self.rootgame.matrix, set_color=color, pos=self.last_pos)
        my_copy.check_burst()

    def restart_ball(self):
        "Return to start pos and chage color if it is AUTO"
        self.pos = self.start_pos
        self.ismove = False
        self.rootgame.aim.stream_on()
        if self.ischange:
            self.change_color()

    def change_color(self, some=0):
        "Change color"
        if not self.ismove:
            self.color = choice(['red', 'blue', 'green', 'yellow', 'orange', 'pink', "purple"])

    def volume_control(self, value):
        "Change volume sound effects"
        self.bounce_sound.volume = 0.8 * (value / 100)

    def stop(self):
        "Stop and restart ball"
        self.clock.cancel()
        last_color = self.color
        self.last_pos = self.pos[:]
        self.restart_ball()
        self.make_copy(last_color)


class StaticBall(Widget):
    color = ColorProperty()
    index_y = NumericProperty(0)
    index_x = NumericProperty(0)

    def __init__(self, rootgame, matrix, set_color="random", **kwargs):
        """rootgame - link to GameBall \n
        matrix - link to Matrix \n
        volume - volume sound_burst \n
        set_color - ball's color"""
        super().__init__(**kwargs)
        self.rootgame = rootgame
        if set_color == "random":
            self.color = choice(['red', 'blue', 'green', 'yellow', 'orange', 'pink', "purple"])
        else: 
            self.color = set_color
        self.sound = matrix.sound_burst

        myround = lambda n: int(n) + round(n-int(n))
        self.index_y = myround((690 - self.pos[1]) / 40 - 1)
        self.index_x = myround(self.pos[0] * 0.025)
        
        self.rootgame.play_field.add_widget(self)
        matrix.add(self)

    def burst(self):
        "Self burst"
        self.counter = 0
        self.copy_color = self.color
        if self.sound:
            self.sound.play()
        self.flash = Clock.schedule_interval(self.flashing, 0.25)

    def check_burst(self):
        "Checks the ball's neighbors, if the resulting list is not empty, then bursts them"
        neighbors = self.rootgame.matrix.get_neighbors(self, [])
        if len(neighbors) >= 3:
            self.rootgame.score += len(neighbors) * 2 * (len(neighbors)//5) if len(neighbors) >=5 else len(neighbors)
            for ball in neighbors:
                ball.burst()
            self.rootgame.matrix.add_row()
        else:
            self.rootgame.matrix.add_row()

    def on_index_y(self, instance, value):
        "Check index_y, if it go beyond the limit shoots a rootgame.lose()"
        if value >= 14:
            self.counter = 0
            self.copy_color = self.color
            self.rootgame.pushball.ismove = True
            self.flash = Clock.schedule_interval(self.flashing, 0.5)

    def flashing(self, some):
        "Turns on the flashing of the ball"
        if self.counter <= 2:
            self.counter += 1
            self.color = [1,1,1,1] if self.color == self.copy_color else self.copy_color
        else:
            self.flash.cancel()
            if self.index_y >= 14:
                self.rootgame.lose()
            else:
                self.pos[0] += 1500
                self.rootgame.matrix.delete(self)

class Matrix:
    """Matrix of StaticBalls"""
    def __init__(self, rootgame,  difficulty: str):
        """rootgame - link to GameBall \n
        difficulty - game's difficulty"""
        if difficulty == "easy":
            rows = 6
            self.free_step = 5
        elif difficulty == "normal":
            rows = 8
            self.free_step = 5
        else: 
            rows = 10
            self.free_step = 3

        self.rootgame = rootgame
        self.me = []
        self.steps = 0
        self.first_is_shift = False
        self.sound_burst = SoundLoader.load("source\\burst_ball.mp3")
        self.sound_burst.volume = 0.8 * (self.rootgame.volume / 100)

        for row in range(rows):
            self.me.append([])
            if row % 2 == 0:
                for x in range(25):
                    StaticBall(self.rootgame, self, pos=(x*40, 690 - 40*(row + 1)))
            else:
                for x in range(24): 
                    StaticBall(self.rootgame, self, pos=(20 + x*40, 690 - 40*(row + 1)))

        self.top = Widget(size_hint=(1, 0.01), pos=(0, 690))
        self.rootgame.play_field.add_widget(self.top)

    def volume_control(self, value):
        "Change volume sound effects"
        self.sound_burst.volume = 0.8 * (value / 100)

    def add(self, ball: StaticBall):
        "Add ball in matrix"
        try:
            if ball.index_y >= 0:
                self.me[ball.index_y].insert(ball.index_x, ball)
        except IndexError:
            self.me.append([])
            self.me[ball.index_y].insert(ball.index_x, ball)
            
    def delete(self, ball: StaticBall):
        "Remove ball from the matrix"
        row = self.me[ball.index_y]
        try:
            if row[ball.index_x].index_x == ball.index_x: 
                row.pop(ball.index_x)
        except IndexError:
            pass
        
        for obj in row:
            if obj.index_x == ball.index_x:
                row.remove(obj)

    def get_border(self) -> list:
        "Returns a list of Static balls that can be intersected"
        result = [] 
        for row in range(len(self.me)-1, -1, -1):
            if len(self.me[row]) >= 24:
                result += self.me[row]
                break
            else:
                result += self.me[row]
        else:
            result.append(self.top)
        self.steps += 1
        return result    

    def get_neighbors(self, ori_ball: StaticBall, result=[]) -> list:
        """Returns a list of neighbors with the color of the passed object"""
        model = ori_ball.color
        row = ori_ball.index_y
        col = ori_ball.index_x

        if not result:
            result.append(ori_ball)
        
        if self.is_shift(row):
            dontcheck = -2
            # check right top neighbor
            ball =  self.get_ball(col+1, row-1)
            if ball:  # if it is not None
                if ball.color == model:
                    if ball not in result:
                        result.append(ball)
                        result = self.get_neighbors(ball, result=result)
        else: 
            dontcheck = 2
            # check left bottom neighbor 
            ball = self.get_ball(col-1, row+1)
            if ball:  # if it is not None
                if ball.color == model:
                    if ball not in result:
                        result.append(ball)
                        result = self.get_neighbors(ball, result=result)

        for dy in range(-1, 2):
            for dx in range(-1, 2):
                if dy + dx == 0 or dy + dx  == dontcheck:
                    continue  # discards unnecessary
                ball = self.get_ball(abs(col + dx), abs(row + dy))
                if ball:
                    if ball.color == model:
                        if ball not in result:
                            result.append(ball)
                            result = self.get_neighbors(ball, result=result)
            
            if dy != 0:
                for dx in [0.5, -1]:
                    ball = self.get_ball(abs(col+int(dx*dontcheck)), abs(row+dy))
                    if ball:
                        if ori_ball.collide_widget(ball) and ball.color == model:
                            if ball not in result:
                                result.append(ball)
                                result = self.get_neighbors(ball, result=result)
        
        return result

    def is_shift(self, row) -> bool:
        "Returns True if the string has a shift, else False"
        return self.first_is_shift if row % 2 == 0 else not self.first_is_shift 

    def add_row(self):
        "Adds a line on top"
        if self.steps % self.free_step == 0:
            self.first_is_shift = not self.first_is_shift
            self.me.insert(0, [StaticBall(self.rootgame, self, pos=(20*self.first_is_shift + x*40, 690))  for x in range(25 - self.first_is_shift)])
            self.counter = 0
            self.clock = Clock.schedule_interval(self.animate_move, 1/40)

    def animate_move(self, some):
        "Move down matrix"
        self.counter += 1
        if self.counter < 40:
            for row in self.me:
                for obj in row:
                    obj.pos[1] -= 1
        else:
            self.clock.cancel()
            for row in self.me:
                for obj in row:
                    # obj.pos[1] -= 1
                    obj.index_y += 1

    def get_ball(self, x: int, y: int) -> StaticBall:
        "Return StaticBall with idex = (x, y)"
        try:
            row = self.me[y]
        except IndexError:
            return None

        try:
            if row[x].index_x == x: 
                return row[x]
        except IndexError:
            pass

        for ball in row:
            if ball.index_x == x:
                return ball

        
class BallsGame(FloatLayout):
    """Class of game. Main Logic"""
    switch_volume = ObjectProperty()
    play_field = ObjectProperty()

    score = NumericProperty(0)

    def __init__(self, rootw: Widget, difficult: str, **kwargs):
        """rootw - link to Container \n
        difficult - choosen difficulty"""
        super().__init__(**kwargs)
        self.rootw = rootw
        self.difficulty = difficult
        self.islose = False
        self.volume = self.rootw.setting["volume"]

        self.matrix = Matrix(self, difficult)
        self.aim = Aiming(self, self.rootw.setting["ball_direction"])
        self.pushball = PushBall(self, self.rootw.setting["change_color"])
        self.play_field.add_widget(self.aim)
        self.play_field.add_widget(self.pushball)

        # set settings
        mods = []
        self.listen = False
        if self.rootw.setting["ball_direction"] == ARROWS_KEY:
            mods.append("aim")

        if self.rootw.setting["change_color"] != AUTO:
            mods.append("change_color")

        if self.rootw.setting["shoot_key"] in (LBM, RBM):
            self.listen = "right" if self.rootw.setting["shoot_key"] == RBM else "left"
            self.keyboard = MyKeyboardListener(self, mods) if mods != [] else None
        else:
            mods.append("shoot")
            self.keyboard = MyKeyboardListener(self, mods, shoot_event= self.rootw.setting["shoot_key"])

    def change_state_sound(self, state):
        "On / Off music"
        if state == "down":       
            self.ids.img.source = "source/speaker_off.png"
            self.rootw.volume_control(0)
            self.pushball.volume_control(0)
            self.matrix.volume_control(0)
        else:
            self.ids.img.source = "source/speaker_on.png"
            self.rootw.volume_control(self.volume)
            self.pushball.volume_control(self.volume)
            self.matrix.volume_control(self.volume)

    def on_touch_down(self, touch):
        "Mouse click tracking"
        if self.listen:
            if touch.button == self.listen:
                self.pushball.shoot()
        return super().on_touch_down(touch)

    def lose(self):
        "Saves points and closes the game"
        if not self.islose:
            self.islose = True
            try:
                self.keyboard._keyboard_closed()
                del self.keyboard
            except AttributeError:
                pass
            self.rootw.clear_widgets()
            self.rootw.add_widget(YourScore(self.rootw, self.rootw.nickname, dif=self.difficulty, score=self.score))

    def restart_game(self):
        "Restart game whith this settings"
        try:
            self.keyboard._keyboard_closed()
            del self.keyboard
        except AttributeError:
            pass
        self.rootw.init_game(self.difficulty)

    def exit_game(self):
        try:
            self.keyboard._keyboard_closed()
            del self.keyboard
        except AttributeError:
            pass
        self.rootw.clear_widgets()
        self.rootw.add_widget(MainMenu(rootw=self.rootw))
        
#  ========================= APP ==============================

class Container(FloatLayout):
    soundtreck = SoundLoader.load("source\\soundtreck.wav")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # self.add_widget(InputName(rootw= self))
        # ============= DEL IT BEFORE RELEASE ===============
        self.nickname = "player0"
        self.add_widget(MainMenu(rootw=self))
        self.setting = {"shoot_key": LBM,
                        "ball_direction": MOVE_MOUSE,
                        "change_color": AUTO, 
                        "volume": 100}
        if self.soundtreck:
            self.soundtreck.loop = True
            self.soundtreck.play()

    def volume_control(self, value):
        "Change volume sound effects"
        self.soundtreck.volume = value / 100

    def get_nickname(self, text):
        """Save inputed name and open new menu"""
        self.nickname = text
        self.clear_widgets()
        self.add_widget(MainMenu(rootw=self))

    def load_new_settings(self, setting: str, value):
        """Changins self settings"""
        self.setting[setting] = value
        if setting == 'volume':
            self.soundtreck.volume = value / 100

    def ask_difficulty(self, *some):
        """Open window for choose difficulty"""
        self.clear_widgets()
        self.add_widget(DifficultySelection())

    def init_game(self, difficulty):
        """Open play field"""
        self.clear_widgets()
        self.add_widget(BallsGame(self, difficulty))

class BallsApp(App):
    def build(self):
        container = Container()
        return container
        

if __name__ == "__main__":
    BallsApp().run()