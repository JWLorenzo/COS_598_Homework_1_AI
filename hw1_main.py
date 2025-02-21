import pygame
import pygame.freetype
import math
import random
import gobjs


class Display:
    def __init__(self, screen, clock):
        self.screen = screen
        self.clock = clock
        self.run = True
        self.delta = 0
        self.font = None

    def draw_gobj(self, gobj):
        pygame.draw.circle(self.screen, gobj.color, gobj.pos(), gobj.radius)

    def draw_text(self, msg, x, y, color):
        surface, rect = self.font.render(msg, color)
        self.screen.blit(surface, (x - rect.w // 2, y - rect.h))


def init_display(sw, sh):
    pygame.init()
    screen = pygame.display.set_mode((sw, sh))
    clock = pygame.time.Clock()
    display = Display(screen, clock)
    display.font = pygame.freetype.Font("JuliaMono-Bold.ttf", 18)
    return display


def handle_input(keys, dt, player, win_w, win_h):
    pos = player.pos()
    r = player.radius

    if keys[pygame.K_a]:
        player.turn(dt, -1)
    elif keys[pygame.K_d]:
        player.turn(dt, 1)
    if keys[pygame.K_w]:
        player.move(dt)
    elif keys[pygame.K_s]:
        player.move(dt, -1.0)


def gather_perecpts(enemy, player):
    return enemy.can_see(player)


def game_loop(display):

    win_w, win_h = pygame.display.get_window_size()
    d_rect = (0, 0, win_w, win_h)

    # NOTE: You are welcome to modify some aspects of the following
    # The player and enemy classes do take additional parameters
    # which are currently set to defaults. You are welcome to
    # override them to get a different scenario.

    # Possible Player start locations (x, y, heading)
    start_locs = [
        (50, 50, math.pi / 4),
        (win_w // 2, 50, math.pi / 2),
        (win_w - 50, 50, 3 * math.pi / 4),
        (50, win_h // 2, 0),
        (win_w - 50, win_h // 2, math.pi),
        (50, win_h - 50, -math.pi / 4),
        (win_w // 2, win_h - 50, -math.pi / 2),
        (win_w - 50, win_h - 50, -3 * math.pi / 4),
    ]
    # Randomly choose one.
    player_start = random.choice(start_locs)
    player = gobjs.Player(player_start[0], player_start[1], heading=player_start[2])

    # Goals. The number passed into the Goal contructor are the x,y coords.
    goals = [
        gobjs.Goal(200, 200),
        gobjs.Goal(win_w - 200, 200),
        gobjs.Goal(200, win_h - 200),
        gobjs.Goal(win_w - 200, win_h - 200),
        gobjs.Goal(win_w // 2, win_h // 2),
    ]

    # The enemies.
    enemy1 = gobjs.EnemyYellow(win_w // 2 + 50, win_h // 2, heading=0)
    enemy2 = gobjs.EnemyBlue(win_w // 2 - 50, win_h // 2, heading=math.pi)
    enemy3 = gobjs.EnemyRed(win_w // 2, win_h // 2 - 50, heading=math.pi / 2)
    enemies = [enemy1, enemy2, enemy3]
    comms = {"R": None, "B": None, "Y": None}

    tick = 0
    goal_count = 0
    winner = "Draw"
    msgs = []

    # You probably don't need to modify anything in the main loop
    while display.run:
        dt = display.clock.tick(60) / 1000

        # Check event queue for quit
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                display.run = False

        display.screen.fill("black")

        next_msgs = []
        for msg in msgs:
            if pygame.time.get_ticks() - msg[2] < msg[0][1]:
                display.draw_text(
                    msg[0][0], msg[1].x, msg[1].y - (msg[1].radius + 3), msg[1].color
                )
                next_msgs.append(msg)
        msgs = next_msgs

        for g in goals:
            if not g.is_touched():
                if g.check_collision(player):
                    g.touch()
                    goal_count += 1
                    if goal_count == len(goals):
                        display.run = False
                        winner = "Player"
            g.draw(display.screen)

        # Call Enemy AI and draw
        for e in enemies:
            mt = e.ai(e.update(player), goals, comms)
            e.turn(dt, mt[0])
            e.move(dt, mt[1])
            if mt[2] is not None:
                msgs.append((mt[2], e, pygame.time.get_ticks()))
            if e.check_collision(player):
                display.run = False
                winner = "AI"
            if not e.onscreen(d_rect):
                display.run = False
                winner = "Player"
            e.draw(display.screen)

        # Move and draw the player
        keys = pygame.key.get_pressed()
        handle_input(keys, dt, player, win_w, win_h)
        player.draw(display.screen)

        if not player.onscreen(d_rect):
            winner = "AI"
            display.run = False

        pygame.display.flip()

    print(f"The winner is the {winner}.")


def main():
    display = init_display(800, 800)
    game_loop(display)


if __name__ == "__main__":
    main()
