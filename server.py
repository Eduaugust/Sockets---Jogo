import json
from random import randint
import socket
from time import time
from typing import List
from uuid import uuid4
from mapa import inicializa_mapa
from player import Player, ServerPlayer

localIP     = "127.0.0.1"
localPort   = 3000
bufferSize  = 16384

# --------- Last time ---------

lastTime = time()

# --------- Mapa ---------

mapa = inicializa_mapa()                                      

# --------- Bases ---------

baseAzul = [
    [4707, 1205],
    [4917, 1205],
    [4917, 1820],
    [4707, 1820],
]

baseVermelha = [
    [51, 1205],
    [261, 1205],
    [261, 1820],
    [51, 1820],
]

# --------- Estados ---------

stateGlobal = {}

exampleState = {
    "Players": {

    },
        
    "Projectiles": {

    },
    "ChatMessages": {

    },
    "KillMessages": {

    },
    "TeamWon": "None", # None, Blue, Red
    "TeamDominating": 'None',
    "TimeToBlueWin": [0, 0], # time already dominating, time started in last capture
    "TimeToRedWin": [0, 0], # time already dominating, time started in last capture
    "ProgressTimeBlue": 0,
    "ProgressTimeRed": 0,
}

global atualState

idOfPlayer = None


def updateTeamDominating() -> None:
    global atualState
    red = 0
    blue = 0
    # Print state like team won and others
    # Clear terminal os
    print("\033c")
    print(f"TeamDominating: {stateGlobal[messageDict['HostId']]['TeamDominating']}",)
    print(f"TimeToBlueWin: {stateGlobal[messageDict['HostId']]['TimeToBlueWin']}",)
    print(f"TimeToRedWin: {stateGlobal[messageDict['HostId']]['TimeToRedWin']}",)
    print(f"ProgressTimeBlue: {stateGlobal[messageDict['HostId']]['ProgressTimeBlue']}",)
    print(f"ProgressTimeRed: {stateGlobal[messageDict['HostId']]['ProgressTimeRed']}",)
    print(f"TeamWon: {stateGlobal[messageDict['HostId']]['TeamWon']}",)
    print(f"Time to blue win: {time() - stateGlobal[messageDict['HostId']]['TimeToBlueWin'][1] + stateGlobal[messageDict['HostId']]['TimeToBlueWin'][0] }")
    print(f"Time to red win: {time() - stateGlobal[messageDict['HostId']]['TimeToRedWin'][1] + stateGlobal[messageDict['HostId']]['TimeToRedWin'][0] }")
    # Update the team dominating
    timeToWon = 10 * 1
    for idPlayer in stateGlobal[messageDict['HostId']]["Players"]:
        tentandoDominar = checkColsionPlayerAndAsterisk(stateGlobal[messageDict['HostId']]["Players"][idPlayer]["x"], stateGlobal[messageDict['HostId']]["Players"][idPlayer]["y"], 0, 0)
        if not tentandoDominar:
            continue
        if stateGlobal[messageDict['HostId']]["Players"][idPlayer]["team"] == 'red':
            red += 1
        else:
            blue += 1

    if red > 0 and blue == 0:
        if stateGlobal[messageDict['HostId']]["TeamDominating"] == 'blue':
            if stateGlobal[messageDict['HostId']]["ProgressTimeRed"] == 0:
                stateGlobal[messageDict['HostId']]["ProgressTimeRed"] = time()
            else:
                if time() - stateGlobal[messageDict['HostId']]["ProgressTimeRed"] >= 10:
                    # Save the blue time
                    stateGlobal[messageDict['HostId']]["TimeToBlueWin"][0] = time() - stateGlobal[messageDict['HostId']]["TimeToBlueWin"][1]

                    # Set new time to red
                    stateGlobal[messageDict['HostId']]["TimeToRedWin"][1] = time()
                    stateGlobal[messageDict['HostId']]["ProgressTimeRed"] = 0
                    stateGlobal[messageDict['HostId']]["ProgressTimeBlue"] = 0
                    stateGlobal[messageDict['HostId']]["TeamDominating"] = 'red'
        elif stateGlobal[messageDict['HostId']]["TeamDominating"] == 'Red':
            stateGlobal[messageDict['HostId']]["ProgressTimeRed"] = 0
            if stateGlobal[messageDict['HostId']]["ProgressTimeBlue"] != 0:
                # insiro o tempo que o time azul dominou
                stateGlobal[messageDict['HostId']]['ProgressTimeBlue'] += 1/15
                if stateGlobal[messageDict['HostId']]["ProgressTimeBlue"] - time() < 0:
                    stateGlobal[messageDict['HostId']]["ProgressTimeBlue"] = 0

        else: 
            # TeamDominating is None

            # Init the progress time
            if stateGlobal[messageDict['HostId']]["ProgressTimeRed"] == 0 and stateGlobal[messageDict['HostId']]["ProgressTimeBlue"] == 0:
                stateGlobal[messageDict['HostId']]["ProgressTimeRed"] = time()
            elif time() - stateGlobal[messageDict['HostId']]["ProgressTimeRed"] >= 10:
                # Set new time to red
                stateGlobal[messageDict['HostId']]["TimeToRedWin"][1] = time()
                stateGlobal[messageDict['HostId']]["ProgressTimeRed"] = 0
                stateGlobal[messageDict['HostId']]["ProgressTimeBlue"] = 0
                stateGlobal[messageDict['HostId']]["TeamDominating"] = 'red'
            
    elif blue > 0 and red == 0:
        if stateGlobal[messageDict['HostId']]["TeamDominating"] == 'red':
            if stateGlobal[messageDict['HostId']]["ProgressTimeBlue"] == 0:
                stateGlobal[messageDict['HostId']]["ProgressTimeBlue"] = time()
                stateGlobal[messageDict['HostId']]["ProgressTimeRed"] = 0
            else:
                if time() - stateGlobal[messageDict['HostId']]["ProgressTimeBlue"] >= 10:
                    # Save the red time
                    stateGlobal[messageDict['HostId']]["TimeToRedWin"][0] = time() - stateGlobal[messageDict['HostId']]["TimeToRedWin"][1]

                    # Set new time to blue
                    stateGlobal[messageDict['HostId']]["TimeToBlueWin"][1] = time()
                    stateGlobal[messageDict['HostId']]["ProgressTimeRed"] = 0
                    stateGlobal[messageDict['HostId']]["ProgressTimeBlue"] = 0
                    stateGlobal[messageDict['HostId']]["TeamDominating"] = 'blue'
        elif stateGlobal[messageDict['HostId']]["TeamDominating"] == 'blue':
            stateGlobal[messageDict['HostId']]["ProgressTimeBlue"] = 0
            if stateGlobal[messageDict['HostId']]["ProgressTimeRed"] != 0:
                # insiro o tempo que o time vermelho dominou
                stateGlobal[messageDict['HostId']]['ProgressTimeRed'] += 1/15
                if stateGlobal[messageDict['HostId']]["ProgressTimeRed"] - time() < 0:
                    stateGlobal[messageDict['HostId']]["ProgressTimeRed"] = 0
        else:
            # TeamDominating is None

            # Init the progress time
            if stateGlobal[messageDict['HostId']]["ProgressTimeRed"] == 0 and stateGlobal[messageDict['HostId']]["ProgressTimeBlue"] == 0:
                stateGlobal[messageDict['HostId']]["ProgressTimeBlue"] = time()
                stateGlobal[messageDict['HostId']]["ProgressTimeRed"] = 0
            elif time() - stateGlobal[messageDict['HostId']]["ProgressTimeBlue"] >= 10:
                # Set new time to blue
                stateGlobal[messageDict['HostId']]["TimeToBlueWin"][1] = time()
                stateGlobal[messageDict['HostId']]["ProgressTimeRed"] = 0
                stateGlobal[messageDict['HostId']]["ProgressTimeBlue"] = 0
                stateGlobal[messageDict['HostId']]["TeamDominating"] = 'blue'

            
    elif blue > 0 and red > 0:
        # If progress time is not 0 in red
        if stateGlobal[messageDict['HostId']]["ProgressTimeRed"] != 0:
            # Progress time dont move, anything do not move
            stateGlobal[messageDict['HostId']]["ProgressTimeRed"] += 1/15
        elif stateGlobal[messageDict['HostId']]["ProgressTimeBlue"] != 0:
            # Progress time dont move, anything do not move
            stateGlobal[messageDict['HostId']]["ProgressTimeBlue"] += 1/15
    elif blue == 0 and red == 0:
        # If progress time is not 0, then, reset it if the time is greater than 10 seconds
        if stateGlobal[messageDict['HostId']]["ProgressTimeRed"] != 0:
            stateGlobal[messageDict['HostId']]["ProgressTimeRed"] += 1/15
            if time() - stateGlobal[messageDict['HostId']]["ProgressTimeRed"] < 0:
                stateGlobal[messageDict['HostId']]["ProgressTimeRed"] = 0
        if stateGlobal[messageDict['HostId']]["ProgressTimeBlue"] != 0:
            stateGlobal[messageDict['HostId']]["ProgressTimeBlue"] += 1/15
            if time() - stateGlobal[messageDict['HostId']]["ProgressTimeBlue"] < 0:
                stateGlobal[messageDict['HostId']]["ProgressTimeBlue"] = 0
    # Check if someone won, just if progress time is 0

    if stateGlobal[messageDict['HostId']]["ProgressTimeRed"] == 0 and stateGlobal[messageDict['HostId']]["ProgressTimeBlue"] == 0:
        if stateGlobal[messageDict['HostId']]["TimeToBlueWin"][1] != 0 and  time() - stateGlobal[messageDict['HostId']]["TimeToBlueWin"][1] + stateGlobal[messageDict['HostId']]["TimeToBlueWin"][0]  >= timeToWon:
                # Blue won
                stateGlobal[messageDict['HostId']]["TimeToBlueWin"][0] = 0
                stateGlobal[messageDict['HostId']]["TimeToBlueWin"][1] = 0
                stateGlobal[messageDict['HostId']]["TimeToRedWin"][0] = 0
                stateGlobal[messageDict['HostId']]["TimeToRedWin"][1] = 0
                stateGlobal[messageDict['HostId']]["TeamDominating"] = 'blue'
                stateGlobal[messageDict['HostId']]["TeamWon"] = 'blue'
        elif stateGlobal[messageDict['HostId']]["TimeToRedWin"][1] != 0 and time() - stateGlobal[messageDict['HostId']]["TimeToRedWin"][1] + stateGlobal[messageDict['HostId']]["TimeToRedWin"][0]  >= timeToWon:
                # Red won
                stateGlobal[messageDict['HostId']]["TimeToBlueWin"][0] = 0
                stateGlobal[messageDict['HostId']]["TimeToBlueWin"][1] = 0
                stateGlobal[messageDict['HostId']]["TimeToRedWin"][0] = 0
                stateGlobal[messageDict['HostId']]["TimeToRedWin"][1] = 0
                stateGlobal[messageDict['HostId']]["TeamDominating"] = 'red'
                stateGlobal[messageDict['HostId']]["TeamWon"] = 'red'

def checkColisionWithMapa(x, y, moveX, moveY) -> List[int]:
    # Check if the player will colide with the map
    returnValue = [1, 1]
    for objeto in mapa:
        if objeto.tipo == '#':
            # Check if the player will colide with the obstacle
            if objeto.x - 25 <= x + moveX <= objeto.x + 50:
                if objeto.y - 25 <= y <= objeto.y + 50:
                    returnValue[0] = 0
            if objeto.y - 25 <= y + moveY <= objeto.y + 50:
                if objeto.x - 25 <= x <= objeto.x + 50:
                    returnValue[1] = 0
    return returnValue

def checkColisionWithBase(x, y, moveX, moveY) -> List[int]:
    # Check if the player will colide with the map
    returnValue = [1, 1]
    for objeto in mapa:
        if objeto.tipo == 'R' or objeto.tipo == 'B':
            # Check if the player will colide with the obstacle
            if objeto.x - 25 <= x + moveX <= objeto.x + 50:
                if objeto.y - 25 <= y <= objeto.y + 50:
                    returnValue[0] = 0
            if objeto.y - 25 <= y + moveY <= objeto.y + 50:
                if objeto.x - 25 <= x <= objeto.x + 50:
                    returnValue[1] = 0
    return returnValue

def colisionBetweenPlayersAndBases() -> None:
    # Colision between players and bases
    for idPlayer in stateGlobal[messageDict['HostId']]["Players"]:
        lastStatePlayer = stateGlobal[messageDict['HostId']]["Players"][idPlayer]
        # Check if the player will colide with the base
        if lastStatePlayer["team"] == 'red':
            # Check if the player will colide with the base azul
            if baseAzul[0][0] <= lastStatePlayer["x"] <= baseAzul[1][0]:
                if baseAzul[0][1] <= lastStatePlayer["y"] <= baseAzul[2][1]:
                    randomX = randint(baseVermelha[0][0], baseVermelha[1][0])
                    randomY = randint(baseVermelha[0][1], baseVermelha[2][1])
                    lastStatePlayer["x"] = randomX
                    lastStatePlayer["y"] = randomY
                    stateGlobal[messageDict['HostId']]["Players"][idPlayer] = lastStatePlayer
                    addKillMessage(f"{lastStatePlayer['userName']} suicided")
        else:
            # Check if the player will colide with the base vermelha
            if baseVermelha[0][0] <= lastStatePlayer["x"] <= baseVermelha[1][0]:
                if baseVermelha[0][1] <= lastStatePlayer["y"] <= baseVermelha[2][1]:
                    randomX = randint(baseAzul[0][0], baseAzul[1][0])
                    randomY = randint(baseAzul[0][1], baseAzul[2][1])
                    lastStatePlayer["x"] = randomX
                    lastStatePlayer["y"] = randomY
                    stateGlobal[messageDict['HostId']]["Players"][idPlayer] = lastStatePlayer
                    addKillMessage(f"{lastStatePlayer['userName']} suicided")

def checkColsionPlayerAndAsterisk(x, y, moveX, moveY) -> bool:
    # Check if the player will colide with the map
    returnValue = [1, 1]
    for objeto in mapa:
        if objeto.tipo == '*':
            # Check if the player will colide with the obstacle
            if objeto.x - 25 <= x + moveX <= objeto.x + 50:
                if objeto.y - 25 <= y <= objeto.y + 50:
                    return True
            if objeto.y - 25 <= y + moveY <= objeto.y + 50:
                if objeto.x - 25 <= x <= objeto.x + 50:
                    return True
    return False

def createPlayer(msg: dict) -> None:
    global idOfPlayer
    if idOfPlayer is None:
        idOfPlayer = str(uuid4())

    newPlayer = ServerPlayer(msg['username'], 0, 0, 0, idOfPlayer)
    msg["Players"] = dict()
    msg["Players"][idOfPlayer] = newPlayer.toDict()
    # If the number of blue is greater than red, then, the new player will be red, else, blue
    red = 0
    blue = 0
    for idPlayer in stateGlobal[messageDict['HostId']]["Players"]:
        if stateGlobal[messageDict['HostId']]["Players"][idPlayer]["team"] == 'red':
            red += 1
        else:
            blue += 1
    team = 'red' if red  < blue else 'blue'

    # new player
    stateGlobal[messageDict['HostId']]["Players"][idOfPlayer] = msg['Players'][idOfPlayer]
    stateGlobal[messageDict['HostId']]["Players"][idOfPlayer]["team"] = team
    stateGlobal[messageDict['HostId']]["Players"][idOfPlayer]["timeStamp"] = str(time())

    if stateGlobal[messageDict['HostId']]["Players"][idOfPlayer]["team"] == 'red':
        # Add new player to base vermelha in a random position inside the base
        randomX = randint(baseVermelha[0][0], baseVermelha[1][0])
        randomY = randint(baseVermelha[0][1], baseVermelha[2][1])
        msg['Players'][idOfPlayer]["x"] = randomX
        msg['Players'][idOfPlayer]["y"] = randomY
    else:
        # Add new player to base azul in a random position inside the base
        randomX = randint(baseAzul[0][0], baseAzul[1][0])
        randomY = randint(baseAzul[0][1], baseAzul[2][1])
        msg['Players'][idOfPlayer]["x"] = randomX
        msg['Players'][idOfPlayer]["y"] = randomY
    stateGlobal[messageDict['HostId']]["Players"][idOfPlayer] = msg['Players'][idOfPlayer]

def debug():
    for idHost in stateGlobal:
        print(idHost == messageDict['HostId'], len(stateGlobal[idHost]["Players"]))

def createProjetil(msg: dict) -> None:
    if not 'NewBullet' in msg.keys():
        return
    newBullet = msg['NewBullet'] if msg['NewBullet'] != "None" else False
    if newBullet:
        # Add new bullet to projectiles
        idOfBullet = next(iter(newBullet))
        stateGlobal[messageDict['HostId']]["Projectiles"][idOfBullet] = newBullet[idOfBullet]
        stateGlobal[messageDict['HostId']]["Projectiles"][idOfBullet]["atualTimeToDestroy"] = 0

def addMessageToChat(msg: dict) -> None:
    # If have the key NewMessage, then, add the message to chat
    if 'NewMessage' in msg.keys():
        newMessage = msg['NewMessage']
        # Add new message to chat
        idOfMessage = str(time())
        stateGlobal[messageDict['HostId']]["ChatMessages"][idOfMessage] = newMessage

    # --------- Remove mensagem se tiver mais de 10 mensagens ---------
    message_to_remove = []
    if len(stateGlobal[messageDict['HostId']]["ChatMessages"]) > 10:
        # Remover apenas as mensagens mais antigas
        keys = list(stateGlobal[messageDict['HostId']]["ChatMessages"].keys())
        keys.sort()
        for idMessage in keys[:len(stateGlobal[messageDict['HostId']]["ChatMessages"]) - 10]:
            message_to_remove.append(idMessage)
    for idMessage in message_to_remove:
        del stateGlobal[messageDict['HostId']]["ChatMessages"][idMessage]        

def addKillMessage(killMessage: str) -> None:
    idOfMessage = str(time())
    stateGlobal[messageDict['HostId']]["KillMessages"][idOfMessage] = killMessage

def colisionBetweenPlayersAndProjectiles() -> None:
    # Colision between players and projectiles
    to_remove = []
    for idPlayer in stateGlobal[messageDict['HostId']]["Players"]:
        for idProjetil in stateGlobal[messageDict['HostId']]["Projectiles"]:
            lastStatePlayer = stateGlobal[messageDict['HostId']]["Players"][idPlayer]
            lastStateProjetil = stateGlobal[messageDict['HostId']]["Projectiles"][idProjetil]
            if lastStatePlayer["team"] != lastStateProjetil["team"]:
                posicaoRealxX = lastStateProjetil["x"] + lastStateProjetil["moveX"] * lastStateProjetil["atualTimeToDestroy"]
                posicaoRealY = lastStateProjetil["y"] + lastStateProjetil["moveY"] * lastStateProjetil["atualTimeToDestroy"]
                # Mas coloque um offset de 25, porque o player tem 25 de largura e 25 de altura
                if lastStatePlayer["x"] - 25 <= posicaoRealxX <= lastStatePlayer["x"] + 25:
                    if lastStatePlayer["y"] - 25 <= posicaoRealY <= lastStatePlayer["y"] + 25:
                        to_remove.append(idProjetil)
                        lastStatePlayer["life"] -= lastStateProjetil["damage"]
                        if lastStatePlayer["life"] <= 0:
                            # Player died
                            # Add message to kill messages
                            killMessage = f"{lastStateProjetil['userName']} killed {lastStatePlayer['userName']}"
                            addKillMessage(killMessage)
                            lastStatePlayer["life"] = lastStatePlayer["maxLife"]
                            if lastStatePlayer["team"] == 'red':
                                randintX = randint(baseVermelha[0][0], baseVermelha[1][0])
                                randintY = randint(baseVermelha[0][1], baseVermelha[2][1])
                                lastStatePlayer["x"] = randintX
                                lastStatePlayer["y"] = randintY
                            else:
                                randintX = randint(baseAzul[0][0], baseAzul[1][0])
                                randintY = randint(baseAzul[0][1], baseAzul[2][1])
                                lastStatePlayer["x"] = randintX
                                lastStatePlayer["y"] = randintY
                        stateGlobal[messageDict['HostId']]["Players"][idPlayer] = lastStatePlayer
            if len(to_remove) > 0:
                break
        for idProjetil in to_remove:
            try:
                del stateGlobal[messageDict['HostId']]["Projectiles"][idProjetil]
            except:
                pass

def colisionBetweenProjectilesAndMapa() -> None:
    # Colision between projectiles and map
    to_remove = []
    for idProjetil in stateGlobal[messageDict['HostId']]["Projectiles"]:
        lastStateProjetil = stateGlobal[messageDict['HostId']]["Projectiles"][idProjetil]
        # Check if the projectile will colide with the map
        posicaoRealxX = lastStateProjetil["x"] + lastStateProjetil["moveX"] * lastStateProjetil["atualTimeToDestroy"]
        posicaoRealY = lastStateProjetil["y"] + lastStateProjetil["moveY"] * lastStateProjetil["atualTimeToDestroy"]
        multipleX, multipleY = checkColisionWithMapa(posicaoRealxX, posicaoRealY, lastStateProjetil["moveX"], lastStateProjetil["moveY"])
        multipleX1, multipleY1 = checkColisionWithBase(posicaoRealxX, posicaoRealY, lastStateProjetil["moveX"], lastStateProjetil["moveY"])
        if multipleX == 0 or multipleY == 0 or multipleX1 == 0 or multipleY1 == 0:
            to_remove.append(idProjetil)
    for idProjetil in to_remove:
        del stateGlobal[messageDict['HostId']]["Projectiles"][idProjetil]        

def clearKillMessages() -> None:
    # Clear if the time is greater than 5 seconds
    message_to_remove = []
    for idMessage in stateGlobal[messageDict['HostId']]["KillMessages"]:
        if float(idMessage) < time() - 5:
            message_to_remove.append(idMessage)
    for idMessage in message_to_remove:
        del stateGlobal[messageDict['HostId']]["KillMessages"][idMessage]

def atualizaEstadoAtual(msg: dict) -> None:
    global atualState, idOfPlayer

    # ---------- Players ----------

    # Players of atual state have the player with uuid of msg
    if 'Players' not in msg.keys():
        idOfPlayer = str(uuid4())
        createPlayer(msg)
    else:
        # ------ All iteractions ------
        idOfPlayer = next(iter(msg['Players']))


        lastState = stateGlobal[messageDict['HostId']]["Players"][idOfPlayer]
         # update time to reconect
        stateGlobal[messageDict['HostId']]["Players"][idOfPlayer]["atualTimeToReconect"] = 0
        # If player will colide with enemy team, then, don't go to that direction
        playerToRemove = []
        
        for idPlayer in stateGlobal[messageDict['HostId']]["Players"]:
            # Decrement the atualTimeToReconect
            if stateGlobal[messageDict['HostId']]["Players"][idPlayer]["atualTimeToReconect"] < 100:
                stateGlobal[messageDict['HostId']]["Players"][idPlayer]["atualTimeToReconect"] += 1
            else:
                # If is equal to 0, then, delete the player
                playerToRemove.append(idPlayer)

            if stateGlobal[messageDict['HostId']]["Players"][idPlayer]["team"] != lastState["team"]:
                # Mas coloque um offset de 25, porque o player tem 25 de largura e 25 de altura
                if stateGlobal[messageDict['HostId']]["Players"][idPlayer]["x"] - 25 <= lastState["x"] + msg['Players'][idOfPlayer]["moveX"] <= stateGlobal[messageDict['HostId']]["Players"][idPlayer]["x"] + 25:
                    if stateGlobal[messageDict['HostId']]["Players"][idPlayer]["y"] - 25 <= lastState["y"] <= stateGlobal[messageDict['HostId']]["Players"][idPlayer]["y"] + 25:
                        lastState["x"] -= msg['Players'][idOfPlayer]["moveX"]
                        stateGlobal[messageDict['HostId']]["Players"][idOfPlayer] = lastState
                if stateGlobal[messageDict['HostId']]["Players"][idPlayer]["y"] - 25 <= lastState["y"] + msg['Players'][idOfPlayer]["moveY"] <= stateGlobal[messageDict['HostId']]["Players"][idPlayer]["y"] + 25:
                    if stateGlobal[messageDict['HostId']]["Players"][idPlayer]["x"] - 25 <= lastState["x"] <= stateGlobal[messageDict['HostId']]["Players"][idPlayer]["x"] + 25:
                        lastState["y"] -= msg['Players'][idOfPlayer]["moveY"]
                        stateGlobal[messageDict['HostId']]["Players"][idOfPlayer] = lastState
        
        for idPlayer in playerToRemove:
            del stateGlobal[messageDict['HostId']]["Players"][idPlayer]

        # Check if the player will colide with the map
        multipleX, multipleY = checkColisionWithMapa(lastState["x"], lastState["y"], msg['Players'][idOfPlayer]["moveX"], msg['Players'][idOfPlayer]["moveY"])

        lastState["x"] += msg['Players'][idOfPlayer]["moveX"] * multipleX
        lastState["y"] += msg['Players'][idOfPlayer]["moveY"] * multipleY
        stateGlobal[messageDict['HostId']]["Players"][idOfPlayer] = lastState
    stateGlobal[messageDict['HostId']]["Players"][idOfPlayer]["moveX"] = 0
    stateGlobal[messageDict['HostId']]["Players"][idOfPlayer]["moveY"] = 0

    # Colision between players and bases
    colisionBetweenPlayersAndBases()
    # --------- Projectiles ---------

    # New Projectiles
    createProjetil(msg)

    # Update all projectiles
    to_remove = []
    for idProjetil in stateGlobal[messageDict['HostId']]["Projectiles"]:
        lastState = stateGlobal[messageDict['HostId']]["Projectiles"][idProjetil]
        lastState["atualTimeToDestroy"] += 10
        stateGlobal[messageDict['HostId']]["Projectiles"][idProjetil] = lastState
        if lastState["atualTimeToDestroy"] >= lastState["timeToDestroy"]:
            to_remove.append(idProjetil)

    for idProjetil in to_remove:
        del stateGlobal[messageDict['HostId']]["Projectiles"][idProjetil]
    
    # Colision between projectiles and map
    colisionBetweenProjectilesAndMapa()

    # Colision between players and projectiles
    colisionBetweenPlayersAndProjectiles()

    # --------- Chat ---------
    addMessageToChat(msg)
    atualStateComMessage = stateGlobal[messageDict['HostId']].copy()
    initTime = stateGlobal[messageDict['HostId']]["Players"][idOfPlayer]["timeStamp"] 
    message_to_remove = []
    for idMessage in stateGlobal[messageDict['HostId']]["ChatMessages"]:
        if idMessage < initTime:
            message_to_remove.append(idMessage)
    for idMessage in message_to_remove:
        del atualStateComMessage["ChatMessages"][idMessage]

    # --------- Kill Messages ---------
    clearKillMessages()

    # --------- Update Team Dominating ---------
    updateTeamDominating()

    # --------- HostId ---------
    idHost = msg["HostId"]
    atualStateComMessage["HostId"] = idHost

    # Update global state
    atualState = atualStateComMessage

def createNewHost(msg: dict) -> None:
    newHostId = str(uuid4())
    state = {
        "Players": {

        },
            
        "Projectiles": {

        },
        "ChatMessages": {

        },
        "KillMessages": {

        },
        "TeamWon": "None", # None, Blue, Red
        "TeamDominating": 'None',
        "TimeToBlueWin": [0, 0], # time already dominating, time started in last capture
        "TimeToRedWin": [0, 0], # time already dominating, time started in last capture
        "ProgressTimeBlue": 0,
        "ProgressTimeRed": 0,
    }
    stateGlobal[newHostId] = state
    msg['HostId'] = newHostId


# Create a datagram socket
UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

# Bind to address and ip
UDPServerSocket.bind((localIP, localPort))

print("UDP server up and listening")

# Listen for incoming datagrams
while(True):
    # try:
        bytesAddressPair = UDPServerSocket.recvfrom(bufferSize)
        address = bytesAddressPair[1]
        message: str = bytesAddressPair[0].decode('utf-8') 
        message = message.replace("'", '"')  # replace single quotes with double quotes
        message = message.replace('"{', '{')  # replace single quotes with double quotes
        message = message.replace('}"', '}')  # replace single quotes with double quotes
        messageDict: dict = json.loads(message)

        if 'getHosts' in messageDict.keys():
            # If have the key Games, then, return all games
            games = {}
            keys = list(stateGlobal.keys())
            for idHost in keys:
                games[idHost] = len(stateGlobal[idHost]["Players"])
            if len(games) == 0:
                games["None"] = 0
            bytesToSend: bytes = str.encode(str(games))
            # Sending a reply to client
            UDPServerSocket.sendto(bytesToSend, address)
            continue
            
        if 'NewHost' in messageDict.keys():
            print("New host")
            createNewHost(messageDict)

        atualState = {}

        del atualState
        
        atualState = stateGlobal[messageDict['HostId']]
        lastTime = time()
        if 'Players' in messageDict.keys():
            if idOfPlayer in messageDict['Players'].keys():
                lastTime = messageDict['Players'][idOfPlayer]['lastTime']

        deltaTime = time() - lastTime

        atualizaEstadoAtual(messageDict)

        stateGlobal[messageDict['HostId']]['idOfPlayer'] = idOfPlayer


        stateGlobal[messageDict['HostId']]['Players'][idOfPlayer]['lastTime'] = time()

        atualState['idOfPlayer'] = idOfPlayer

        bytesToSend: bytes = str.encode(str(atualState))

        # Sending a reply to client
        UDPServerSocket.sendto(bytesToSend, address)
    # except Exception as e:
    #     print(e)
    #     print("Erro ao receber mensagem")
    #     pass