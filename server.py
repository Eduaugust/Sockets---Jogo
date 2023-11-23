import json
import socket
from time import time

localIP     = "127.0.0.1"
localPort   = 3000
bufferSize  = 16384

atualState = {
    "Players": {

    },
        
    "Projectiles": {

    },
    "ChatMessages": {

    }
}

def createPlayer(msg: dict, idOfPlayer) -> None:
    team = 'red' if len(atualState["Players"]) % 2 == 0 else 'blue'
    # new player
    atualState["Players"][idOfPlayer] = msg['Players'][idOfPlayer]
    atualState["Players"][idOfPlayer]["team"] = team
    atualState["Players"][idOfPlayer]["timeStamp"] = time()

    if atualState["Players"][idOfPlayer]["team"] == 'red':
        msg['Players'][idOfPlayer]["x"] = 0
        msg['Players'][idOfPlayer]["y"] = 0
    else:
        msg['Players'][idOfPlayer]["x"] = 0
        msg['Players'][idOfPlayer]["y"] = 50
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
                            lastStatePlayer["life"] = lastStatePlayer["maxLife"]
                            if lastStatePlayer["team"] == 'red':
                                lastStatePlayer["x"] = 0
                                lastStatePlayer["y"] = 0
                            else:
                                lastStatePlayer["x"] = 0
                                lastStatePlayer["y"] = 50
                        atualState["Players"][idPlayer] = lastStatePlayer
    for idProjetil in to_remove:
        del atualState["Projectiles"][idProjetil]

def atualizaEstadoAtual(msg: dict) -> bytes:
    global atualState

    # ---------- Players ----------

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
                    
        lastState["x"] += msg['Players'][idOfPlayer]["moveX"]
        lastState["y"] += msg['Players'][idOfPlayer]["moveY"]
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
        lastState["atualTimeToDestroy"] += 1
        atualState["Projectiles"][idProjetil] = lastState
        if lastState["atualTimeToDestroy"] >= lastState["timeToDestroy"]:
            to_remove.append(idProjetil)

    for idProjetil in to_remove:
        del atualState["Projectiles"][idProjetil]

    # Colision between players and projectiles
    colisionBetweenPlayersAndProjectiles()

    # --------- Chat ---------
    addMessageToChat(msg)
    atualStateComMessage = atualState.copy()
    initTime = atualState["Players"][idOfPlayer]["timeStamp"] 
    message_to_remove = []
    for idMessage in atualState["ChatMessages"]:
        if atualState["ChatMessages"][idMessage]["timeStamp"] < initTime:
            message_to_remove.append(idMessage)
    for idMessage in message_to_remove:
        del atualStateComMessage["ChatMessages"][idMessage]
    
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