import math
import random
import pygame

vec = pygame.math.Vector2
WIDTH = 800
HEIGHT = 600


def randomBinomial() -> float:
    return random.random() - random.random()


class GObj:

    def __init__(
        self,
        x,
        y,
        radius,
        speed,
        turn_rate,
        heading,
        sight_distance,
        color="white",
        fill=0,
    ):
        self.x = x
        self.y = y
        self.radius = radius
        self.speed = speed
        self.turn_rate = turn_rate
        self.heading = heading
        self.sight_distance = sight_distance
        self.color = color
        self.fill = fill
        self.target = vec(random.randint(0, WIDTH), random.randint(0, HEIGHT))
        self.last_target = 0
        self.wander_rate = 0.3
        self.last_speed = 0
        self.last_direction = 0
        self.chase = 0

    def orientation(self):
        ox = math.cos(self.heading)
        oy = math.sin(self.heading)
        return ox, oy

    def orientation_vector(self):
        ox, oy = self.orientation()
        return math.sqrt(ox**2 + oy**2)

    def pos(self):
        return (self.x, self.y)

    def move(self, dt, direction=1.0):
        self.x += direction * self.speed * dt * math.cos(self.heading)
        self.y += direction * self.speed * dt * math.sin(self.heading)

    def turn(self, dt, direction):
        self.heading += direction * self.turn_rate * dt

    # def can_see(self, gameobj):
    #     ox = gameobj.x
    #     oy = gameobj.y

    #     x1 = self.x
    #     y1 = self.y
    #     x2 = x1+math.cos(self.heading)*self.sight_distance
    #     y2 = y1+math.sin(self.heading)*self.sight_distance
    #     D = x1*y2 - x2*y1
    #     I = gameobj.radius**2 * self.sight_distance**2 - D**2
    #     return I >= 0
    def check_collision(self, gameobj):
        distance = math.sqrt((gameobj.x - self.x) ** 2 + (gameobj.y - self.y) ** 2)
        if distance < self.radius + gameobj.radius:
            return True
        else:
            return False

    def onscreen(self, rect):
        if (
            self.x + self.radius >= rect[0]
            and self.x - self.radius <= rect[2]
            and self.y + self.radius >= rect[1]
            and self.y - self.radius <= rect[3]
        ):
            return True
        else:
            return False

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (self.x, self.y), self.radius, self.fill)


class Player(GObj):
    def __init__(
        self,
        x,
        y,
        radius=10,
        speed=100,
        turn_rate=5.0,
        heading=0,
        sight_distance=0,
        color="darkorchid",
        fill=0,
    ):
        GObj.__init__(
            self, x, y, radius, speed, turn_rate, heading, sight_distance, color, fill
        )

    def draw(self, screen):
        GObj.draw(self, screen)
        pygame.draw.line(
            screen,
            "black",
            (self.x, self.y),
            (
                self.x + math.cos(self.heading) * self.radius,
                self.y + math.sin(self.heading) * self.radius,
            ),
            2,
        )


class Goal(GObj):
    def __init__(
        self,
        x,
        y,
        radius=20,
        speed=0,
        turn_rate=0.0,
        heading=0.0,
        sight_distance=0.0,
        color="red",
        fill=3,
    ):
        GObj.__init__(
            self, x, y, radius, speed, turn_rate, heading, sight_distance, color, fill
        )
        self.touched = False

    def touch(self):
        self.color = "green"
        self.touched = True

    def is_touched(self):
        return self.touched


class Enemy(GObj):
    def __init__(
        self,
        x,
        y,
        radius,
        speed,
        turn_rate,
        heading,
        sight_distance,
        color,
        fill,
        goals,
    ):
        GObj.__init__(
            self, x, y, radius, speed, turn_rate, heading, sight_distance, color, fill
        )
        self.goals = goals
        self.sight_cone_color_clear = "white"
        self.sight_cone_color_obj = "fuchsia"
        self.sight_cone_color = self.sight_cone_color_clear

        x0 = self.x
        y0 = self.y
        x1 = self.x + math.cos(self.heading - math.pi / 6) * (
            self.radius + self.sight_distance
        )
        y1 = self.y + math.sin(self.heading - math.pi / 6) * (
            self.radius + self.sight_distance
        )
        x2 = self.x + math.cos(self.heading + math.pi / 6) * (
            self.radius + self.sight_distance
        )
        y2 = self.y + math.sin(self.heading + math.pi / 6) * (
            self.radius + self.sight_distance
        )

        self.sight_cone = [(x0, y0), (x1, y1), (x2, y2)]

    def draw(self, screen):
        xy0 = self.sight_cone[0]
        xy1 = self.sight_cone[1]
        xy2 = self.sight_cone[2]

        pygame.draw.line(
            screen, self.sight_cone_color, (xy0[0], xy0[1]), (xy1[0], xy1[1]), 1
        )
        pygame.draw.line(
            screen, self.sight_cone_color, (xy1[0], xy1[1]), (xy2[0], xy2[1]), 1
        )
        pygame.draw.line(
            screen, self.sight_cone_color, (xy2[0], xy2[1]), (xy0[0], xy0[1]), 1
        )

        GObj.draw(self, screen)

    def update(self, gameobj):
        ox = gameobj.x
        oy = gameobj.y

        x0 = self.x
        y0 = self.y
        x1 = self.x + math.cos(self.heading - math.pi / 6) * (
            self.radius + self.sight_distance
        )
        y1 = self.y + math.sin(self.heading - math.pi / 6) * (
            self.radius + self.sight_distance
        )
        x2 = self.x + math.cos(self.heading + math.pi / 6) * (
            self.radius + self.sight_distance
        )
        y2 = self.y + math.sin(self.heading + math.pi / 6) * (
            self.radius + self.sight_distance
        )

        self.sight_cone[0] = (x0, y0)
        self.sight_cone[1] = (x1, y1)
        self.sight_cone[2] = (x2, y2)

        for i in range(len(self.sight_cone)):
            x1 = self.sight_cone[i][0]
            y1 = self.sight_cone[i][1]
            x2 = self.sight_cone[(i + 1) % len(self.sight_cone)][0]
            y2 = self.sight_cone[(i + 1) % len(self.sight_cone)][1]
            if (x2 - x1) * (oy - y1) - (y2 - y1) * (ox - x1) <= 0:
                self.sight_cone_color = self.sight_cone_color_clear
                return (False, None)
        self.sight_cone_color = self.sight_cone_color_obj
        dx = ox - self.x
        dy = oy - self.y
        dist = math.sqrt(dx * dx + dy * dy)
        dx /= dist
        dy /= dist
        return (True, (dx, dy), dist)

    # Base class AI routine
    def ai(self, percept, goals, comms):

        return (0.0, 0.0, None)

    def seek(self, target: vec):
        self.desired = (target - vec(self.pos())).normalize()
        target_angle = math.atan2(self.desired.y, self.desired.x)
        angle = target_angle - self.heading
        if abs(angle) > self.wander_rate:
            angle = math.copysign(self.wander_rate, angle)

        return angle

    def wander(self):
        tick_count = pygame.time.get_ticks()
        if tick_count - self.last_target > 500:
            self.target = vec(random.randint(0, WIDTH), random.randint(0, HEIGHT))
            self.last_target = tick_count
        return self.seek(self.target)


class EnemyYellow(Enemy):
    def __init__(
        self,
        x,
        y,
        radius=10,
        speed=40,
        turn_rate=3.0,
        heading=0.0,
        sight_distance=120,
        color="yellow",
        fill=0,
        goals=[],
    ):
        Enemy.__init__(
            self,
            x,
            y,
            radius,
            speed,
            turn_rate,
            heading,
            sight_distance,
            color,
            fill,
            goals,
        )
        self.ticks = 0

    # # This is ai routine for the type A enemy.
    # def ai(self, percept, goals, comms):
    #     # direction = randomBinomial() * self.turn_rate
    #     speed = self.orientation_vector()
    #     print(self.heading)
    #     # turn, speed = self.wander()
    #     if self.ticks > 0:
    #         self.ticks -= 1
    #     elif self.ticks == 0 and percept[0]:
    #         print("Chasing")
    #         self.ticks = 60 * 4
    #         player_x = self.x + percept[1][0] * percept[2]
    #         player_y = self.y + percept[1][1] * percept[2]
    #         self.last_direction = self.seek(vec(player_x, player_y))
    #         self.target = vec(player_x, player_y)
    #         print(f"Percept0: {percept[0]}")
    #         print(f"Percept1: {percept[1]}")
    #         print(f"Percept2: {percept[2]}")
    #         print(f"Player coords: {player_x}, {player_y}")
    #         print(f"Self Coords: {self.x}, {self.y}")
    #         return (self.last_direction, speed, ("Don't make me chase you!", 2000))
    #     # direction = self.wander()
    #     return (self, 0, None)

    def ai(self, percept, goals, comms):
        speed = self.orientation_vector()
        direction = self.wander()
        if self.ticks > 0:
            self.ticks -= 1
            if self.chase and self.ticks == 0 and percept[0]:
                self.chase = 0
                self.target = vec(random.randint(0, WIDTH), random.randint(0, HEIGHT))
        elif self.ticks == 0 and percept[0]:
            print("Chasing")
            self.ticks = 60 * 4
            self.chase = 0
            player_x = self.x + percept[1][0] * percept[2]
            player_y = self.y + percept[1][1] * percept[2]
            print(f"Player Coords: {player_x}, {player_y}")
            direction = self.seek(vec(player_x, player_y))
            return (direction, speed, ("Don't make me chase you!", 2000))
        if self.chase:
            direction = self.seek(self.target)
        else:
            direction = self.wander()
        return (direction, 0, None)


class EnemyBlue(Enemy):
    def __init__(
        self,
        x,
        y,
        radius=10,
        speed=90,
        turn_rate=3.0,
        heading=0.0,
        sight_distance=120,
        color="dodgerblue",
        fill=0,
        goals=[],
    ):
        Enemy.__init__(
            self,
            x,
            y,
            radius,
            speed,
            turn_rate,
            heading,
            sight_distance,
            color,
            fill,
            goals,
        )

        self.ticks = 0

    # This is the ai routing for the type B enemy.
    def ai(self, percept, goals, comms):
        if self.ticks > 0:
            self.ticks -= 1
        elif self.ticks == 0 and percept[0]:
            self.ticks = 60 * 4
            return (0.0, 0.0, ("I see you!", 2000))
        return (0.0, 0.0, None)


class EnemyRed(Enemy):
    def __init__(
        self,
        x,
        y,
        radius=10,
        speed=90,
        turn_rate=3.0,
        heading=0.0,
        sight_distance=120,
        color="red",
        fill=0,
        goals=[],
    ):
        Enemy.__init__(
            self,
            x,
            y,
            radius,
            speed,
            turn_rate,
            heading,
            sight_distance,
            color,
            fill,
            goals,
        )

        self.ticks = 0

    # This is the ai routing for the type B enemy.
    def ai(self, percept, goals, comms):
        if self.ticks > 0:
            self.ticks -= 1
        elif self.ticks == 0 and percept[0]:
            self.ticks = 60 * 4
            return (0.0, 0.0, ("Enemy!", 2000))
        return (0.0, 0.0, None)
