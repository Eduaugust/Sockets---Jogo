from PIL import Image


class BaseVermelha:
    def __init__(self, x, y):
        self.x = x*50
        self.y = y*50
        self.tipo = 'R'

class BaseAzul:
    def __init__(self, x, y):
        self.x = x*50
        self.y = y*50
        self.tipo = 'B'

class Obstaculo:
    def __init__(self, x, y):
        self.x = x*50
        self.y = y*50
        self.tipo = '#'

class ControlPoint:
    def __init__(self, x, y):
        self.x = x*50
        self.y = y*50
        self.tipo = '*'

class Vazio:
    def __init__(self, x, y):
        self.x = x*50
        self.y = y*50
        self.tipo = ' '

class DominationData:
    def __init__(self, state):
        self.team_won = state['TeamWon']
        self.team_dominating = state['TeamDominating']
        self.time_to_blue_win = state['TimeToBlueWin']
        self.time_to_red_win = state['TimeToRedWin']
        self.progress_time_blue = state['ProgressTimeBlue']
        self.progress_time_red = state['ProgressTimeRed']
        self.blueColor = (100, 100, 255)
        self.redColor = (255, 100, 100)
        self.grayColor = (100, 100, 100)
        self.greenColor = (100, 255, 100)
    
    def __str__(self) -> str:
        return f'\nTime vencedor: {self.team_won}\n' \
               f'Time dominante: {self.team_dominating}\n' \
               f'Tempo para o time azul vencer: {self.time_to_blue_win}\n' \
               f'Tempo para o time vermelho vencer: {self.time_to_red_win}\n' \
               f'Tempo de progresso do time azul: {self.progress_time_blue}\n' \
               f'Tempo de progresso do time vermelho: {self.progress_time_red}\n'

def inicializa_mapa():
    objetos = []
    mapa = retorna_mapa()
    for i in range(len(mapa)):
        for j in range(len(mapa[i])):
            if mapa[i][j] == 'R':
                objetos.append(BaseVermelha(j, i))
            elif mapa[i][j] == 'B':
                objetos.append(BaseAzul(j, i))
            elif mapa[i][j] == '#':
                objetos.append(Obstaculo(j, i))
            elif mapa[i][j] == '*':
                objetos.append(ControlPoint(j, i))
            else:
                objetos.append(Vazio(j, i))
    return objetos

def retorna_mapa():
    # Load the image
    image = Image.open("mapa1.png")

    # Get the pixel data
    pixels = image.load()

    # Create an empty array
    map_array = []

    # Iterate over each pixel
    for y in range(image.height):
        row = []
        for x in range(image.width):
            # Get the RGB values of the pixel
            r, g, b, alpha = pixels[x, y]

            # Determine the value based on the color
            if r == 255 and g == 255 and b == 255:  # White
                value = " "
            elif r == 255 and g == 0 and b == 0:  # Red
                value = "R"
            elif r == 0 and g == 0 and b == 255:  # Blue
                value = "B"
            elif r == 0 and g == 255 and b == 0:  # Green
                value = "*"
            elif r == 0 and g == 0 and b == 0:  # Black
                value = "#"
            else:
                value = " "  # Default value for other colors

            row.append(value)

        map_array.append(row)

    return map_array