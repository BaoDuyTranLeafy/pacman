import copy

import AStar
from matrix import matrix
import pygame
import math
import DFS


class PacmanGame:
    def __init__(self):
        pygame.init()
        self.WIDTH = 900
        self.HEIGHT = 950
        self.screen = pygame.display.set_mode([self.WIDTH, self.HEIGHT])
        self.timer = pygame.time.Clock()
        self.fps = 60
        self.font = pygame.font.Font('freesansbold.ttf', 20)
        self.level = copy.deepcopy(matrix)
        self.color = 'blue'
        self.PI = math.pi
        self.player_images = []
        for i in range(1, 5):
            self.player_images.append(pygame.transform.scale(pygame.image.load(f'pacman_image/{i}.png'), (45, 45)))
        self.icon = pygame.image.load("pacman_image/1.png")
        pygame.display.set_icon(self.icon)
        self.player_x = 75 - 23
        self.player_y = 70 - 24
        self.direction = 0
        self.x, self.y = 2, 2
        self.counter = 0
        self.flicker = False
        # R, L, U, D
        self.turns_allowed = [False, False, False, False]
        self.direction_command = 0
        self.player_speed = 2
        self.score = 0
        self.powerup = False
        self.power_counter = 0
        self.targets = [(self.player_x, self.player_y), (self.player_x, self.player_y), (self.player_x, self.player_y), (self.player_x, self.player_y)]
        self.moving = False
        self.ghost_speeds = [2, 2, 2, 2]
        self.startup_counter = 0
        self.lives = 3
        self.game_over = False
        self.game_won = False

    def draw_misc(self):
        score_text = self.font.render(f'Score: {self.score}', True, 'white')
        self.screen.blit(score_text, (10, 920))
        if self.powerup:
            pygame.draw.circle(self.screen, 'blue', (140, 930), 15)
        for i in range(self.lives):
            self.screen.blit(pygame.transform.scale(self.player_images[0], (30, 30)), (650 + i * 40, 915))
        if self.game_over:
            pygame.draw.rect(self.screen, 'white', [50, 200, 800, 300], 0, 10)
            pygame.draw.rect(self.screen, 'dark gray', [70, 220, 760, 260], 0, 10)
            gameover_text = self.font.render('Game over! Space bar to restart!', True, 'red')
            self.screen.blit(gameover_text, (100, 300))
        if self.game_won:
            pygame.draw.rect(self.screen, 'white', [50, 200, 800, 300], 0, 10)
            pygame.draw.rect(self.screen, 'dark gray', [70, 220, 760, 260], 0, 10)
            gameover_text = self.font.render('Victory! Space bar to restart!', True, 'green')
            self.screen.blit(gameover_text, (100, 300))

    def check_collisions(self, scor, power, power_count):
        num1 = (self.HEIGHT - 50) // 32
        num2 = self.WIDTH // 30
        if 0 < self.player_x < 870:
            if self.level[self.center_y // num1][self.center_x // num2] == 1:
                self.level[self.center_y // num1][self.center_x // num2] = 0
                scor += 10
            if self.level[self.center_y // num1][self.center_x // num2] == 2:
                self.level[self.center_y // num1][self.center_x // num2] = 0
                scor += 50
                power = True
                power_count = 0

        return scor, power, power_count

    def draw_board(self):
        num1 = (self.HEIGHT - 50) // 32  # 28
        num2 = (self.WIDTH // 30)  # 30
        for i in range(len(self.level)):
            for j in range(len(self.level[i])):
                if self.level[i][j] == 1:
                    pygame.draw.circle(self.screen, 'white', (j * num2 + (0.5 * num2), i * num1 + (0.5 * num1)), 4)
                if self.level[i][j] == 2 and not self.flicker:
                    pygame.draw.circle(self.screen, 'white', (j * num2 + (0.5 * num2), i * num1 + (0.5 * num1)), 10)
                if self.level[i][j] == 3:
                    pygame.draw.line(self.screen, self.color, (j * num2 + (0.5 * num2), i * num1),
                                     (j * num2 + (0.5 * num2), i * num1 + num1), 3)
                if self.level[i][j] == 4:
                    pygame.draw.line(self.screen, self.color, (j * num2, i * num1 + (0.5 * num1)),
                                     (j * num2 + num2, i * num1 + (0.5 * num1)), 3)
                if self.level[i][j] == 5:
                    pygame.draw.arc(self.screen, self.color,
                                    [(j * num2 - (num2 * 0.4)) - 2, (i * num1 + (0.5 * num1)), num2, num1],
                                    0, self.PI / 2, 3)
                if self.level[i][j] == 6:
                    pygame.draw.arc(self.screen, self.color,
                                    [(j * num2 + (num2 * 0.5)), (i * num1 + (0.5 * num1)), num2, num1], self.PI / 2,
                                    self.PI, 3)
                if self.level[i][j] == 7:
                    pygame.draw.arc(self.screen, self.color,
                                    [(j * num2 + (num2 * 0.5)), (i * num1 - (0.4 * num1)), num2, num1], self.PI,
                                    3 * self.PI / 2, 3)
                if self.level[i][j] == 8:
                    pygame.draw.arc(self.screen, self.color,
                                    [(j * num2 - (num2 * 0.4)) - 2, (i * num1 - (0.4 * num1)), num2, num1],
                                    3 * self.PI / 2, 2 * self.PI, 3)
                if self.level[i][j] == 9:
                    pygame.draw.line(self.screen, 'white', (j * num2, i * num1 + (0.5 * num1)),
                                     (j * num2 + num2, i * num1 + (0.5 * num1)), 3)

    def draw_player(self):
        # 0-RIGHT, 1-LEFT, 2-UP, 3-DOWN
        if self.direction == 0:
            self.screen.blit(self.player_images[self.counter // 5], (self.player_x, self.player_y))
        elif self.direction == 1:
            self.screen.blit(pygame.transform.flip(self.player_images[self.counter // 5], True, False), (self.player_x, self.player_y))
        elif self.direction == 2:
            self.screen.blit(pygame.transform.rotate(self.player_images[self.counter // 5], 90), (self.player_x, self.player_y))
        elif self.direction == 3:
            self.screen.blit(pygame.transform.rotate(self.player_images[self.counter // 5], 270), (self.player_x, self.player_y))

    def check_position(self, centerx, centery):
        turns = [False, False, False, False]
        num1 = (self.HEIGHT - 50) // 32
        num2 = (self.WIDTH // 30)
        num3 = 15

        if centerx // 30 < 29:
            if self.direction == 0:
                if self.level[centery // num1][(centerx - num3) // num2] < 3:
                    turns[1] = True
            if self.direction == 1:
                if self.level[centery // num1][(centerx + num3) // num2] < 3:
                    turns[0] = True
            if self.direction == 2:
                if self.level[(centery + num3) // num1][centerx // num2] < 3:
                    turns[3] = True
            if self.direction == 3:
                if self.level[(centery - num3) // num1][centerx // num2] < 3:
                    turns[2] = True

            if self.direction == 2 or self.direction == 3:
                if 12 <= centerx % num2 <= 18:
                    if self.level[(centery + num3) // num1][centerx // num2] < 3:
                        turns[3] = True
                    if self.level[(centery - num3) // num1][centerx // num2] < 3:
                        turns[2] = True
                if 12 <= centery % num1 <= 18:
                    if self.level[centery // num1][(centerx - num2) // num2] < 3:
                        turns[1] = True
                    if self.level[centery // num1][(centerx + num2) // num2] < 3:
                        turns[0] = True

            if self.direction == 0 or self.direction == 1:
                if 12 <= centerx % num2 <= 18:
                    if self.level[(centery + num1) // num1][centerx // num2] < 3:
                        turns[3] = True
                    if self.level[(centery - num1) // num1][centerx // num2] < 3:
                        turns[2] = True
                if 12 <= centery % num1 <= 18:
                    if self.level[centery // num1][(centerx - num3) // num2] < 3:
                        turns[1] = True
                    if self.level[centery // num1][(centerx + num3) // num2] < 3:
                        turns[0] = True
        else:
            turns[0] = True
            turns[1] = True

        return turns

    def move_player(self, play_x, play_y):
        # r, l, u, d
        if self.direction == 0 and self.turns_allowed[0]:
            play_x += self.player_speed
        elif self.direction == 1 and self.turns_allowed[1]:
            play_x -= self.player_speed
        if self.direction == 2 and self.turns_allowed[2]:
            play_y -= self.player_speed
        elif self.direction == 3 and self.turns_allowed[3]:
            play_y += self.player_speed
        return play_x, play_y

    def move_pacman(self, player_x, player_y, x, y):
        player_x = player_x + 23
        player_y = player_y + 24
        start = (x, y)
        goal = (30, 2)

        solver = AStar.AStar(start, goal)
        path = solver.astar()
        print(path)
        new_x, new_y = player_x, player_y
        if path:
            if path[0] == path[-1]:
                new_x, new_y = player_x, player_y
            else:
                dx, dy = path[0]
                dx1, dy1 = path[1]
                if dy1 - dy == 1 and dx1 - dx == 0:
                    new_x = player_x + 1 * self.player_speed
                    self.direction = 0
                elif dy1 - dy == -1 and dx1 - dx == 0:
                    new_x = player_x + -1 * self.player_speed
                    self.direction = 1
                if dx1 - dx == -1 and dy1 - dy == 0:
                    new_y = player_y + -1 * self.player_speed
                    self.direction = 2
                elif dx1 - dx == 1 and dy1 - dy == 0:
                    new_y = player_y + 1 * self.player_speed
                    self.direction = 3
                if new_x == solver.cd_array[dx1][dy1][0] and new_y == solver.cd_array[dx1][dy1][1]:
                    x, y = dx1, dy1
                    path.pop(0)
        new_x = new_x - 23
        new_y = new_y - 24
        return new_x, new_y, x, y, self.direction

    def run_game(self):
        run = True
        while run:
            self.timer.tick(self.fps)
            if self.counter < 19:
                self.counter += 1
                if self.counter > 3:
                    self.flicker = False
            else:
                self.counter = 0
                self.flicker = True
            if self.powerup and self.power_counter < 600:
                self.power_counter += 1
            elif self.powerup and self.power_counter >= 600:
                self.power_counter = 0
                self.powerup = False
            if self.startup_counter < 180 and not self.game_over and not self.game_won:
                self.moving = False
                self.startup_counter += 1
            else:
                self.moving = True

            self.screen.fill('black')
            self.draw_board()  # Assuming draw_board is a method of your class
            self.center_x = self.player_x + 23
            self.center_y = self.player_y + 24

            self.game_won = True
            for i in range(len(self.level)):
                if 1 in self.level[i] or 2 in self.level[i]:
                    self.game_won = False
            self.player_circle = pygame.draw.circle(self.screen, 'black', (self.center_x, self.center_y), 20, 2)
            self.draw_player()  # Assuming draw_player is a method of your class
            self.draw_misc()  # Assuming draw_misc is a method of your class

            self.turns_allowed = self.check_position(self.center_x, self.center_y)  # Assuming check_position is a method of your class
            if self.moving:
                self.player_x, self.player_y, self.x, self.y, self.direction = self.move_pacman(self.player_x, self.player_y, self.x, self.y)
                # player_x, player_y = self.move_player(player_x, player_y)

            self.score, self.powerup, self.power_counter = self.check_collisions(self.score, self.powerup, self.power_counter)

            # for event in pygame.event.get():
            #     if event.type == pygame.QUIT:
            #         run = False
            #     if event.type == pygame.KEYDOWN:
            #         if event.key == pygame.K_RIGHT:
            #             direction_command = 0
            #         if event.key == pygame.K_LEFT:
            #             direction_command = 1
            #         if event.key == pygame.K_UP:
            #             direction_command = 2
            #         if event.key == pygame.K_DOWN:
            #             direction_command = 3
            #         if event.key == pygame.K_SPACE and (game_over or game_won):
            #             powerup = False
            #             power_counter = 0
            #             lives -= 1
            #             startup_counter = 0
            #             player_x = 450
            #             player_y = 663
            #             direction = 0
            #             direction_command = 0
            #             score = 0
            #             lives = 3
            #             level = copy.deepcopy(matrix)
            #             game_over = False
            #             game_won = False
            #
            #     if event.type == pygame.KEYUP:
            #         if event.key == pygame.K_RIGHT and direction_command == 0:
            #             direction_command = direction
            #         if event.key == pygame.K_LEFT and direction_command == 1:
            #             direction_command = direction
            #         if event.key == pygame.K_UP and direction_command == 2:
            #             direction_command = direction
            #         if event.key == pygame.K_DOWN and direction_command == 3:
            #             direction_command = direction
            #
            # if direction_command == 0 and turns_allowed[0]:
            #     direction = 0
            # if direction_command == 1 and turns_allowed[1]:
            #     direction = 1
            # if direction_command == 2 and turns_allowed[2]:
            #     direction = 2
            # if direction_command == 3 and turns_allowed[3]:
            #     direction = 3

            if self.player_x > 900:
                self.player_x = -47
            elif self.player_x < -50:
                self.player_x = 897

            pygame.display.flip()

        pygame.quit()


if __name__ == "__main__":
    pacman_game = PacmanGame()
    pacman_game.run_game()
