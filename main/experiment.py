import pygame
import time
import random
import math
from utils import generate_trial_sequence, save_trial_data

def run_experiment(screen, clock, font, participant_id):
    trial_sequence = generate_trial_sequence()
    trial_data = []

    for i, config_id in enumerate(trial_sequence):
        # Use your own logic to map config_id to size, distance, and direction
        distance = random.choice([100, 200, 300])
        size = random.choice([20, 40, 60])
        direction = random.choice(["up", "down", "left", "right"])

        # Center reset
        center_rect = pygame.Rect(390, 290, 20, 20)
        waiting = True
        while waiting:
            screen.fill((255, 255, 255))
            pygame.draw.rect(screen, (0, 0, 255), center_rect)
            screen.blit(font.render("Click center to begin trial", True, (0, 0, 0)), (250, 250))
            pygame.display.flip()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                elif event.type == pygame.MOUSEBUTTONDOWN and center_rect.collidepoint(event.pos):
                    waiting = False

        # Begin trial
        target_x = 400 + distance if direction == "right" else 400 - distance
        target_y = 300

        start_pos = pygame.mouse.get_pos()
        start_time = time.time()
        errors = 0
        mouse_path = [start_pos]

        while True:
            screen.fill((255, 255, 255))
            pygame.draw.circle(screen, (255, 0, 0), (target_x, target_y), size)
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    dx = mouse_pos[0] - target_x
                    dy = mouse_pos[1] - target_y
                    distance_to_target = math.hypot(dx, dy)
                    if distance_to_target <= size:
                        end_time = time.time()
                        total_time = round((end_time - start_time) * 1000, 2)
                        travel_distance = calculate_mouse_distance(mouse_path)
                        trial_data.append([i+1, distance, size, direction, total_time, round(travel_distance, 2), errors])
                        break
                    else:
                        errors += 1

            mouse_path.append(pygame.mouse.get_pos())
            clock.tick(60)

    save_trial_data(participant_id, trial_data)

def calculate_mouse_distance(path):
    dist = 0
    for i in range(1, len(path)):
        dist += math.dist(path[i], path[i-1])
    return dist
