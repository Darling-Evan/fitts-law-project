# Fitts' Law Experiment using Pygame
import pygame
import sys
import random
import math
import time
import csv
import uuid
import os
from pygame.locals import *

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
WHITE = (0, 0, 0)
BLACK = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
GRAY = (200, 200, 200)

# Experiment Parameters
TARGET_SIZES = [20, 40, 60]  
TARGET_DISTANCES = [100, 200, 300]  
DIRECTIONS = ["left", "right"]
TRIALS_PER_CONFIG = 10

class FittsLawExperiment:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Fitts' Law Experiment")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        self.scroll_position = 0
        
        # Create data directory if it doesn't exist
        if not os.path.exists("data"):
            os.makedirs("data")
        
        # Experiment state
        self.state = "welcome"  
        self.participant_id = str(uuid.uuid4())[:8]  
        self.trial_data = []
        self.current_trial = 0
        self.generate_trial_sequence()
        
        # Current trial variables
        self.start_time = 0
        self.errors = 0
        self.start_pos = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.target_pos = (0, 0)
        self.mouse_path = []
        
    def generate_trial_sequence(self):
        """Generate randomized trial sequence for all configurations."""
        self.trials = []
        # Create all combinations
        for size in TARGET_SIZES:
            for distance in TARGET_DISTANCES:
                for direction in DIRECTIONS:
                    for _ in range(TRIALS_PER_CONFIG):
                        self.trials.append({
                            "size": size,
                            "distance": distance,
                            "direction": direction
                        })
        # Shuffle trials
        random.shuffle(self.trials)
    
    def setup_trial(self):
        """Setup a new trial with current configuration."""
        trial_config = self.trials[self.current_trial]
        self.current_size = trial_config["size"]
        self.current_distance = trial_config["distance"]
        self.current_direction = trial_config["direction"]
        
        # Calculate target position
        center_x = SCREEN_WIDTH // 2
        center_y = SCREEN_HEIGHT // 2
        
        if self.current_direction == "left":
            target_x = center_x - self.current_distance
        else:
            target_x = center_x + self.current_distance
        
        self.target_pos = (target_x, center_y)
        self.start_pos = (center_x, center_y)
        
        # Reset trial variables
        self.errors = 0
        self.mouse_path = [(center_x, center_y)]  
        self.waiting_for_center_click = True
        
    def calculate_distance_traveled(self):
        """Calculate the total distance traveled by the mouse during the trial."""
        total_distance = 0
        for i in range(1, len(self.mouse_path)):
            # Calculate Euclidean distance between consecutive points
            x1, y1 = self.mouse_path[i-1]
            x2, y2 = self.mouse_path[i]
            distance = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
            total_distance += distance
        return total_distance
    
    def is_target_hit(self, pos):
        """Check if the given position is within the target."""
        x, y = pos
        target_x, target_y = self.target_pos
        distance = math.sqrt((x - target_x)**2 + (y - target_y)**2)
        return distance <= self.current_size / 2
    
    def save_data(self):
        """Save all trial data to a CSV file."""
        filename = f"data/fitts_law_{self.participant_id}.csv"
        with open(filename, 'w', newline='') as csvfile:
            fieldnames = ['trial', 'size', 'distance', 'direction', 
                          'time_ms', 'distance_traveled', 'errors']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for i, data in enumerate(self.trial_data):
                writer.writerow({
                    'trial': i + 1,
                    'size': data['size'],
                    'distance': data['distance'],
                    'direction': data['direction'],
                    'time_ms': data['time_ms'],
                    'distance_traveled': data['distance_traveled'],
                    'errors': data['errors']
                })
        print(f"Data saved to {filename}")
    
    def draw_welcome_screen(self):
        """Draw the welcome screen."""
        self.screen.fill(WHITE)
        
        title = self.font.render("Fitts' Law Experiment", True, BLACK)
        title_rect = title.get_rect(center=(SCREEN_WIDTH//2, 100))
        self.screen.blit(title, title_rect)
        
        instruction = self.small_font.render("Welcome to the Fitts' Law experiment.", True, BLACK)
        instruction_rect = instruction.get_rect(center=(SCREEN_WIDTH//2, 200))
        self.screen.blit(instruction, instruction_rect)
        
        start_text = self.small_font.render("Click to continue to the consent form", True, BLACK)
        start_rect = start_text.get_rect(center=(SCREEN_WIDTH//2, 300))
        self.screen.blit(start_text, start_rect)
        
        pygame.display.flip()
    
    def draw_consent_screen(self):
        """Draw the informed consent screen."""
        self.screen.fill(WHITE)
        
        title = self.font.render("Informed Consent", True, BLACK)
        title_rect = title.get_rect(center=(SCREEN_WIDTH//2, 50))
        self.screen.blit(title, title_rect)
        
        
        consent_text = [
            "INFORMED CONSENT DOCUMENT",
            "",
            "Please read the following informed consent document. If you consent to the study,",
            "click 'I Agree' below. If you do not consent and would like to cancel your",
            "participation in the study, click 'I Decline'.",
            "",
            "Project Title: CS470 HCI - Fitts' Law study",
            "",
            "Research Team:",
            "",
            "Adam Chase: adam.chase@mnsu.edu",
            "Evan Darling: evan.darling@mnsu.edu",
            "GROUP MEMBER: EMAIL ADDRESS",
            "GROUP MEMBER: EMAIL ADDRESS",
            "",
            "Thank you for agreeing to participate in this research study! This document provides",
            "important information about what you will be asked to do during the research study,",
            "about the risks and benefits of the study, and about your rights as a research subject.",
            "",
            "The purpose of this research study is to evaluate how quickly and accurately a user can",
            "click on differently-sized targets on screen at varying distances. During the study,",
            "you will be randomly presented with targets of different sizes placed at different",
            "distances from a starting point. There will be a total of 180 trials, and each trial",
            "will take a few seconds, depending on your speed. The entire study should take no",
            "longer than 15-20 minutes to complete.",
            "",
            "To participate in this study, you must:",
            "* Be at least 18 years of age",
            "* Be able to use a computer mouse/trackpad without assistive devices",
            "",
            "To collect data, our software will record your mouse movements, how long it takes you",
            "to successfully click on each target, and whether you make any errors. This information",
            "will be recorded anonymously with a randomly generated participant ID, and no personally",
            "identifiable information will be collected.",
            "",
            "You will not be compensated for your participation in this study. We do not believe",
            "there are any direct benefits to you based on your participation in the study, but your",
            "participation will contribute to our understanding of human-computer interaction.",
            "We do not anticipate any significant risks in your participating in this study.",
            "",
            "You may end your participation in the study at any time. If you wish to end your",
            "participation, press the ESC key. If you decide to end your participation early,",
            "any results collected for your session will not be saved.",
            "",
            "By clicking 'I Agree', you hereby acknowledge that you are at least 18 years of age,",
            "and that you are able to use a computer mouse/trackpad without assistive devices.",
            "You also indicate that you agree to the following statement:",
            "",
            "'I have read this consent form and I understand the risks, benefits, and procedures",
            "involved with participation in this research study. I hereby agree to participate in",
            "this research study.'"
        ]
        
        #calc vertical position for scrollable content
        y_pos = 100
        visible_lines = 15

        # display text with scolling if needed
        start_line = int(self.scroll_position)
        end_line = min(start_line + visible_lines, len(consent_text))

        for i in range(start_line, end_line):
            line = consent_text[i]
            text = self.small_font.render(line, True, BLACK)
            self.screen.blit(text, (50, y_pos + (i - start_line) * 25))

        # draw scroll indicator
        if len(consent_text) > visible_lines:
            pygame.draw.rect(self.screen, GRAY, (SCREEN_WIDTH - 30, 100, 20, 300))

            # draw scroll position indicator 
            scroll_ratio  = start_line / max(1, len(consent_text) - visible_lines)
            scroll_height = 300 * (visible_lines / len(consent_text))
            scroll_pos = 100 + scroll_ratio * (300 - scroll_height)
            pygame.draw.rect(self.screen, BLACK, (SCREEN_WIDTH - 30, scroll_pos, 20, scroll_height))
        
        # draw buttons 
        pygame.draw.rect(self.screen, GREEN, (SCREEN_WIDTH//2 - 120, 490, 100, 50))
        pygame.draw.rect(self.screen, RED, (SCREEN_WIDTH//2 + 20, 490, 100, 50))

        agree = self.small_font.render("I Agree", True, BLACK)
        agree_rect = agree.get_rect(center=(SCREEN_WIDTH//2 - 70, 515))
        self.screen.blit(agree, agree_rect)

        disagree = self.small_font.render("I Decline", True, BLACK)
        disagree_rect = disagree.get_rect(center=(SCREEN_WIDTH//2 + 70, 515))
        self.screen.blit(disagree, disagree_rect)

        # Draw scroll instructions
        scroll_instruction = self.small_font.render("Scroll with mouse wheel", True, BLACK)
        self.screen.blit(scroll_instruction, (50, SCREEN_HEIGHT - 50))

        # store button positions 
        self.agree_button_rect = pygame.Rect(SCREEN_WIDTH//2 - 120, 490, 100, 50)
        self.decline_button_rect = pygame.Rect(SCREEN_WIDTH//2 + 20, 490, 100, 50)

        pygame.display.flip()
    
    def draw_instruction_screen(self):
        """Draw the instruction screen."""
        self.screen.fill(WHITE)
        
        title = self.font.render("Instructions", True, BLACK)
        title_rect = title.get_rect(center=(SCREEN_WIDTH//2, 50))
        self.screen.blit(title, title_rect)
        
        instructions = [
            "1. For each trial, first click the blue circle in the center.",
            "2. Then, as quickly as possible, click the red target that appears.",
            "3. Try to be both fast and accurate.",
            "4. You will complete 180 trials in total.",
            "",
            "Press ESC at any time to exit the experiment.",
            "",
            "Click anywhere to begin the experiment."
        ]
        
        for i, line in enumerate(instructions):
            text = self.small_font.render(line, True, BLACK)
            text_rect = text.get_rect(center=(SCREEN_WIDTH//2, 120 + i*30))
            self.screen.blit(text, text_rect)
        
        pygame.display.flip()
    
    def draw_trial_screen(self):
        """Draw the current trial screen."""
        self.screen.fill(WHITE)
        
        # Draw progress indicator
        progress = self.font.render(f"Trial: {self.current_trial + 1}/{len(self.trials)}", True, BLACK)
        self.screen.blit(progress, (20, 20))
        
        # Draw center starting point
        if self.waiting_for_center_click:
            pygame.draw.circle(self.screen, BLUE, self.start_pos, 15)
        else:
            pygame.draw.circle(self.screen, GRAY, self.start_pos, 15)
            
            # Draw target
            pygame.draw.circle(self.screen, RED, self.target_pos, self.current_size // 2)
        
        pygame.display.flip()
    
    def draw_feedback_screen(self):
        """Draw feedback after a trial."""
        self.screen.fill(WHITE)
        
        # Show time taken
        last_trial = self.trial_data[-1]
        time_text = self.font.render(f"Time: {last_trial['time_ms']:.0f} ms", True, BLACK)
        time_rect = time_text.get_rect(center=(SCREEN_WIDTH//2, 200))
        self.screen.blit(time_text, time_rect)
        
        # Show errors
        error_text = self.font.render(f"Errors: {last_trial['errors']}", True, BLACK)
        error_rect = error_text.get_rect(center=(SCREEN_WIDTH//2, 250))
        self.screen.blit(error_text, error_rect)
        
        # Continue instruction
        continue_text = self.small_font.render("Click to continue to the next trial", True, BLACK)
        continue_rect = continue_text.get_rect(center=(SCREEN_WIDTH//2, 350))
        self.screen.blit(continue_text, continue_rect)
        
        pygame.display.flip()
    
    def draw_completion_screen(self):
        """Draw the experiment completion screen."""
        self.screen.fill(WHITE)
        
        thanks = self.font.render("Thank you for participating!", True, BLACK)
        thanks_rect = thanks.get_rect(center=(SCREEN_WIDTH//2, 200))
        self.screen.blit(thanks, thanks_rect)
        
        id_text = self.small_font.render(f"Your participant ID: {self.participant_id}", True, BLACK)
        id_rect = id_text.get_rect(center=(SCREEN_WIDTH//2, 250))
        self.screen.blit(id_text, id_rect)
        
        exit_text = self.small_font.render("You may now close this window", True, BLACK)
        exit_rect = exit_text.get_rect(center=(SCREEN_WIDTH//2, 300))
        self.screen.blit(exit_text, exit_rect)
        
        pygame.display.flip()
    
    def handle_events(self):
        """Handle pygame events based on current state."""
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                return False
            
            if event.type == MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                
                if self.state == "welcome":
                    self.state = "consent"
                
                elif self.state == "consent":
                    # Check if clicked on "I Agree" button
                    if hasattr(self, 'agree_button_rect') and self.agree_button_rect.collidepoint(mouse_pos):
                        print(f"Participant {self.participant_id} has consented to the experiment")
                        self.state = "instruction"
                
                    # Check if clicked on "I Decline" button
                    elif hasattr(self, 'decline_button_rect') and self.decline_button_rect.collidepoint(mouse_pos):
                        print("Participant declined consent, exiting")
                        return False
                
                elif self.state == "instruction":
                    self.state = "trial"
                    self.setup_trial()
                
                elif self.state == "trial":
                    if self.waiting_for_center_click:
                        # Check if clicked on the center circle
                        center_x, center_y = self.start_pos
                        if math.sqrt((mouse_pos[0] - center_x)**2 + (mouse_pos[1] - center_y)**2) <= 15:
                            self.waiting_for_center_click = False
                            self.start_time = time.time()
                            # Clear mouse path and start fresh
                            self.mouse_path = [self.start_pos]
                    else:
                        # Check if clicked on the target
                        if self.is_target_hit(mouse_pos):
                            end_time = time.time()
                            trial_time_ms = (end_time - self.start_time) * 1000
                            distance_traveled = self.calculate_distance_traveled()
                            
                            # Save trial data
                            self.trial_data.append({
                                'size': self.current_size,
                                'distance': self.current_distance,
                                'direction': self.current_direction,
                                'time_ms': trial_time_ms,
                                'distance_traveled': distance_traveled,
                                'errors': self.errors
                            })
                            
                            self.state = "feedback"
                        else:
                            self.errors += 1
                
                elif self.state == "feedback":
                    self.current_trial += 1
                    if self.current_trial < len(self.trials):
                        self.state = "trial"
                        self.setup_trial()
                    else:
                        self.save_data()
                        self.state = "completion"
                
                elif self.state == "completion":
                    return False
            
            # Track mouse movement during trials
            if self.state == "trial" and not self.waiting_for_center_click:
                if event.type == MOUSEMOTION:
                    self.mouse_path.append(pygame.mouse.get_pos())
            # Handle mouse wheel scrolling for consent screen
            if self.state == "consent" and event.type == pygame.MOUSEWHEEL:
                total_lines = 39  
                visible_lines = 15
            
            # Update scroll position (adjust the 0.5 value to control scroll speed)
                self.scroll_position = max(0, min(self.scroll_position - event.y * 1.0, 
                                             total_lines - visible_lines))
        return True
    
    def run(self):
        """Main loop of the experiment."""
        running = True
        while running:
            if self.state == "welcome":
                self.draw_welcome_screen()
            elif self.state == "consent":
                self.draw_consent_screen()
            elif self.state == "instruction":
                self.draw_instruction_screen()
            elif self.state == "trial":
                self.draw_trial_screen()
            elif self.state == "feedback":
                self.draw_feedback_screen()
            elif self.state == "completion":
                self.draw_completion_screen()
            
            running = self.handle_events()
            self.clock.tick(60)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    experiment = FittsLawExperiment()
    experiment.run()