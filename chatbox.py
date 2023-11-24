import pygame

class TextBox:
    def __init__(self, x, y, w, h, text=''):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = pygame.Color('lightskyblue3')
        self.text = text
        self.font = pygame.font.Font(None, 22)
        self.active = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.active = not self.active
            else:
                self.active = False
            self.color = pygame.Color('dodgerblue2') if self.active else pygame.Color('lightskyblue3')
        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_RETURN:
                return self.text
            elif event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            else:
                self.text += event.unicode
        return None

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect, 2)
        txt_surface = self.font.render(self.text, True, self.color)
        screen.blit(txt_surface, (self.rect.x+5, self.rect.y+5))

class ChatBox:
    def __init__(self, x, y, w, h):
        self.rect = pygame.Rect(x, y, w, h)
        self.messages = []
        self.idMessage = []
        self.font = pygame.font.Font(None, 22)

    def add_message(self, message, idMessage):
        if idMessage in self.idMessage:
            return
        if len(self.messages) > 10:
            self.messages.pop(0)
            self.idMessage.pop(0)
        self.idMessage.append(idMessage)
        self.messages.append(message)

    def draw(self, screen: pygame.Surface):
        # Draw just 10 lines, so the chat box don't get too big, and each line have 30 characters
        y = 10
        allMessages = self.messages[-10:]
        txtFinal = ''
        for message in allMessages:
            for i in range(0, len(message), 30):
                txtFinal += message[i:i+30] + '\n'
        
        # count the number of lines
        lines = txtFinal.count('\n')
        # if the number is greater than 14, then, remove the first lines
        if lines > 14:
            txtFinal = txtFinal.split('\n')
            txtFinal = '\n'.join(txtFinal[-14:])
        
        txt_surface = self.font.render(txtFinal, True, (0, 0 ,0))
        screen.blit(txt_surface, (self.rect.x+5, self.rect.y+y))