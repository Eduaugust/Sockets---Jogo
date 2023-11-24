import json
from random import randint
import socket
from time import time
from typing import List
from debug import debug

from mapa import inicializa_mapa

localIP     = "192.168.2.104"
localPort   = 3000
bufferSize  = 16384

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

# --------- Estado Atual ---------

atualState = {
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

def updateTeamDominating() -> None:
    global atualState
    timeAzul = time() - atualState["ProgressTimeBlue"] if atualState["ProgressTimeBlue"] != 0 else 0
    timeVermelho = time() - atualState["ProgressTimeRed"] if atualState["ProgressTimeRed"] != 0 else 0
    red = 0
    blue = 0
    # Update the team dominating
    timeToWon = 60 * 3
    for idPlayer in atualState["Players"]:
        tentandoDominar = checkColsionPlayerAndAsterisk(atualState["Players"][idPlayer]["x"], atualState["Players"][idPlayer]["y"], 0, 0)
        if not tentandoDominar:
            continue
        if atualState["Players"][idPlayer]["team"] == 'red':
            red += 1
        else:
            blue += 1

    if red > 0 and blue == 0:
        if atualState["TeamDominating"] == 'blue':
            if atualState["ProgressTimeRed"] == 0:
                atualState["ProgressTimeRed"] = time()
            else:
                if time() - atualState["ProgressTimeRed"] >= 10:
                    # Save the blue time
                    atualState["TimeToBlueWin"][0] = time() - atualState["TimeToBlueWin"][1]

                    # Set new time to red
                    atualState["TimeToRedWin"][1] = time()
                    atualState["ProgressTimeRed"] = 0
                    atualState["ProgressTimeBlue"] = 0
                    atualState["TeamDominating"] = 'red'
        elif atualState["TeamDominating"] == 'Red':
            if atualState["ProgressTimeBlue"] != 0:
                # insiro o tempo que o time azul dominou
                atualState['ProgressTimeBlue'] += 1/15
                if atualState["ProgressTimeBlue"] - time() < 0:
                    atualState["ProgressTimeBlue"] = 0
        else: 
            # TeamDominating is None

            # Init the progress time
            if atualState["ProgressTimeRed"] == 0 and atualState["ProgressTimeBlue"] == 0:
                atualState["ProgressTimeRed"] = time()
            elif time() - atualState["ProgressTimeRed"] >= 10:
                # Save the blue time
                atualState["TimeToBlueWin"][0] = time() - atualState["TimeToBlueWin"][1]

                # Set new time to red
                atualState["TimeToRedWin"][1] = time()
                atualState["ProgressTimeRed"] = 0
                atualState["ProgressTimeBlue"] = 0
                atualState["TeamDominating"] = 'red'
            
    elif blue > 0 and red == 0:
        if atualState["TeamDominating"] == 'red':
            if atualState["ProgressTimeBlue"] == 0:
                atualState["ProgressTimeBlue"] = time()
                atualState["ProgressTimeRed"] = 0
            else:
                if time() - atualState["ProgressTimeBlue"] >= 10:
                    # Save the red time
                    atualState["TimeToRedWin"][0] = time() - atualState["TimeToRedWin"][1]

                    # Set new time to blue
                    atualState["TimeToBlueWin"][1] = time()
                    atualState["ProgressTimeRed"] = 0
                    atualState["ProgressTimeBlue"] = 0
                    atualState["TeamDominating"] = 'blue'
        elif atualState["TeamDominating"] == 'blue':
            if atualState["ProgressTimeRed"] != 0:
                # insiro o tempo que o time vermelho dominou
                atualState['ProgressTimeRed'] += 1/15
                if atualState["ProgressTimeRed"] - time() < 0:
                    atualState["ProgressTimeRed"] = 0
        else:
            # TeamDominating is None

            # Init the progress time
            if atualState["ProgressTimeRed"] == 0 and atualState["ProgressTimeBlue"] == 0:
                atualState["ProgressTimeBlue"] = time()
                atualState["ProgressTimeRed"] = 0
            elif time() - atualState["ProgressTimeBlue"] >= 10:
                # Save the red time
                atualState["TimeToRedWin"][0] = time() - atualState["TimeToRedWin"][1]

                # Set new time to blue
                atualState["TimeToBlueWin"][1] = time()
                atualState["ProgressTimeRed"] = 0
                atualState["ProgressTimeBlue"] = 0
                atualState["TeamDominating"] = 'blue'

            
    elif blue > 0 and red > 0:
        # If progress time is not 0 in red
        if atualState["ProgressTimeRed"] != 0:
            # Progress time dont move, anything do not move
            atualState["ProgressTimeRed"] += 1/15
        elif atualState["ProgressTimeBlue"] != 0:
            # Progress time dont move, anything do not move
            atualState["ProgressTimeBlue"] += 1/15
    elif blue == 0 and red == 0:
        # If progress time is not 0, then, reset it if the time is greater than 10 seconds
        if atualState["ProgressTimeRed"] != 0:
            atualState["ProgressTimeRed"] += 1/15
            if time() - atualState["ProgressTimeRed"] < 0:
                atualState["ProgressTimeRed"] = 0
        if atualState["ProgressTimeBlue"] != 0:
            atualState["ProgressTimeBlue"] += 1/15
            if time() - atualState["ProgressTimeBlue"] < 0:
                atualState["ProgressTimeBlue"] = 0
    # Check if someone won, just if progress time is 0

    if atualState["ProgressTimeRed"] == 0 and atualState["ProgressTimeBlue"] == 0:
        if atualState["TimeToBlueWin"][1] != 0 and  time() - atualState["TimeToBlueWin"][1] + atualState["TimeToBlueWin"][0]  >= timeToWon:
                # Blue won
                atualState["TimeToBlueWin"][0] = 0
                atualState["TimeToBlueWin"][1] = 0
                atualState["TimeToRedWin"][0] = 0
                atualState["TimeToRedWin"][1] = 0
                atualState["TeamDominating"] = 'blue'
                atualState["TeamWon"] = 'blue'
        elif atualState["TimeToRedWin"][1] != 0 and time() - atualState["TimeToRedWin"][1] + atualState["TimeToRedWin"][0]  >= timeToWon:
                # Red won
                atualState["TimeToBlueWin"][0] = 0
                atualState["TimeToBlueWin"][1] = 0
                atualState["TimeToRedWin"][0] = 0
                atualState["TimeToRedWin"][1] = 0
                atualState["TeamDominating"] = 'red'
                atualState["TeamWon"] = 'red'

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
    for idPlayer in atualState["Players"]:
        lastStatePlayer = atualState["Players"][idPlayer]
        # Check if the player will colide with the base
        if lastStatePlayer["team"] == 'red':
            # Check if the player will colide with the base azul
            if baseAzul[0][0] <= lastStatePlayer["x"] <= baseAzul[1][0]:
                if baseAzul[0][1] <= lastStatePlayer["y"] <= baseAzul[2][1]:
                    randomX = randint(baseVermelha[0][0], baseVermelha[1][0])
                    randomY = randint(baseVermelha[0][1], baseVermelha[2][1])
                    lastStatePlayer["x"] = randomX
                    lastStatePlayer["y"] = randomY
                    atualState["Players"][idPlayer] = lastStatePlayer
                    addKillMessage(f"{lastStatePlayer['userName']} suicided")
        else:
            # Check if the player will colide with the base vermelha
            if baseVermelha[0][0] <= lastStatePlayer["x"] <= baseVermelha[1][0]:
                if baseVermelha[0][1] <= lastStatePlayer["y"] <= baseVermelha[2][1]:
                    randomX = randint(baseAzul[0][0], baseAzul[1][0])
                    randomY = randint(baseAzul[0][1], baseAzul[2][1])
                    lastStatePlayer["x"] = randomX
                    lastStatePlayer["y"] = randomY
                    atualState["Players"][idPlayer] = lastStatePlayer
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

def createPlayer(msg: dict, idOfPlayer) -> None:
    print("Novo player")
    # If the number of blue is greater than red, then, the new player will be red, else, blue
    red = 0
    blue = 0
    for idPlayer in atualState["Players"]:
        if atualState["Players"][idPlayer]["team"] == 'red':
            red += 1
        else:
            blue += 1
    team = 'red' if red  < blue else 'blue'

    # new player
    atualState["Players"][idOfPlayer] = msg['Players'][idOfPlayer]
    atualState["Players"][idOfPlayer]["team"] = team
    atualState["Players"][idOfPlayer]["timeStamp"] = str(time())

    if atualState["Players"][idOfPlayer]["team"] == 'red':
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
    atualState["Players"][idOfPlayer] = msg['Players'][idOfPlayer]

def createProjetil(msg: dict) -> None:
    newBullet = msg['NewBullet'] if msg['NewBullet'] != "None" else False
    if newBullet:
        # Add new bullet to projectiles
        idOfBullet = next(iter(newBullet))
        atualState["Projectiles"][idOfBullet] = newBullet[idOfBullet]
        atualState["Projectiles"][idOfBullet]["atualTimeToDestroy"] = 0

def addMessageToChat(msg: dict) -> None:
    # If have the key NewMessage, then, add the message to chat
    if 'NewMessage' in msg.keys():
        newMessage = msg['NewMessage']
        # Add new message to chat
        idOfMessage = str(time())
        atualState["ChatMessages"][idOfMessage] = newMessage

    # --------- Remove mensagem se tiver mais de 10 mensagens ---------
    message_to_remove = []
    if len(atualState["ChatMessages"]) > 10:
        # Remover apenas as mensagens mais antigas
        keys = list(atualState["ChatMessages"].keys())
        keys.sort()
        for idMessage in keys[:len(atualState["ChatMessages"]) - 10]:
            message_to_remove.append(idMessage)
    for idMessage in message_to_remove:
        del atualState["ChatMessages"][idMessage]        

def addKillMessage(killMessage: str) -> None:
    idOfMessage = str(time())
    atualState["KillMessages"][idOfMessage] = killMessage

def colisionBetweenPlayersAndProjectiles() -> None:
    # Colision between players and projectiles
    to_remove = []
    for idPlayer in atualState["Players"]:
        for idProjetil in atualState["Projectiles"]:
            lastStatePlayer = atualState["Players"][idPlayer]
            lastStateProjetil = atualState["Projectiles"][idProjetil]
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
                        atualState["Players"][idPlayer] = lastStatePlayer
            if len(to_remove) > 0:
                break
        for idProjetil in to_remove:
            try:
                del atualState["Projectiles"][idProjetil]
            except:
                pass

def colisionBetweenProjectilesAndMapa() -> None:
    # Colision between projectiles and map
    to_remove = []
    for idProjetil in atualState["Projectiles"]:
        lastStateProjetil = atualState["Projectiles"][idProjetil]
        # Check if the projectile will colide with the map
        posicaoRealxX = lastStateProjetil["x"] + lastStateProjetil["moveX"] * lastStateProjetil["atualTimeToDestroy"]
        posicaoRealY = lastStateProjetil["y"] + lastStateProjetil["moveY"] * lastStateProjetil["atualTimeToDestroy"]
        multipleX, multipleY = checkColisionWithMapa(posicaoRealxX, posicaoRealY, lastStateProjetil["moveX"], lastStateProjetil["moveY"])
        multipleX1, multipleY1 = checkColisionWithBase(posicaoRealxX, posicaoRealY, lastStateProjetil["moveX"], lastStateProjetil["moveY"])
        if multipleX == 0 or multipleY == 0 or multipleX1 == 0 or multipleY1 == 0:
            to_remove.append(idProjetil)
    for idProjetil in to_remove:
        del atualState["Projectiles"][idProjetil]        

def clearKillMessages() -> None:
    # Clear if the time is greater than 5 seconds
    message_to_remove = []
    for idMessage in atualState["KillMessages"]:
        if float(idMessage) < time() - 5:
            message_to_remove.append(idMessage)
    for idMessage in message_to_remove:
        del atualState["KillMessages"][idMessage]

def atualizaEstadoAtual(msg: dict) -> bytes:
    global atualState

    # ---------- Players ----------

    # Colision between players and bases
    colisionBetweenPlayersAndBases()

    # Players of atual state have the player with uuid of msg
    idOfPlayer = next(iter(msg['Players']))
    if idOfPlayer not in atualState["Players"].keys():
        createPlayer(msg, idOfPlayer)
    else:
        # ------ All iteractions ------

        lastState = atualState["Players"][idOfPlayer]
         # update time to reconect
        atualState["Players"][idOfPlayer]["atualTimeToReconect"] = 0
        # If player will colide with enemy team, then, don't go to that direction
        playerToRemove = []
        
        for idPlayer in atualState["Players"]:
            # Decrement the atualTimeToReconect
            if atualState["Players"][idPlayer]["atualTimeToReconect"] < 100:
                atualState["Players"][idPlayer]["atualTimeToReconect"] += 1
            else:
                # If is equal to 0, then, delete the player
                playerToRemove.append(idPlayer)

            if atualState["Players"][idPlayer]["team"] != lastState["team"]:
                # Mas coloque um offset de 25, porque o player tem 25 de largura e 25 de altura
                if atualState["Players"][idPlayer]["x"] - 25 <= lastState["x"] + msg['Players'][idOfPlayer]["moveX"] <= atualState["Players"][idPlayer]["x"] + 25:
                    if atualState["Players"][idPlayer]["y"] - 25 <= lastState["y"] <= atualState["Players"][idPlayer]["y"] + 25:
                        lastState["x"] -= msg['Players'][idOfPlayer]["moveX"]
                        atualState["Players"][idOfPlayer] = lastState
                if atualState["Players"][idPlayer]["y"] - 25 <= lastState["y"] + msg['Players'][idOfPlayer]["moveY"] <= atualState["Players"][idPlayer]["y"] + 25:
                    if atualState["Players"][idPlayer]["x"] - 25 <= lastState["x"] <= atualState["Players"][idPlayer]["x"] + 25:
                        lastState["y"] -= msg['Players'][idOfPlayer]["moveY"]
                        atualState["Players"][idOfPlayer] = lastState
        
        for idPlayer in playerToRemove:
            del atualState["Players"][idPlayer]

        # Check if the player will colide with the map
        multipleX, multipleY = checkColisionWithMapa(lastState["x"], lastState["y"], msg['Players'][idOfPlayer]["moveX"], msg['Players'][idOfPlayer]["moveY"])

        lastState["x"] += msg['Players'][idOfPlayer]["moveX"] * multipleX
        lastState["y"] += msg['Players'][idOfPlayer]["moveY"] * multipleY
        atualState["Players"][idOfPlayer] = lastState
    atualState["Players"][idOfPlayer]["moveX"] = 0
    atualState["Players"][idOfPlayer]["moveY"] = 0

    # --------- Projectiles ---------

    # New Projectiles

    createProjetil(msg)

    # Update all projectiles
    to_remove = []
    for idProjetil in atualState["Projectiles"]:
        lastState = atualState["Projectiles"][idProjetil]
        lastState["atualTimeToDestroy"] += 10
        atualState["Projectiles"][idProjetil] = lastState
        if lastState["atualTimeToDestroy"] >= lastState["timeToDestroy"]:
            to_remove.append(idProjetil)

    for idProjetil in to_remove:
        del atualState["Projectiles"][idProjetil]
    
    # Colision between projectiles and map
    colisionBetweenProjectilesAndMapa()

    # Colision between players and projectiles
    colisionBetweenPlayersAndProjectiles()

    # --------- Chat ---------
    addMessageToChat(msg)
    atualStateComMessage = atualState.copy()
    initTime = atualState["Players"][idOfPlayer]["timeStamp"] 
    message_to_remove = []
    for idMessage in atualState["ChatMessages"]:
        if idMessage < initTime:
            message_to_remove.append(idMessage)
    for idMessage in message_to_remove:
        del atualStateComMessage["ChatMessages"][idMessage]

    # --------- Kill Messages ---------
    clearKillMessages()

    # --------- Update Team Dominating ---------
    updateTeamDominating()

    # --------- Return ---------
    
    byteSend: bytes = str.encode(str(atualState))

    return byteSend

msgFromServer = str(atualState)

# Create a datagram socket
UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

# Bind to address and ip
UDPServerSocket.bind((localIP, localPort))

print("UDP server up and listening")

# Listen for incoming datagrams
while(True):
    bytesAddressPair = UDPServerSocket.recvfrom(bufferSize)
    address = bytesAddressPair[1]
    message: str = bytesAddressPair[0].decode('utf-8') 
    message = message.replace("'", '"')  # replace single quotes with double quotes
    message = message.replace('"{', '{')  # replace single quotes with double quotes
    message = message.replace('}"', '}')  # replace single quotes with double quotes
    messageDict: dict = json.loads(message)

    bytesToSend: bytes = atualizaEstadoAtual(messageDict)

    # Sending a reply to client
    UDPServerSocket.sendto(bytesToSend, address)