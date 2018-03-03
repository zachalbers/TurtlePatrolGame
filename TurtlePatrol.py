# All Code written by Zachariah.
# Some general concepts taken from "flappy" and "missle", both written by John Aycock

# Note: Change speed constant if it is running too slow or too fast. Positive only.


import engine
import turtle
import time
import random
import math


# CONSTANTS

# Window Constants
WIDTH = 640
HEIGHT = 640
MAX_Y = HEIGHT // 2
MIN_Y = -HEIGHT // 2
MAX_X = WIDTH // 2
MIN_X = -WIDTH // 2
GROUND_Y = -HEIGHT // 4

#Misc Constants
SPEED = 2
JUMP_HEIGHT = 100
H = 100

# Shape Constants
turtle.register_shape('Mountain1', (
    (0, 0), (50, -70), (60, -100), (55, -120), (80, -145),
    (100, -180), (90, -220), (130, -250), (180, -270), (140, -300),
    (150, -380), (160, -420), (120, -500), (80, -550), (60, -580),
    (30, -600), (0, -640) ))
turtle.register_shape('Mountain2', (
    (0, 0), (50 + H, -70), (60 + H, -100), (55 + H, -120), (80 + H, -145),
    (100 + H, -180), (90 + H, -220), (130 + H, -250), (180 + H, -270), (140 + H, -300),
    (150 + H, -380), (160 + H, -420), (120 + H, -500), (80 + H, -550), (60 + H, -580),
    (30 + H, -600), (0, -640) ))
turtle.register_shape('wheel', (
    (-3,-3), (-3, 3), (3, 3), (3, -3) ))

# VARIABLES
current_jump = 0
score = 0
IN_JUMP = True
IS_UFO = False
IS_CAR = True
MISSILE_COUNT_UP = 0
MISSILE_COUNT_RIGHT = 0
Car_y_pos = 0


# GAME OBJECTS

class Ground(engine.GameObject):
    def __init__(self, left_x, top_y, right_x, bottom_y):
        turtle.register_shape('ground', (
            (left_x, top_y), (right_x, top_y), (right_x, bottom_y), (left_x, bottom_y)) )
        super().__init__(0, 0, 0, 1, 'ground', 'brown')

    def isstatic(self):
        return True

class Hole(engine.GameObject):
    def __init__(self, x_pos):
        turtle.register_shape('hole', ((0, 0), (0, 30), (-40, 15)) )
        super().__init__(x_pos, GROUND_Y, -SPEED, 0, 'hole', 'black')

    def isstatic(self):
        return False

    def in_hole(self, x, y):    # Boundary Detection
        if y > GROUND_Y + 1:
            return False
        if self.x -30 <= x <= self.x:
            return True

class EnemyTurtle(engine.GameObject):
    def __init__(self):
        super().__init__(320, GROUND_Y+5, -SPEED, 0, 'turtle', 'green')

    def isstatic(self):
        return False

    def in_turtle(self, x, y):     # Boundary Detection
        if y > GROUND_Y + 10:
            return False
        if self.x -15 <= x <= self.x:
            return True

class Car(engine.GameObject):
    def __init__(self):
        turtle.register_shape('car', (
            (-3, 0), (-3, 30), (-20, 30), (-20, 0)) )
        super().__init__(0, GROUND_Y, 0, 0, 'car', 'blue')

    def delete(self):
        global IS_CAR
        draw_score(True)
        IS_CAR = False
        super().delete()


    def move(self):
        global IN_JUMP
        global JUMP_HEIGHT
        global current_jump
        global Car_y_pos

        if not IN_JUMP:
            return
        elif current_jump == 0:
            current_jump = JUMP_HEIGHT
            IN_JUMP = False
            return
        # Will move up half jump height and then move back down.
        elif 0 < current_jump <= (JUMP_HEIGHT // 2):
            self.y -= SPEED
            current_jump -= SPEED
        else:
            self.y += SPEED
            current_jump -= SPEED

        Car_y_pos = self.y

class Wheel(engine.GameObject):
    def __init__(self, x_pos, y_pos, speed):
        self.delay = 6
        super().__init__(x_pos, y_pos, 0, speed, 'wheel', 'white')

    def move(self):
        global IN_JUMP
        global Car_y_pos
        if IN_JUMP:
            self.y = Car_y_pos
            return

        if self.delay == 0:
            self.delay = 6
            if self.deltay == -3:
                self.deltay = 3
            else:
                self.deltay = -3
        else:
            self.delay -= 1
            return
        super().move()

    def isoob(self):
        global IS_CAR
        if not IS_CAR:
            return True
        super().isoob()



class MissileRight(engine.GameObject):
    def __init__(self):
        global MISSILE_COUNT_RIGHT
        MISSILE_COUNT_RIGHT += 1
        super().__init__(15, GROUND_Y + 10, (SPEED * 2), 0, 'classic', 'blue')

    def delete(self):
        global MISSILE_COUNT_RIGHT
        MISSILE_COUNT_RIGHT -= 1
        super().delete()

class MissleVertical(engine.GameObject):
    def __init__(self, x_pos, y_pos, y_dir, color):
        super().__init__(x_pos, y_pos, 0, y_dir, 'classic', color)
        global MISSILE_COUNT_UP
        if self.color == 'blue':    # Will only include missiles from the Car
            MISSILE_COUNT_UP += 1

    def delete(self):
        global MISSILE_COUNT_UP
        if self.color == 'blue':
            MISSILE_COUNT_UP -= 1
        super().delete()

    # Checks to see if it is at ground level. If true it will explode and add a hole.
    def on_ground(self):
        if self.y > GROUND_Y:
            return
        else:
            engine.add_obj(Explosion(self.x, self.y))
            engine.add_obj(Hole(self.x))
            engine.del_obj(self)

    def step(self):
        super().step()
        self.on_ground()

class Explosion(engine.GameObject):
    def __init__(self, x, y):
        super().__init__(x, y, 0, 0, 'circle', 'orange')

    def step(self): # Will delete if age is more than 20
        super().step()
        if self.age > 20:
            self.delete()
            engine.del_obj(self)

    def draw(self):
        turtle.shapesize(outline=20)
        draw_shape = super().draw()
        turtle.resizemode("auto")
        return draw_shape

class UFO(engine.GameObject):
    def __init__(self):
        global IS_UFO
        IS_UFO = True
        self.hover_count = random.randint(3, 8)
        self.new_x_pos = 0
        self.new_y_pos = 0
        self.delay = 25
        self.fly_time = 100
        self.first_time = True
        super().__init__(-320, 100, 0, 0, 'circle', 'red')

    def ufo_missile(self):  # Random chance of adding a missile after a hover
        chance = random.randint(1, 2)
        if chance == 1:
            engine.add_obj(MissleVertical(self.x, self.y - 25, (-SPEED), 'red'))

    def random_move(self):  # Creates new random positions
        self.new_x_pos = (random.randint(-150, 150))
        self.new_y_pos = (random.randint(-140, 140))
        self.deltax = (self.new_x_pos - self.x) / 100
        self.deltay = (self.new_y_pos - self.y) / 100

    def exit_move(self):
        self.new_x_pos = MAX_X + 5
        self.new_y_pos = MAX_Y + 5
        self.deltax = (self.new_x_pos - self.x) / 100
        self.deltay = (self.new_y_pos - self.y) / 100

    def move(self):
        if self.first_time:
            self.random_move()
            self.first_time = False

        if self.fly_time == 0:
            if self.delay == 0:
                self.delay = 25
                self.fly_time = 100
                self.ufo_missile()
                self.hover_count -= 1
                if self.hover_count == 0:
                    self.exit_move()
                    return
                self.random_move()
                return
            else:
                self.delay -= 1
                return
        else:
            self.fly_time -= 1

        super().move()

    def delete(self):
        global IS_UFO
        IS_UFO = False
        super().delete()

    def in_ufo(self, x, y): # Collision Detection
        x1 = self.x - 12
        x2 = self.x + 12
        y1 = self.y - 12
        y2 = self.y + 12
        if (x1 <= x <= x2) and (y1 <= y <= y2):
            return True
        else:
            return False

class Mountain(engine.GameObject):
    def __init__(self, shape, color, speed):
        super().__init__(MAX_X, GROUND_Y, speed, 0, shape, color)

    def isoob(self):
        return False

    def move(self):
        if self.x < MIN_X - 638:
            self.x = 320
        super().move()

# COLLISION DETECTION

# Hole and Car
def hole_collision_cb(car, hole):
    if hole.in_hole( (car.x), (car.y) ) or hole.in_hole( (car.x + 30), (car.y) ):
        engine.del_obj(car)
        engine.add_obj(Explosion(car.x, car.y))
def hole_collision_cb2(hole, car):
    return hole_collision_cb(car, hole)

# Turtle and Car
def turt_collision_cb(car, turt):
    if turt.in_turtle( (car.x), (car.y) ) or turt.in_turtle( (car.x + 30), (car.y) ):
        engine.del_obj(car)
        engine.del_obj(turt)
        engine.add_obj(Explosion(turt.x, turt.y))
        engine.add_obj(Explosion(car.x, car.y))
def turt_collision_cb2(turt, car):
    return turt_collision_cb(car, turt)

# Right Missile and Turtle
def miss_turt_collision_cb(miss, turt):
    global score
    if turt.in_turtle( (miss.x), (miss.y-10) ):
        engine.add_obj(Explosion(miss.x, miss.y))
        engine.add_obj(Explosion(turt.x, turt.y))
        engine.del_obj(miss)
        engine.del_obj(turt)
        score += 10
        draw_score(False)
def miss_turt_collision_cb2(turt, miss):
    return miss_turt_collision_cb(miss, turt)

# UFO and Vertical Missile
def miss_ufo_collision_cb(miss, ufo):
    global score
    if ufo.in_ufo(miss.x, miss.y):
        engine.add_obj(Explosion(miss.x, miss.y))
        engine.add_obj(Explosion(ufo.x, ufo.y))
        engine.del_obj(miss)
        engine.del_obj(ufo)
        score += 100
        draw_score(False)
def miss_ufo_collision_cb2(ufo, miss):
    return miss_ufo_collision_cb(miss, ufo)

# UFO and Car
def car_ufo_collision_cb(car, ufo):
    global score
    if ufo.in_ufo(car.x, car.y + 20) or ufo.in_ufo(car.x + 30, car.y + 20):
        engine.add_obj(Explosion(car.x, car.y))
        engine.add_obj(Explosion(ufo.x, ufo.y))
        engine.del_obj(car)
        engine.del_obj(ufo)
        draw_score(True)
def car_ufo_collision_cb2(ufo, car):
    return car_ufo_collision_cb(car, ufo)

#UFO Missile and Car
def car_miss_collision_cb(car, miss):
    global score
    if (car.x < miss.x < car.x + 30) and (miss.y < car.y + 20) and miss.deltay == -SPEED:
        engine.add_obj(Explosion(car.x, car.y))
        engine.del_obj(car)
        engine.del_obj(miss)
        draw_score(True)
def car_miss_collision_cb2(miss, car):
    return car_miss_collision_cb(car, miss)


# RANDOM EVENT CALLBACKS
def hole_cb():
    objct = Hole(320)
    engine.add_obj(objct)

def turtle_cb():
    objct = EnemyTurtle()
    engine.add_obj(objct)

def UFO_cb():
    if IS_UFO:
        return
    objct = UFO()
    engine.add_obj(objct)


# KEYBOARD CALLBACK
def keyboard_cb(key):
    global IN_JUMP
    if key == 'e':
        engine.exit_engine()
    elif key == 'Return' and not IN_JUMP:
        IN_JUMP = True
    elif key == 'space'and not IN_JUMP and MISSILE_COUNT_UP < 2 and MISSILE_COUNT_RIGHT < 2 and IS_CAR:
        engine.add_obj(MissleVertical(15, GROUND_Y + 10, (SPEED * 2), 'blue'))
        engine.add_obj(MissileRight())


# MAIN SETUP

def draw_random_stars(star_count):
    for i in range(star_count):
        x = random.randint(MIN_X, MAX_X)
        y = random.randint(GROUND_Y, MAX_Y)
        turtle.goto(x, y)
        turtle.color('white')
        turtle.dot(2)

def draw_score(end):
    if end == False:
        score_string = "Score: " + str(score)
    else:
        score_string = "GAME OVER"
    turtle.goto(0, GROUND_Y-140)
    turtle.dot(150, 'brown')
    turtle.color('black')
    turtle.write(score_string, align='center', font=('Courier', 20, 'normal'))

def set_screen():
    engine.init_screen(WIDTH, HEIGHT)
    turtle.color('blue')
    turtle.write("Turtle Patrol", True, align='center', font=('Courier', 50, 'italic'))
    time.sleep(2)
    turtle.undo()
    turtle.bgcolor('black')


def start_game():
    global score
    engine.init_engine()
    engine.set_keyboard_handler(keyboard_cb)

    # Adds Ground and Car and Mountains
    engine.add_obj(Mountain('Mountain2', 'ivory4', (-SPEED/4)))
    engine.add_obj(Mountain('Mountain1', 'bisque', (-SPEED/2)))
    engine.add_obj(Ground(MIN_X, GROUND_Y, MAX_X, MIN_Y))
    engine.add_obj(Car())

    # Adds Wheels
    engine.add_obj(Wheel(2, GROUND_Y, -3))
    engine.add_obj(Wheel(15, GROUND_Y, 3))
    engine.add_obj(Wheel(28, GROUND_Y, -3))

    # Random Events
    engine.add_random_event(0.006, hole_cb)
    engine.add_random_event(0.007, turtle_cb)
    engine.add_random_event(0.004, UFO_cb)

    # Collision Detection
    engine.register_collision(Car, Hole, hole_collision_cb)
    engine.register_collision(Hole, Car, hole_collision_cb2)

    engine.register_collision(Car, EnemyTurtle, turt_collision_cb)
    engine.register_collision(EnemyTurtle, Car, turt_collision_cb2)

    engine.register_collision(MissileRight, EnemyTurtle, miss_turt_collision_cb)
    engine.register_collision(EnemyTurtle, MissileRight, miss_turt_collision_cb2)

    engine.register_collision(MissleVertical, UFO, miss_ufo_collision_cb)
    engine.register_collision(UFO, MissleVertical, miss_ufo_collision_cb2)

    engine.register_collision(Car, UFO, car_ufo_collision_cb)
    engine.register_collision(UFO, Car, car_ufo_collision_cb2)

    engine.register_collision(Car, MissleVertical, car_miss_collision_cb)
    engine.register_collision(MissleVertical, Car, car_miss_collision_cb2)

    # Score and Stars drawn
    draw_score(False)
    draw_random_stars(50)

    engine.engine()

# Game Starts
if __name__ == '__main__':
    set_screen()
    start_game()
