import pygame
import sys
import pickle
from Network import Network

pygame.font.init()
STAT_FONT = pygame.font.SysFont("comicsans", 20)
width = 500
height = 500
win = pygame.display.set_mode((width, height))
pygame.display.set_caption("Client")

clientNumber = 0

player_width = 10
player_height = 50
margin = 3
spawn_positions = ((margin, margin), (width - margin - player_width, height - margin - player_height))
colors = ((255, 0, 0), (0, 0, 255))


class Player():
    def __init__(self, player_id):
        self.player_id = player_id
        self.x, self.y = spawn_positions[player_id]
        self.width = player_width
        self.height = player_height
        self.color = colors[player_id]
        self.rect = self.get_rect()
        self.vel = 7
        self.fired_bullets = []
        self.fire_heat = 0
        self.shot = False
        self.score = 0

    def get_pos(self):
        return self.x, self.y, self.shot, self.score

    def set_pos(self, pos_list):
        self.x, self.y = pos_list

        self.rect = self.get_rect()

    def get_rect(self):
        return self.x, self.y, self.width, self.height

    def get_midpoint(self):
        return self.y + self.height / 2

    def draw(self, win):
        pygame.draw.rect(win, self.color, self.rect)

    def move(self):
        keys = pygame.key.get_pressed()
        self.shot = False

        if keys[pygame.K_UP] and not self.y <= 0 + self.vel:
            self.y -= self.vel

        if keys[pygame.K_DOWN] and not self.y >= height - self.vel - self.height:
            self.y += self.vel

        if keys[pygame.K_SPACE] and self.fire_heat == 0:
            self.fired_bullets.append(Bullet(self))
            self.fire_heat = 30
            self.color = (0, 0, 0)
            self.shot = True

        if self.fire_heat > 0:
            self.fire_heat -= 1
        elif self.fire_heat == 0:
            self.color = colors[self.player_id]
        else:
            pass

        self.rect = self.get_rect()


# defining a class for the bullets rather than non-object drawings, since later will have to check for collision
class Bullet():
    def __init__(self, player):
        self.target = 1 - player.player_id  # returns 0 if 1 and 1 if 0 respectively
        self.y = player.get_midpoint()
        self.x = margin + player_width if self.target == 1 else width - margin - player_width
        self.vel = 19 if self.target == 1 else -19
        self.color = (0, 255, 0)
        self.radius = 5
        self.circle = (self.x, self.y)

    def fly(self):
        self.x += self.vel

        self.circle = (round(self.x), round(self.y))

    def draw(self):
        pygame.draw.circle(win, self.color, self.circle, self.radius)


def redrawWindow(win, player, opponent):
    win.fill((255, 255, 255))
    bullet_label = STAT_FONT.render("Bullets: " + str(len(player.fired_bullets)), 1, (0, 0, 0))
    score_label = STAT_FONT.render("Net shots landed: " + str(player.score - opponent.score), 1, (0, 0, 0))
    player.draw(win)
    opponent.draw(win)
    if len(player.fired_bullets) > 0:
        for bullet in player.fired_bullets:
            bullet.draw()
    if len(opponent.fired_bullets) > 0:
        for bullet in opponent.fired_bullets:
            bullet.draw()

    win.blit(bullet_label, (15, 10))
    win.blit(score_label, (210, 10))
    pygame.display.update()


def main():
    run = True
    n = Network()
    pl_id = int(n.get_player_id())
    player = Player(pl_id)
    opponent = Player(1 - player.player_id)

    clock = pygame.time.Clock()

    while run:
        clock.tick(45)
        try:
            position = {player.player_id: player.get_pos()}
            game = n.send_player_pos_return_game_obj(position)
            print(game.Players_pos)
        except:
            run = False
            print("Couldn't retrieve game.")
            break

        if game.ready == False or len(game.Players_pos) != 2:   # run for waiting player
            win.fill((255, 255, 255))
            text = STAT_FONT.render("Waiting for second Client to connect...", 1, (0,0,0))
            win.blit(text, (180, 190))
            pygame.display.update()
            continue

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                sys.exit()

        if game.is_Over():
            if game.winner == player.player_id:
                menu_screen(winner="player")
            else:
                menu_screen(winner="opponent")

        player.move()
        opponent.set_pos(game.Players_pos[opponent.player_id][:2])  # moving opponent based on received game data
        if game.Players_pos[opponent.player_id][2] == True:
            opponent.fired_bullets.append(Bullet(opponent))
        opponent.score = game.Players_pos[opponent.player_id][3]

        for bullet in player.fired_bullets:     # making bullets fly, plus each client checks for own bullets to hit
            if bullet.target == 1:
                if bullet.x > opponent.x + opponent.width:
                    player.fired_bullets.remove(bullet)
                elif opponent.x - bullet.radius * 2 < bullet.x < opponent.x + opponent.width and \
                        opponent.y - bullet.radius < bullet.y < opponent.y + opponent.height + bullet.radius:
                    player.score += 1
                    player.fired_bullets.remove(bullet)
                else:
                    bullet.fly()
            elif bullet.target == 0:
                if bullet.x < opponent.x - bullet.radius * 2:
                    player.fired_bullets.remove(bullet)
                elif opponent.x - bullet.radius * 2 < bullet.x < opponent.x + opponent.width and \
                        opponent.y - bullet.radius < bullet.y < opponent.y + opponent.height + bullet.radius:
                    player.score += 1
                    player.fired_bullets.remove(bullet)
                else:
                    bullet.fly()

        for bullet in opponent.fired_bullets:
            if bullet.target == 1 and bullet.x > width + 100:
                opponent.fired_bullets.remove(bullet)
            elif bullet.target == 0 and bullet.x < - 100:
                opponent.fired_bullets.remove(bullet)
            else:
                bullet.fly()

        redrawWindow(win, player, opponent)


def menu_screen(winner=None):
    run = True
    clock = pygame.time.Clock()
    while run:
        clock.tick(60)
        win.fill((200, 200, 200))
        font = pygame.font.SysFont("comicsans", 60)
        text = font.render("Click to Play!", 1, (0, 0, 200))
        if winner == "player":
            win_label = font.render("YOU WON!", 1, (200, 30, 0))
            win.blit(win_label, (170, 10))
        elif winner == "opponent":
            win_label = font.render("You lost...", 1, (200, 30, 0))
            win.blit(win_label, (170, 10))
        else:
            pass
        win.blit(text, (140, 200))
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                run = False
    main()


menu_screen()
