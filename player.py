from turtle import width
import uuid
import pygame
from network import Network
from projetil import Projetil


class Player():

    def __init__(self, x, y, color, n: Network, win: pygame.Surface, id: str = str(uuid.uuid4()), team: str = 'red', width = 25, height = 25, life: int = 4, maxLife: int = 4):
        self.id = id
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.rect = (x,y,width,height)
        self.vel = 3
        self.moveX = 0
        self.moveY = 0
        self.n = n
        self.team = team
        self.life = life
        self.maxLife = maxLife
    
    def __str__(self):
        player = dict()
        player[self.id] = {
            'x': self.x,
            'y': self.y,
            'team': self.team,
            'moveX': self.moveX,
            'moveY': self.moveY,
            'atualTimeToReconect': 0,
            'life': self.life,
            'maxLife': self.maxLife,
        }
        return str(player)

    def draw(self, win):
        pygame.draw.rect(win, self.color, self.rect)
        # Draw a life bar thats decreses when the player is hit, life = maxLife = 100%
        pygame.draw.rect(win, (0, 255, 0), (self.x, self.y - 10, self.width * (self.life / self.maxLife), 5))

    def move(self):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_LEFT]:
            self.moveX -= self.vel

        if keys[pygame.K_RIGHT]:
            self.moveX += self.vel

        if keys[pygame.K_UP]:
            self.moveY -= self.vel

        if keys[pygame.K_DOWN]:
            self.moveY += self.vel
    
    def shoot(self):
        width, height = pygame.display.get_surface().get_size()
        # Get the position of the mouse when the player click the mouse
        mousePos = pygame.mouse.get_pos()
        # Get the position of the player
        playerPos = (width / 2, height / 2)
        # Get the distance between the player and the mouse
        distance = (mousePos[0] - playerPos[0], mousePos[1] - playerPos[1])
        # Get the magnitude of the distance
        magnitude = (distance[0] ** 2 + distance[1] ** 2) ** 0.5
        # Normalize the distance
        distance = (distance[0] / magnitude, distance[1] / magnitude)
        # Get the vector of the direction of the bullet from the player to the mouse
        bulletVector = (distance[0] * 10, distance[1] * 10)        

        # Create a bullet
        bullet = Projetil(self.id, self.x, self.y, bulletVector[0], bulletVector[1],self.team, self.n)
        return bullet

    def atualizaEstadoAtual(self, x: int, y: int, team: str, life: int, maxLife: int):
        self.x = x
        self.y = y
        self.team = team
        if team == 'red':
            self.color = (255, 0, 0)
        else:
            self.color = (0, 0, 255)
        self.moveX = 0
        self.moveY = 0
        self.atualTimeToReconect = 0
        self.life = life
        self.maxLife = maxLife
    
    def update(self):
        self.rect = (self.x, self.y, self.width, self.height)
