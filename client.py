from ast import Tuple
from threading import Thread
from typing import List
import pygame
from chatbox import ChatBox, TextBox
from debug import debug
from network import Network
from player import Player
from projetil import Projetil

width, height = 1080, 720
win = pygame.display.set_mode((width, height), pygame.RESIZABLE)
pygame.display.set_caption("Client")

width, height = pygame.display.get_surface().get_size()
clientNumber = 0



def redrawWindow(win, players: List[Player], projectils: List[Projetil],  messages: List[str], chat_box: ChatBox, input_box: TextBox, camera):
    win.fill((255,255,255))
    for player in players:
        player.draw(win)
    for projetil in projectils:
        projetil.draw(win, players[0].x, players[0].y, camera)
    chat_box.draw(win)
    input_box.draw(win)        
    pygame.display.update()

def atualizaEstadoAtual(p: Player, n: Network, newBullet: Projetil | None = None) -> tuple[List[Player], List[Projetil]] | None:
    stateAtual = {
        "Players": str(p), 
        "NewBullet": str(newBullet) if newBullet is not None else "None"
        }
    stateAtual: dict | None = n.send(str(stateAtual))
    if stateAtual is None:
        print("Falhou")
        return
    allPlayers: List[Player] = []
    for index, idPlayer in enumerate(stateAtual['Players']):
        if idPlayer == p.id:
            # this is the player
            originalPlayer = stateAtual['Players'][idPlayer]
            p.atualizaEstadoAtual(originalPlayer['x'], originalPlayer['y'], originalPlayer['team'], originalPlayer['life'], originalPlayer['maxLife'])
    # First player is the player
    allPlayers.append(p)
    for idPlayer in stateAtual['Players']:
        if idPlayer == p.id:
            continue
        outroPlayer = stateAtual['Players'][idPlayer]
        color = (0, 0, 255) if outroPlayer['team'] == 'blue' else (255, 0, 0)
        allPlayers.append(Player(outroPlayer['x'],outroPlayer['y'],color, n, win, idPlayer, outroPlayer['team'], life=outroPlayer['life'], maxLife=outroPlayer['maxLife']))
    
    # Projectils
    allProjectils: List[Projetil] = []
    for idProjetil in stateAtual['Projectiles']:
            projetil = stateAtual['Projectiles'][idProjetil]
            pr = Projetil(projetil['userId'], projetil['x'], projetil['y'], projetil['moveX'], projetil['moveY'], projetil['team'], n, projetil['radius'], projetil['timeToDestroy'], projetil['atualTimeToDestroy'])
            allProjectils.append(pr)

    return allPlayers, allProjectils

def main():
    run = True
    n = Network()
    startPos = (0, 0)
    p = Player(startPos[0],startPos[1],(0,255,0), n, win)
    clock = pygame.time.Clock()
    
    # Configurações do chat
    chat_box = ChatBox(50, 50, 600, 400)
    input_box = TextBox(50, 460, 600, 30)
    
    response = atualizaEstadoAtual(p, n)
    if response is None:
        print("Desconectou no meio do jogo")
        return
    allPlayers: List[Player] = response[0]
    allProjectils: List[Projetil] = response[1]
    
    bulletTime = 0
    while run:
        newBullet = None
        if bulletTime > 0:
            bulletTime -= 1
        p = allPlayers[0]
         # Get the widht and height of the screen
        width, height = pygame.display.get_surface().get_size()        

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if bulletTime > 0:
                    continue
                bullet = p.shoot()
                if bullet is not None:
                    newBullet = bullet
            message = input_box.handle_event(event)
            if message is not None:
                chat_box.add_message(message)
                input_box.text = ''
            

        camera = (p.x, p.y)
        # update all projectils
        for projetil in allProjectils:
            projetil.x -= camera[0] - width // 2
            projetil.y -= camera[1] - height // 2
            
            dx = projetil.atualTimeToDestroy * projetil.moveX
            dy = projetil.atualTimeToDestroy * projetil.moveY

            projetil.x += dx
            projetil.y += dy

        # update all players
        for player in allPlayers:
            # update the player position and add a offset
            
            if player.id == p.id:
                # Center the player in the screen
                p.x = width / 2
                p.y = height / 2
            else:
                player.x -= camera[0] - width // 2
                player.y -= camera[1] - height // 2

            player.update()
        p.move()
        messages = ['Olá', 'Como vai? dsd sd sd sd s ds dsd sd s d', 'Tudo bem?', 'Estou bem', 'E você?', 'Também estou bem', 'Que bom', 'Sim', 'Até mais', 'Até mais', 'Tchau']
        chat_box.add_message('Olá')
        redrawWindow(win, allPlayers, allProjectils, messages, chat_box, input_box, camera)
        # Exemplo de uso
        p.atualTimeToReconect = 0
        response = atualizaEstadoAtual(p, n, newBullet)
        if response is None:
            return
        allPlayers, allProjectils = response

        clock.tick(60)

if __name__ == "__main__":
    main()