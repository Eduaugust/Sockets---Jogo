from ast import Tuple
from threading import Thread, local
from time import time
from typing import List
import pygame
from chatbox import ChatBox, TextBox
from debug import debug
from network import Network
from player import Player
from projetil import Projetil
from mapa import DominationData, inicializa_mapa, retorna_mapa

width, height = 1080, 720
win = pygame.display.set_mode((width, height))
pygame.display.set_caption("Client")

width, height = pygame.display.get_surface().get_size()
clientNumber = 0

clock = pygame.time.Clock()

def draw_gradient_rect(win, x, y, width, height, color1, color2, percentage):
    # Calcula a quantidade de cada cor
    color1_width = int(width * percentage)
    color2_width = width - color1_width

    try:


        # Desenha a primeira cor
        pygame.draw.rect(win, color1, pygame.Rect(x, y, color1_width, height))

        # Desenha a segunda cor
        pygame.draw.rect(win, color2, pygame.Rect(x + color1_width, y, color2_width, height))
    
    except Exception as e:
        print(e)
        print(color1, color2, percentage)

def redrawWindow(win, players: List[Player], projectils: List[Projetil], chat_box: ChatBox, input_box: TextBox, kill_box: ChatBox, dominationData: DominationData,mapa,camera):
    win.fill((255,255,255))
    color1, color2, percentage = -1, -1, -1
    for objeto in mapa:
        # Apply the offset of the camera
        localizacaoX = objeto.x - camera[0] + width // 2
        localizacaoY = objeto.y - camera[1] + height // 2

        # Define as cores
        color1 = dominationData.blueColor if dominationData.team_dominating == 'blue' else dominationData.redColor if dominationData.team_dominating == 'red' else dominationData.grayColor
        color2 = dominationData.redColor if dominationData.progress_time_red != 0 else dominationData.blueColor

        # Define a porcentagem da primeira cor
        percentage = (time() - dominationData.progress_time_blue) / 10 if dominationData.progress_time_blue != 0 else (time() - dominationData.progress_time_red) / 10 if dominationData.progress_time_red != 0 else 0
        percentage = 1 - percentage
        # Desenha o retângulo com gradiente
     
        if objeto.tipo == 'R':
            pygame.draw.rect(win, (200, 100, 100), pygame.Rect(localizacaoX, localizacaoY, 100, 100))
        elif objeto.tipo == 'B':
            pygame.draw.rect(win, (100, 100, 200), pygame.Rect(localizacaoX, localizacaoY, 100, 100))
        elif objeto.tipo == '#':
            pygame.draw.rect(win, (200, 200, 200), pygame.Rect(localizacaoX, localizacaoY, 100, 100))
        elif objeto.tipo == '*':
            draw_gradient_rect(win, localizacaoX, localizacaoY, 50, 50, color1, color2, percentage)
        else:
            pygame.draw.rect(win, (255, 255, 255), pygame.Rect(localizacaoX, localizacaoY, 100, 100))
    for player in players:
        player.draw(win)
    for projetil in projectils:
        projetil.draw(win)
    chat_box.draw(win)
    input_box.draw(win)   
    kill_box.draw(win)   
    debug("FPS: " + str(clock.get_fps())[0:4] + str(color1) + str(color2) + str(percentage), 10, 10)


    pygame.display.update()

def atualizaEstadoAtual(p: Player, n: Network, chat_box: ChatBox, kill_box: ChatBox, newBullet: Projetil | None = None, message: str | None = None) -> tuple[List[Player], List[Projetil], DominationData] | None:
    message = p.userName + ": " + message if message is not None else "None"
    stateAtual = {
        "Players": str(p), 
        "NewBullet": str(newBullet) if newBullet is not None else "None",
        "NewMessage": message,
        }
    stateAtual: dict | None = n.send(str(stateAtual))
    if stateAtual is None:
        print("Falhou")
        return
    
    # --------- Players ---------

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
        allPlayers.append(Player(outroPlayer['userName'], outroPlayer['x'],outroPlayer['y'],color, n, win, idPlayer, outroPlayer['team'], life=outroPlayer['life'], maxLife=outroPlayer['maxLife']))
    
    # --------- Projectils ---------
    allProjectils: List[Projetil] = []
    for idProjetil in stateAtual['Projectiles']:
            projetil = stateAtual['Projectiles'][idProjetil]
            pr = Projetil(projetil['userId'], projetil['userName'], projetil['x'], projetil['y'], projetil['moveX'], projetil['moveY'], projetil['team'], n, projetil['radius'], projetil['timeToDestroy'], projetil['atualTimeToDestroy'])
            allProjectils.append(pr)

    # --------- Chat ---------
    for idMessage in stateAtual['ChatMessages']:
        if stateAtual['ChatMessages'][idMessage] != 'None':
            chat_box.add_message(stateAtual['ChatMessages'][idMessage], idMessage)


    # --------- Kill Messages ---------
    kill_box.messages = []
    kill_box.idMessage = []
    for idMessage in stateAtual['KillMessages']:
        kill_box.add_message(stateAtual['KillMessages'][idMessage], idMessage)

    # --------- Dominating ---------
    # "TeamWon": "None", # None, Blue, Red
    # "TeamDominating": 'None',
    # "TimeToBlueWin": [0, 0], # time already dominating, time started in last capture
    # "TimeToRedWin": [0, 0], # time already dominating, time started in last capture
    # "ProgressTimeBlue": 0,
    # "ProgressTimeRed": 0,

    dominationData = {
        "TeamWon": stateAtual['TeamWon'],
        "TeamDominating": stateAtual['TeamDominating'],
        "TimeToBlueWin": stateAtual['TimeToBlueWin'],
        "TimeToRedWin": stateAtual['TimeToRedWin'],
        "ProgressTimeBlue": stateAtual['ProgressTimeBlue'],
        "ProgressTimeRed": stateAtual['ProgressTimeRed'],
    }

    dominationData = DominationData(dominationData)

    return allPlayers, allProjectils, dominationData

def main():
    run = True
    n = Network()
    startPos = (0, 0)
    p = Player("Teste" , startPos[0],startPos[1],(0,255,0), n, win)

    # --------- Mapa ---------
    mapa = inicializa_mapa()
    
    # --------- Chat ---------
    width, height = pygame.display.get_surface().get_size() 
    chat_box = ChatBox(50, height - 70 - 10 * 22 , width * 0.3, height - 10)
    input_box = TextBox(50, height - 40, width * 0.3, 22)

    # --------- Kill Messages ---------
    kill_box = ChatBox(width - 200, 0, 200, 200)

    # --------- Atualiza Estado Atual ---------
    
    response = atualizaEstadoAtual(p, n, chat_box, kill_box)
    if response is None:
        print("Desconectou no meio do jogo")
        return
    allPlayers: List[Player] = response[0]
    allProjectils: List[Projetil] = response[1]
    dominationData: DominationData = response[2]
    
    bulletTime = 0 # Time para atirar dnv
    # --------- Loop --------- 
    while run:
        newBullet = None
        if bulletTime > 0:
            bulletTime -= 1
        p = allPlayers[0]
        messageToSend = None         
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
            
            message = input_box.handle_event(event)
            if message is not None:
                messageToSend = message
                input_box.text = ''
            if not input_box.active and event.type == pygame.MOUSEBUTTONDOWN:
                if bulletTime > 0:
                    continue
                bullet = p.shoot()
                bulletTime = 60 * 0.5
                if bullet is not None:
                    newBullet = bullet
            

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
        if not input_box.active:
            p.move()
        redrawWindow(win, allPlayers, allProjectils, chat_box, input_box, kill_box, dominationData, mapa, camera)
        # Exemplo de uso
        p.atualTimeToReconect = 0
        response = atualizaEstadoAtual(p, n, chat_box, kill_box, newBullet, messageToSend)
        if response is None:
            return
        allPlayers, allProjectils, dominationData = response

        clock.tick(30)

if __name__ == "__main__":
    main()