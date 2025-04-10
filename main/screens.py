import pygame

def welcome_screen(screen, font):
    while True:
        screen.fill((255, 255, 255))
        title = font.render("Welcome to Fitts' Law Experiment", True, (0, 0, 0))
        start_button = pygame.Rect(300, 300, 200, 50)
        quit_button = pygame.Rect(300, 370, 200, 50)

        pygame.draw.rect(screen, (0, 200, 0), start_button)
        pygame.draw.rect(screen, (200, 0, 0), quit_button)
        screen.blit(title, (220, 100))
        screen.blit(font.render("Start", True, (255, 255, 255)), (375, 315))
        screen.blit(font.render("Quit", True, (255, 255, 255)), (375, 385))

        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            if event.type == pygame.MOUSEBUTTONDOWN:
                if start_button.collidepoint(event.pos):
                    return "start"
                elif quit_button.collidepoint(event.pos):
                    return "quit"

def icf_screen(screen, font):
    consent_text = [
        "Informed Consent Form",
        "By participating, you agree to...",
        "(Add more ICF details here...)",
        "",
        "Do you agree to participate?"
    ]

    while True:
        screen.fill((240, 240, 240))
        for idx, line in enumerate(consent_text):
            text = font.render(line, True, (0, 0, 0))
            screen.blit(text, (50, 50 + idx * 30))

        agree_button = pygame.Rect(200, 500, 150, 40)
        decline_button = pygame.Rect(450, 500, 150, 40)
        pygame.draw.rect(screen, (0, 200, 0), agree_button)
        pygame.draw.rect(screen, (200, 0, 0), decline_button)
        screen.blit(font.render("Agree", True, (255, 255, 255)), (240, 510))
        screen.blit(font.render("Decline", True, (255, 255, 255)), (480, 510))

        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "decline"
            if event.type == pygame.MOUSEBUTTONDOWN:
                if agree_button.collidepoint(event.pos):
                    return "agree"
                elif decline_button.collidepoint(event.pos):
                    return "decline"
