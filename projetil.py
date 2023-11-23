import time
import uuid

import pygame
from debug import debug

from network import Network


class Projetil:
    def __init__(self, userId: str, x: int, y: int, moveX: int, moveY: int, team: str, n: Network, radius: int = 10, timeToDestroy: int = 100, atualTimeToDestroy: int = 0, damage: int = 1) -> None:
        self.id = str(uuid.uuid4())
        self.userId = userId
        self.x = x
        self.y = y
        self.color = (255, 0, 0) if team == 'red' else (0, 0, 255)
        self.moveX = moveX
        self.moveY = moveY
        self.n = n
        self.team = team
        self.radius = radius
        self.timeToDestroy = timeToDestroy
        self.atualTimeToDestroy = atualTimeToDestroy
        self.damage = damage

    def __str__(self) -> str:
        return str({
            self.id: {
                'userId': self.userId,
                'x': self.x,
                'y': self.y,
                'team': self.team,
                'moveX': self.moveX,
                'moveY': self.moveY,
                'radius': self.radius,
                'timeToDestroy': self.timeToDestroy,
                'atualTimeToDestroy': self.atualTimeToDestroy,
                'damage': self.damage
            }
        })

    def draw(self, win, centroRelativoX, centroRelativoY, camera) -> None:
        # Format to self.y have only 3 decimals
        debug(f"Projetil: - {int(self.x)}, {int(self.y)}, {centroRelativoX, centroRelativoY, camera}", 10, 10)
        pygame.draw.circle(win, self.color, radius=self.radius, center=(self.x, self.y))
    