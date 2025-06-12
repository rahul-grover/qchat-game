import pygame
import random
import math
import json
import os
from datetime import datetime

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# Constants
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 600
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (100, 150, 255)
GREEN = (100, 255, 100)
RED = (255, 100, 100)
YELLOW = (255, 255, 100)
PURPLE = (200, 100, 255)
ORANGE = (255, 165, 0)
PINK = (255, 192, 203)
LIGHT_BLUE = (173, 216, 230)

# Game settings
GRAVITY = 0.8
JUMP_STRENGTH = -15
PLAYER_SPEED = 5

# Points system
POINTS_PER_CORRECT = 10
BONUS_POINTS_MULTIPLIER = 2  # Bonus for consecutive correct answers
QUESTIONS_PER_LEVEL = 5

# Leaderboard file
LEADERBOARD_FILE = "leaderboard.json"

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 40
        self.height = 50
        self.vel_x = 0
        self.vel_y = 0
        self.on_ground = False
        self.color = BLUE
        
    def update(self, platforms):
        keys = pygame.key.get_pressed()
        
        # Horizontal movement
        self.vel_x = 0
        if keys[pygame.K_LEFT]:
            self.vel_x = -PLAYER_SPEED
        if keys[pygame.K_RIGHT]:
            self.vel_x = PLAYER_SPEED
            
        # Jumping
        if keys[pygame.K_UP] and self.on_ground:
            self.vel_y = JUMP_STRENGTH
            
        # Apply gravity
        self.vel_y += GRAVITY
        
        # Update position
        self.x += self.vel_x
        self.y += self.vel_y
        
        # Keep player on screen horizontally
        if self.x < 0:
            self.x = 0
        elif self.x + self.width > SCREEN_WIDTH:
            self.x = SCREEN_WIDTH - self.width
            
        # Check platform collisions
        self.on_ground = False
        player_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        
        for platform in platforms:
            platform_rect = pygame.Rect(platform[0], platform[1], platform[2], platform[3])
            if player_rect.colliderect(platform_rect):
                # Landing on top of platform
                if self.vel_y > 0 and self.y < platform[1]:
                    self.y = platform[1] - self.height
                    self.vel_y = 0
                    self.on_ground = True
                # Hitting platform from below
                elif self.vel_y < 0 and self.y > platform[1]:
                    self.y = platform[1] + platform[3]
                    self.vel_y = 0
                    
        # Ground collision
        if self.y + self.height >= SCREEN_HEIGHT - 50:
            self.y = SCREEN_HEIGHT - 50 - self.height
            self.vel_y = 0
            self.on_ground = True
            
    def draw(self, screen):
        # Draw player as a cute character
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
        # Eyes
        pygame.draw.circle(screen, WHITE, (int(self.x + 10), int(self.y + 15)), 5)
        pygame.draw.circle(screen, WHITE, (int(self.x + 30), int(self.y + 15)), 5)
        pygame.draw.circle(screen, BLACK, (int(self.x + 12), int(self.y + 15)), 2)
        pygame.draw.circle(screen, BLACK, (int(self.x + 32), int(self.y + 15)), 2)
        # Smile
        pygame.draw.arc(screen, BLACK, (self.x + 10, self.y + 25, 20, 15), 0, math.pi, 2)

class Leaderboard:
    def __init__(self):
        self.scores = self.load_scores()
    
    def load_scores(self):
        try:
            if os.path.exists(LEADERBOARD_FILE):
                with open(LEADERBOARD_FILE, 'r') as f:
                    return json.load(f)
            return []
        except:
            return []
    
    def save_scores(self):
        try:
            with open(LEADERBOARD_FILE, 'w') as f:
                json.dump(self.scores, f, indent=2)
        except:
            pass
    
    def add_score(self, name, score, level):
        entry = {
            'name': name,
            'score': score,
            'level': level,
            'date': datetime.now().strftime('%Y-%m-%d %H:%M')
        }
        self.scores.append(entry)
        # Sort by score (descending) then by level (descending)
        self.scores.sort(key=lambda x: (x['score'], x['level']), reverse=True)
        # Keep only top 10
        self.scores = self.scores[:10]
        self.save_scores()
    
    def get_top_scores(self, limit=10):
        return self.scores[:limit]
        self.x = x
        self.y = y
        self.width = 60
        self.height = 80
        self.question_level = question_level
        self.opened = False
        self.color = YELLOW if not self.opened else GREEN
        
    def draw(self, screen):
        color = GREEN if self.opened else YELLOW
        pygame.draw.rect(screen, color, (self.x, self.y, self.width, self.height))
        pygame.draw.rect(screen, BLACK, (self.x, self.y, self.width, self.height), 3)
        
        # Door handle
        pygame.draw.circle(screen, BLACK, (int(self.x + 45), int(self.y + 40)), 5)
        
        # Question mark if not opened
        if not self.opened:
            font = pygame.font.Font(None, 36)
            text = font.render("?", True, BLACK)
            text_rect = text.get_rect(center=(self.x + self.width//2, self.y + self.height//2))
            screen.blit(text, text_rect)

class MathQuestion:
    def __init__(self, level, question_number):
        self.level = level
        self.question_number = question_number
        self.generate_question()
        
    def generate_question(self):
        # Difficulty increases with level
        if self.level == 1:
            # Level 1: Simple addition/subtraction (1-10)
            self.num1 = random.randint(1, 10)
            self.num2 = random.randint(1, 10)
            if random.choice([True, False]):
                self.operation = "+"
                self.correct_answer = self.num1 + self.num2
                self.question = f"{self.num1} + {self.num2} = ?"
            else:
                if self.num1 < self.num2:
                    self.num1, self.num2 = self.num2, self.num1
                self.operation = "-"
                self.correct_answer = self.num1 - self.num2
                self.question = f"{self.num1} - {self.num2} = ?"
                
        elif self.level == 2:
            # Level 2: Medium addition/subtraction (10-25)
            self.num1 = random.randint(10, 25)
            self.num2 = random.randint(5, 15)
            if random.choice([True, False]):
                self.operation = "+"
                self.correct_answer = self.num1 + self.num2
                self.question = f"{self.num1} + {self.num2} = ?"
            else:
                self.operation = "-"
                self.correct_answer = self.num1 - self.num2
                self.question = f"{self.num1} - {self.num2} = ?"
                
        elif self.level == 3:
            # Level 3: Larger numbers + simple multiplication
            if random.choice([True, False, False]):  # 1/3 chance multiplication
                self.num1 = random.randint(2, 8)
                self.num2 = random.randint(2, 8)
                self.operation = "×"
                self.correct_answer = self.num1 * self.num2
                self.question = f"{self.num1} × {self.num2} = ?"
            else:
                self.num1 = random.randint(20, 50)
                self.num2 = random.randint(10, 25)
                if random.choice([True, False]):
                    self.operation = "+"
                    self.correct_answer = self.num1 + self.num2
                    self.question = f"{self.num1} + {self.num2} = ?"
                else:
                    self.operation = "-"
                    self.correct_answer = self.num1 - self.num2
                    self.question = f"{self.num1} - {self.num2} = ?"
                    
        elif self.level == 4:
            # Level 4: More multiplication + larger numbers
            if random.choice([True, False]):  # 50% chance multiplication
                self.num1 = random.randint(3, 12)
                self.num2 = random.randint(3, 12)
                self.operation = "×"
                self.correct_answer = self.num1 * self.num2
                self.question = f"{self.num1} × {self.num2} = ?"
            else:
                self.num1 = random.randint(50, 100)
                self.num2 = random.randint(20, 40)
                if random.choice([True, False]):
                    self.operation = "+"
                    self.correct_answer = self.num1 + self.num2
                    self.question = f"{self.num1} + {self.num2} = ?"
                else:
                    self.operation = "-"
                    self.correct_answer = self.num1 - self.num2
                    self.question = f"{self.num1} - {self.num2} = ?"
                    
        else:  # Level 5+
            # Level 5+: Advanced problems
            operation_choice = random.choice(["add", "sub", "mult", "mult"])  # More multiplication
            if operation_choice == "mult":
                self.num1 = random.randint(5, 15)
                self.num2 = random.randint(5, 15)
                self.operation = "×"
                self.correct_answer = self.num1 * self.num2
                self.question = f"{self.num1} × {self.num2} = ?"
            elif operation_choice == "add":
                self.num1 = random.randint(75, 150)
                self.num2 = random.randint(25, 75)
                self.operation = "+"
                self.correct_answer = self.num1 + self.num2
                self.question = f"{self.num1} + {self.num2} = ?"
            else:  # subtraction
                self.num1 = random.randint(100, 200)
                self.num2 = random.randint(25, 75)
                self.operation = "-"
                self.correct_answer = self.num1 - self.num2
                self.question = f"{self.num1} - {self.num2} = ?"
        
        # Generate wrong answers
        self.answers = [self.correct_answer]
        while len(self.answers) < 4:
            if self.operation == "×":
                wrong = self.correct_answer + random.randint(-15, 15)
            else:
                wrong = self.correct_answer + random.randint(-10, 10)
            if wrong not in self.answers and wrong >= 0:
                self.answers.append(wrong)
        
        random.shuffle(self.answers)
        self.correct_index = self.answers.index(self.correct_answer)

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Math Quiz Adventure")
        self.clock = pygame.time.Clock()
        self.font_large = pygame.font.Font(None, 48)
        self.font_medium = pygame.font.Font(None, 36)
        self.font_small = pygame.font.Font(None, 24)
        
        # Create simple sound effects
        self.create_sounds()
        
        # Game state
        self.player = Player(50, SCREEN_HEIGHT - 100)
        self.platforms = [
            [200, 500, 150, 20],
            [400, 400, 150, 20],
            [600, 300, 150, 20],
            [800, 450, 150, 20],
            [300, 200, 150, 20],
            [700, 150, 150, 20],
            [100, 350, 100, 20],
            [850, 250, 100, 20]
        ]
        
        self.doors = [
            Door(320, 420, 1),
            Door(520, 220, 2),
            Door(720, 370, 3),
            Door(420, 120, 4),
            Door(820, 170, 5)
        ]
        
        self.current_question = None
        self.show_question = False
        self.question_result = None
        self.doors_opened = 0
        self.game_won = False
        
    def create_sounds(self):
        # Create simple beep sounds
        try:
            # Correct answer sound (higher pitch)
            self.correct_sound = pygame.mixer.Sound(buffer=b'\x00\x00' * 1000)
            # Incorrect answer sound (lower pitch)
            self.incorrect_sound = pygame.mixer.Sound(buffer=b'\x00\x00' * 1000)
        except:
            self.correct_sound = None
            self.incorrect_sound = None
    
    def play_correct_sound(self):
        if self.correct_sound:
            try:
                self.correct_sound.play()
            except:
                pass
    
    def play_incorrect_sound(self):
        if self.incorrect_sound:
            try:
                self.incorrect_sound.play()
            except:
                pass
    
    def check_door_collision(self):
        player_rect = pygame.Rect(self.player.x, self.player.y, self.player.width, self.player.height)
        for door in self.doors:
            if not door.opened:
                door_rect = pygame.Rect(door.x, door.y, door.width, door.height)
                if player_rect.colliderect(door_rect):
                    self.current_question = MathQuestion(door.question_level)
                    self.show_question = True
                    self.current_door = door
                    return True
        return False
    
    def handle_question_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1:
                self.check_answer(0)
            elif event.key == pygame.K_2:
                self.check_answer(1)
            elif event.key == pygame.K_3:
                self.check_answer(2)
            elif event.key == pygame.K_4:
                self.check_answer(3)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            # Check if clicked on answer buttons
            button_width = 200
            button_height = 60
            start_x = SCREEN_WIDTH // 2 - button_width // 2
            start_y = 300
            
            for i in range(4):
                button_y = start_y + i * 80
                if start_x <= mouse_x <= start_x + button_width and button_y <= mouse_y <= button_y + button_height:
                    self.check_answer(i)
                    break
    
    def check_answer(self, selected_index):
        if selected_index == self.current_question.correct_index:
            self.question_result = "correct"
            self.play_correct_sound()
            self.current_door.opened = True
            self.doors_opened += 1
            if self.doors_opened >= len(self.doors):
                self.game_won = True
        else:
            self.question_result = "incorrect"
            self.play_incorrect_sound()
    
    def draw_question(self):
        # Semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        # Question box
        box_width = 600
        box_height = 400
        box_x = SCREEN_WIDTH // 2 - box_width // 2
        box_y = SCREEN_HEIGHT // 2 - box_height // 2
        
        pygame.draw.rect(self.screen, WHITE, (box_x, box_y, box_width, box_height))
        pygame.draw.rect(self.screen, BLACK, (box_x, box_y, box_width, box_height), 5)
        
        # Question text
        question_text = self.font_large.render(self.current_question.question, True, BLACK)
        question_rect = question_text.get_rect(center=(SCREEN_WIDTH // 2, box_y + 80))
        self.screen.blit(question_text, question_rect)
        
        # Answer buttons
        button_width = 200
        button_height = 60
        start_x = SCREEN_WIDTH // 2 - button_width // 2
        start_y = 300
        
        for i, answer in enumerate(self.current_question.answers):
            button_y = start_y + i * 80
            button_color = LIGHT_BLUE
            
            # Highlight correct/incorrect answers if result is shown
            if self.question_result:
                if i == self.current_question.correct_index:
                    button_color = GREEN
                elif self.question_result == "incorrect":
                    button_color = RED
            
            pygame.draw.rect(self.screen, button_color, (start_x, button_y, button_width, button_height))
            pygame.draw.rect(self.screen, BLACK, (start_x, button_y, button_width, button_height), 3)
            
            # Answer text
            answer_text = self.font_medium.render(f"{i+1}. {answer}", True, BLACK)
            answer_rect = answer_text.get_rect(center=(start_x + button_width // 2, button_y + button_height // 2))
            self.screen.blit(answer_text, answer_rect)
        
        # Instructions
        if not self.question_result:
            instruction_text = self.font_small.render("Click on an answer or press 1-4", True, BLACK)
            instruction_rect = instruction_text.get_rect(center=(SCREEN_WIDTH // 2, box_y + box_height - 30))
            self.screen.blit(instruction_text, instruction_rect)
        else:
            if self.question_result == "correct":
                result_text = self.font_medium.render("Correct! Press SPACE to continue", True, GREEN)
            else:
                result_text = self.font_medium.render("Try again! Press SPACE", True, RED)
            result_rect = result_text.get_rect(center=(SCREEN_WIDTH // 2, box_y + box_height - 30))
            self.screen.blit(result_text, result_rect)
    
    def draw_background(self):
        # Gradient background
        for y in range(SCREEN_HEIGHT):
            color_ratio = y / SCREEN_HEIGHT
            r = int(135 + (255 - 135) * color_ratio)
            g = int(206 + (255 - 206) * color_ratio)
            b = int(235 + (255 - 235) * color_ratio)
            pygame.draw.line(self.screen, (r, g, b), (0, y), (SCREEN_WIDTH, y))
    
    def draw_platforms(self):
        for platform in self.platforms:
            pygame.draw.rect(self.screen, GREEN, platform)
            pygame.draw.rect(self.screen, BLACK, platform, 2)
    
    def draw_ground(self):
        pygame.draw.rect(self.screen, GREEN, (0, SCREEN_HEIGHT - 50, SCREEN_WIDTH, 50))
        pygame.draw.rect(self.screen, BLACK, (0, SCREEN_HEIGHT - 50, SCREEN_WIDTH, 50), 3)
    
    def draw_ui(self):
        # Score
        score_text = self.font_medium.render(f"Doors Opened: {self.doors_opened}/{len(self.doors)}", True, BLACK)
        self.screen.blit(score_text, (10, 10))
        
        # Instructions
        if not self.show_question:
            instruction_text = self.font_small.render("Use arrow keys to move and jump. Touch doors to answer math questions!", True, BLACK)
            self.screen.blit(instruction_text, (10, SCREEN_HEIGHT - 30))
    
    def draw_win_screen(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill(PURPLE)
        self.screen.blit(overlay, (0, 0))
        
        win_text = self.font_large.render("Congratulations! You completed all the math challenges!", True, WHITE)
        win_rect = win_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        self.screen.blit(win_text, win_rect)
        
        restart_text = self.font_medium.render("Press R to play again or ESC to quit", True, WHITE)
        restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
        self.screen.blit(restart_text, restart_rect)
    
    def reset_game(self):
        self.player = Player(50, SCREEN_HEIGHT - 100)
        self.doors = [
            Door(320, 420, 1),
            Door(520, 220, 2),
            Door(720, 370, 3),
            Door(420, 120, 4),
            Door(820, 170, 5)
        ]
        self.doors_opened = 0
        self.game_won = False
        self.show_question = False
        self.question_result = None
    
    def run(self):
        running = True
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_r and self.game_won:
                        self.reset_game()
                    elif event.key == pygame.K_SPACE and self.show_question and self.question_result:
                        if self.question_result == "correct":
                            self.show_question = False
                            self.question_result = None
                        else:
                            self.question_result = None
                
                if self.show_question and not self.question_result:
                    self.handle_question_input(event)
            
            if not self.show_question and not self.game_won:
                self.player.update(self.platforms)
                if self.check_door_collision():
                    pass  # Question will be shown
            
            # Draw everything
            self.draw_background()
            self.draw_ground()
            self.draw_platforms()
            
            for door in self.doors:
                door.draw(self.screen)
            
            if not self.show_question:
                self.player.draw(self.screen)
            
            self.draw_ui()
            
            if self.show_question:
                self.draw_question()
            
            if self.game_won:
                self.draw_win_screen()
            
            pygame.display.flip()
            self.clock.tick(FPS)
        
        pygame.quit()

if __name__ == "__main__":
    game = Game()
    game.run()
