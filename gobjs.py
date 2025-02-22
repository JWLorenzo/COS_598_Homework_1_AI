import math
import random
import pygame

vec = pygame.math.Vector2
WIDTH = 800
HEIGHT = 800

RED_ENABLED = True
BLUE_ENABLED = False
YELLOW_ENABLED = False


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
        self.message_active = False
        self.message_cooldown = 0

    def pos(self):
        return (self.x, self.y)

    def move(self, dt, direction=1.0):
        self.x += direction * self.speed * dt * math.cos(self.heading)
        self.y += direction * self.speed * dt * math.sin(self.heading)

    def turn(self, dt, direction):
        self.heading += direction * self.turn_rate * dt

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
        speed=150,
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
        self.last_target = 0
        self.wander_rate = 0.3
        self.sight_angle = math.pi / 6
        self.target = vec(random.randint(0, WIDTH), random.randint(0, HEIGHT))

        x0 = self.x
        y0 = self.y
        x1 = self.x + math.cos(self.heading - self.sight_angle) * (
            self.radius + self.sight_distance
        )
        y1 = self.y + math.sin(self.heading - self.sight_angle) * (
            self.radius + self.sight_distance
        )
        x2 = self.x + math.cos(self.heading + self.sight_angle) * (
            self.radius + self.sight_distance
        )
        y2 = self.y + math.sin(self.heading + self.sight_angle) * (
            self.radius + self.sight_distance
        )

        self.sight_cone = [(x0, y0), (x1, y1), (x2, y2)]

    def orientation(self):
        ox = math.cos(self.heading)
        oy = math.sin(self.heading)
        return ox, oy

    def orientation_vector(self):
        ox, oy = self.orientation()
        return math.sqrt(ox**2 + oy**2)

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
        x1 = self.x + math.cos(self.heading - self.sight_angle) * (
            self.radius + self.sight_distance
        )
        y1 = self.y + math.sin(self.heading - self.sight_angle) * (
            self.radius + self.sight_distance
        )
        x2 = self.x + math.cos(self.heading + self.sight_angle) * (
            self.radius + self.sight_distance
        )
        y2 = self.y + math.sin(self.heading + self.sight_angle) * (
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

    def seek(self, target: pygame.math.Vector2) -> float:
        self.desired = (target - vec(self.pos())).normalize()
        target_angle = math.atan2(self.desired.y, self.desired.x)
        angle = target_angle - self.heading
        angle = (angle + math.pi) % (2 * math.pi) - math.pi
        if abs(angle) > self.wander_rate:
            angle = math.copysign(self.wander_rate, angle)

        return angle

    def update_message_state(self):
        if self.message_active:
            self.message_cooldown -= 1
            if self.message_cooldown <= 0:
                self.message_active = False

    def current_speed(self, goals) -> float:
        return self.orientation_vector() * (1 + 0.1 * sum(g.touched for g in goals))


class EnemyYellow(Enemy):
    def __init__(
        self,
        x,
        y,
        radius=10,
        speed=90,
        turn_rate=5.0,
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

    def wander(self) -> float:
        tick_count = pygame.time.get_ticks()
        self.dt = (tick_count - self.last_target) / 1000
        if tick_count - self.last_target > 300:
            self.target = vec(
                random.randint(25, WIDTH - 25),
                random.randint(25, HEIGHT - 25),
            )
            self.last_target = tick_count
        return self.seek(self.target)

    def ai(self, percept, goals, comms):
        if YELLOW_ENABLED:
            self.update_message_state()
            if not self.message_active:
                if comms["B"] == "Nyoom!":
                    self.message_active = True
                    self.message_cooldown = 120
                    return (
                        0,
                        0,
                        ("How is that desk chair so fast?", 2000, None),
                    )

            speed = self.current_speed(goals)
            if self.ticks > 0:
                self.ticks -= 1
                direction = self.seek(self.target)
                if self.ticks == 0:
                    comms.update(Y=None)
                return (direction, speed, None)
            elif self.ticks == 0 and percept[0]:
                self.ticks = 5
                player_x = self.x + percept[1][0] * percept[2]
                player_y = self.y + percept[1][1] * percept[2]
                self.target = vec(player_x, player_y)
                direction = self.seek(self.target)
                comms.update(Y=self.target)
                if not self.message_active:
                    self.message_active = True
                    self.message_cooldown = 120
                    return (
                        direction,
                        speed,
                        ("Get em' Blue!", 2000, None),
                    )
                else:
                    return (
                        direction,
                        speed,
                        None,
                    )

            direction = self.wander()
            comms.update(Y=None)
            return (direction, speed, None)
        else:
            return (0.0, 0.0, None)


class EnemyBlue(Enemy):
    def __init__(
        self,
        x,
        y,
        radius=10,
        speed=90,
        turn_rate=3.0,
        heading=0.0,
        sight_distance=180,
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
        self.sight_angle = math.pi / 32
        self.cooldown = 0
        self.tick_set = 60
        self.wander_rate = 0.4
        self.sight_distance_original = 180
        self.last_message = ""
        self.voiceline = False

    # This is the ai routing for the type B enemy.
    def ai(self, percept, goals, comms):
        if BLUE_ENABLED:
            self.update_message_state()
            if comms["B"] == "Nyoom!":
                comms.update(B=None)
            speed = self.current_speed(goals)
            if self.ticks > 0:
                self.ticks -= 1
                if self.sight_distance > self.sight_distance_original:
                    self.sight_distance -= self.sight_dec
                else:
                    self.sight_distance = self.sight_distance_original
                direction = self.seek(self.target)
                return (
                    direction,
                    speed * 4.5 * (self.ticks / self.tick_set),
                    None,
                )
            elif (self.ticks == 0) and (percept[0]):
                self.sight_dec = (
                    self.sight_distance - self.sight_distance_original
                ) / self.tick_set

                self.ticks = self.tick_set

                player_x = self.x + percept[1][0] * percept[2]
                player_y = self.y + percept[1][1] * percept[2]
                self.target = vec(player_x, player_y)
                direction = self.seek(self.target)
                comms.update(B="Nyoom!")
                if not self.message_active:
                    self.message_active = True
                    self.message_cooldown = 120
                    return (
                        direction,
                        speed * 4.5 * (self.ticks / self.tick_set),
                        ("Nyoom!", 2000),
                    )
                else:
                    return (
                        direction,
                        speed * 4.5 * (self.ticks / self.tick_set),
                        None,
                    )
            elif (self.ticks == 0) and comms["Y"] != None:
                self.sight_dec = (
                    self.sight_distance - self.sight_distance_original
                ) / self.tick_set

                self.ticks = self.tick_set
                # self.dart_ratio_result = self.dist_ratio(self.target)

                self.target = comms["Y"]
                self.last_message = "Y"
                direction = self.seek(self.target)
                if not self.message_active:
                    self.message_active = True
                    self.message_cooldown = 120
                    return (
                        direction,
                        speed * 4.5 * (self.ticks / self.tick_set),
                        ("On it Boss!", 2000),
                    )
                else:
                    return (
                        direction,
                        speed * 4.5 * (self.ticks / self.tick_set),
                        None,
                    )
            elif (self.ticks == 0) and comms["R"] != None:
                self.sight_dec = (
                    self.sight_distance - self.sight_distance_original
                ) / self.tick_set

                self.ticks = self.tick_set
                # self.dart_ratio_result = self.dist_ratio(self.target)

                self.target = comms["R"]
                self.last_message = "R"
                direction = self.seek(self.target)
                if not self.message_active:
                    self.message_active = True
                    self.message_cooldown = 120
                    return (
                        direction,
                        speed * 4.5 * (self.ticks / self.tick_set),
                        ("On my way!", 2000),
                    )
                else:
                    return (
                        direction,
                        speed * 4.5 * (self.ticks / self.tick_set),
                        None,
                    )

            self.sight_distance += sum([x.touched for x in goals])

            comms.update(B=None)
            return (
                0.5,
                0.0,
                None,
            )
        else:
            return (0.0, 0.0, None)


class EnemyRed(Enemy):
    def __init__(
        self,
        x,
        y,
        radius=10,
        speed=400,
        turn_rate=90,
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

    def check_screen_edges(self) -> dict:
        return {
            "left": self.x <= self.radius,
            "right": self.x >= WIDTH - self.radius,
            "top": self.y <= self.radius,
            "bottom": self.y >= HEIGHT - self.radius,
        }

    def ai(self, percept, goals, comms):
        speed = self.current_speed(goals)
        if RED_ENABLED:
            direction = 0.0
            if self.ticks > 0:
                self.ticks -= 1
                direction = self.seek(self.target)
                if self.ticks == 0:
                    comms.update(R=None)
                return (direction, 0, None)
            elif self.ticks == 0 and percept[0]:
                self.ticks = 30
                player_x = self.x + percept[1][0] * percept[2]
                player_y = self.y + percept[1][1] * percept[2]
                self.target = vec(player_x, player_y)
                comms.update(R=self.target)
                return (direction, 0, ("I see them!", 2000, None))
            elif self.ticks == 0 and not percept[0]:
                screen_edge = self.check_screen_edges()
                heading_checker = self.heading % math.pi
                if screen_edge["left"]:
                    if heading_checker >= math.pi / 2 and heading_checker <= math.pi:
                        direction = vec(
                            math.cos(heading_checker) + math.pi / 2,
                            math.sin(heading_checker),
                        ).magnitude()
                    elif heading_checker >= 0 and heading_checker <= math.pi / 2:
                        direction = vec(
                            math.cos(heading_checker) - math.pi / 2,
                            math.sin(heading_checker),
                        ).magnitude()
                elif screen_edge["right"]:
                    if heading_checker <= math.pi / 2 and heading_checker >= 0:
                        direction = vec(
                            math.cos(heading_checker),
                            math.sin(heading_checker) - math.pi / 2,
                        ).magnitude()
                    elif heading_checker >= math.pi / 2 and heading_checker <= math.pi:
                        direction = vec(
                            math.cos(heading_checker) + math.pi / 2,
                            math.sin(heading_checker),
                        ).magnitude()
                elif screen_edge["top"]:
                    if heading_checker <= math.pi / 2 and heading_checker >= 0:
                        direction = vec(
                            math.cos(heading_checker),
                            math.sin(heading_checker) - math.pi / 4,
                        ).magnitude()
                    elif heading_checker >= math.pi / 2 and heading_checker <= math.pi:
                        direction = -vec(
                            math.cos(heading_checker) - math.pi / 4,
                            math.sin(heading_checker),
                        ).magnitude()
                elif screen_edge["bottom"]:
                    if heading_checker <= math.pi / 2 and heading_checker >= 0:
                        direction = vec(
                            math.cos(heading_checker),
                            math.sin(heading_checker) + math.pi / 4,
                        ).magnitude()
                    elif heading_checker <= math.pi and heading_checker >= math.pi / 2:
                        direction = vec(
                            math.cos(heading_checker),
                            math.sin(heading_checker) - math.pi / 4,
                        ).magnitude()

                return (direction % math.pi, speed, None)
            comms.update(R=None)
            return (0.0, speed, None)
        else:
            comms.update(R=None)
            return (0.0, 0.0, None)
