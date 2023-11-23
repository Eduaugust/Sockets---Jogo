import pygame

def main():
    pygame.init()

    # Configurações da tela
    size = (700, 500)
    screen = pygame.display.set_mode(size)

    # Configurações do chat
    chat_box = pygame.Rect(50, 50, 600, 400)
    input_box = pygame.Rect(50, 460, 600, 30)
    color_inactive = pygame.Color('lightskyblue3')
    color_active = pygame.Color('dodgerblue2')
    color = color_inactive

    clock = pygame.time.Clock()
    input_active = False
    text = ''
    messages = []

    while True:
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.MOUSEBUTTONDOWN:
                if input_box.collidepoint(event.pos):
                    input_active = not input_active
                else:
                    input_active = False
                color = color_active if input_active else color_inactive
            if event.type == pygame.KEYDOWN:
                if input_active:
                    if event.key == pygame.K_RETURN:
                        messages.append(text)
                        text = ''
                    elif event.key == pygame.K_BACKSPACE:
                        text = text[:-1]
                    else:
                        text += event.unicode

        screen.fill((30, 30, 30))
        pygame.draw.rect(screen, color, input_box, 2)

        font = pygame.font.Font(None, 32)
        txt_surface = font.render(text, True, color)
        screen.blit(txt_surface, (input_box.x+5, input_box.y+5))

        y = 10
        for message in messages[-10:]:
            txt_surface = font.render(message, True, (255, 255, 255))
            screen.blit(txt_surface, (chat_box.x+5, chat_box.y+y))
            y += 30

        pygame.display.flip()
        clock.tick(30)

if __name__ == '__main__':
    main()