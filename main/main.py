'''
Fitts' Law Experiment Main File
This file initializes the Pygame window and handles the main loop for the experiment.
It imports necessary modules and functions from other files in the project.
The main function handles the flow of the experiment, including the welcome screen, informed consent form, and running the experiment.
'''

import pygame
import sys
from experiment import run_experiment
from screens import welcome_screen, icf_screen
from utils import generate_participant_id

pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Fitts' Law Experiment")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 28)

def main():
    while True:
        welcome_result = welcome_screen(screen, font)
        if welcome_result == "start":
            consent = icf_screen(screen, font)
            if consent == "agree":
                participant_id = generate_participant_id()
                run_experiment(screen, clock, font, participant_id)
            else:
                continue  # Go back to welcome screen
        elif welcome_result == "quit":
            pygame.quit()
            sys.exit()

if __name__ == "__main__":
    main()
