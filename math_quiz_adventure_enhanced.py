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
GOLD = (255, 215, 0)

# Game settings
GRAVITY = 0.8
JUMP_STRENGTH = -15
PLAYER_SPEED = 5

# Points system
POINTS_PER_CORRECT = 10
BONUS_POINTS_MULTIPLIER = 2
QUESTIONS_PER_LEVEL = 5
LEVEL_COMPLETION_BONUS = 50

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

class Door:
    def __init__(self, x, y, question_number):
        self.x = x
        self.y = y
        self.width = 60
        self.height = 80
        self.question_number = question_number
        self.opened = False
        
    def draw(self, screen):
        color = GREEN if self.opened else YELLOW
        pygame.draw.rect(screen, color, (self.x, self.y, self.width, self.height))
        pygame.draw.rect(screen, BLACK, (self.x, self.y, self.width, self.height), 3)
        
        # Door handle
        pygame.draw.circle(screen, BLACK, (int(self.x + 45), int(self.y + 40)), 5)
        
        # Question number if not opened
        if not self.opened:
            font = pygame.font.Font(None, 24)
            text = font.render(f"Q{self.question_number}", True, BLACK)
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

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Math Quiz Adventure - Enhanced Edition")
        self.clock = pygame.time.Clock()
        self.font_large = pygame.font.Font(None, 48)
        self.font_medium = pygame.font.Font(None, 36)
        self.font_small = pygame.font.Font(None, 24)
        
        # Create simple sound effects
        self.create_sounds()
        
        # Game state flags
        self.game_started = False
        self.show_name_input_start = True
        self.show_level_transition = False
        self.transition_timer = 0
        
        # Initialize game state
        self.reset_game()
        
        # Leaderboard
        self.leaderboard = Leaderboard()
        self.show_leaderboard = False
        self.show_name_input = False
        self.player_name = ""
        
    def reset_game(self):
        # Initialize level and scoring system first
        self.current_level = 1
        self.questions_answered = 0
        self.questions_correct = 0
        self.consecutive_correct = 0
        self.score = 0
        self.level_completed = False
        self.game_won = False
        self.game_started = False
        self.show_name_input_start = True
        self.show_level_transition = False
        
        # Now setup player and level layout
        self.player = Player(50, SCREEN_HEIGHT - 100)
        self.setup_level_layout()
        
        # Game state
        self.current_question = None
        self.show_question = False
        self.question_result = None
        self.current_door = None
        
    def setup_level_layout(self):
        """Create different maze layouts for each level"""
        if self.current_level == 1:
            # Level 1: Simple layout - easy jumps
            self.platforms = [
                [200, 500, 150, 20],
                [400, 400, 150, 20],
                [600, 300, 150, 20],
                [300, 200, 150, 20],
                [700, 150, 150, 20]
            ]
            self.doors = [
                Door(320, 420, 1),
                Door(520, 220, 2),
                Door(720, 370, 3),
                Door(420, 120, 4),
                Door(820, 70, 5)
            ]
        elif self.current_level == 2:
            # Level 2: Medium complexity - more platforms
            self.platforms = [
                [150, 450, 120, 20],
                [350, 350, 120, 20],
                [550, 450, 120, 20],
                [750, 300, 120, 20],
                [200, 250, 120, 20],
                [500, 200, 120, 20],
                [800, 150, 120, 20]
            ]
            self.doors = [
                Door(270, 370, 1),
                Door(470, 370, 2),
                Door(670, 370, 3),
                Door(320, 170, 4),
                Door(920, 70, 5)
            ]
        elif self.current_level == 3:
            # Level 3: Vertical challenge - tower climbing
            self.platforms = [
                [100, 500, 100, 20],
                [300, 450, 100, 20],
                [500, 400, 100, 20],
                [700, 350, 100, 20],
                [200, 300, 100, 20],
                [400, 250, 100, 20],
                [600, 200, 100, 20],
                [800, 150, 100, 20]
            ]
            self.doors = [
                Door(220, 420, 1),
                Door(420, 370, 2),
                Door(620, 320, 3),
                Door(320, 220, 4),
                Door(720, 120, 5)
            ]
        elif self.current_level == 4:
            # Level 4: Scattered platforms - precision jumps
            self.platforms = [
                [80, 480, 80, 20],
                [250, 420, 80, 20],
                [450, 380, 80, 20],
                [650, 340, 80, 20],
                [850, 300, 80, 20],
                [150, 280, 80, 20],
                [350, 220, 80, 20],
                [550, 160, 80, 20],
                [750, 100, 80, 20]
            ]
            self.doors = [
                Door(170, 400, 1),
                Door(370, 340, 2),
                Door(570, 300, 3),
                Door(270, 140, 4),
                Door(870, 20, 5)
            ]
        else:  # Level 5
            # Level 5: Complex maze - ultimate challenge
            self.platforms = [
                [50, 500, 100, 20],
                [200, 480, 80, 20],
                [350, 460, 80, 20],
                [500, 440, 80, 20],
                [650, 420, 80, 20],
                [800, 400, 100, 20],
                [100, 380, 80, 20],
                [250, 360, 80, 20],
                [400, 340, 80, 20],
                [550, 320, 80, 20],
                [700, 300, 80, 20],
                [150, 260, 80, 20],
                [300, 240, 80, 20],
                [450, 220, 80, 20],
                [600, 200, 80, 20],
                [750, 180, 80, 20],
                [200, 140, 80, 20],
                [400, 120, 80, 20],
                [600, 100, 80, 20],
                [800, 80, 100, 20]
            ]
            self.doors = [
                Door(170, 400, 1),
                Door(320, 280, 2),
                Door(470, 140, 3),
                Door(520, 40, 4),
                Door(920, 0, 5)
            ]
        
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
                    self.current_question = MathQuestion(self.current_level, door.question_number)
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
            self.questions_answered += 1
            self.questions_correct += 1
            self.consecutive_correct += 1
            
            # Calculate points
            points = POINTS_PER_CORRECT
            if self.consecutive_correct >= 3:
                points *= BONUS_POINTS_MULTIPLIER
            self.score += points
            
            # Check if level is completed (all 5 doors opened)
            doors_opened = sum(1 for door in self.doors if door.opened)
            if doors_opened >= QUESTIONS_PER_LEVEL:
                self.level_completed = True
                self.score += LEVEL_COMPLETION_BONUS
                
        else:
            self.question_result = "incorrect"
            self.play_incorrect_sound()
            self.consecutive_correct = 0
    
    def advance_level(self):
        if self.current_level < 5:
            self.current_level += 1
            self.questions_answered = 0
            self.questions_correct = 0
            self.level_completed = False
            self.show_level_transition = True
            self.transition_timer = 180  # 3 seconds at 60 FPS
            
            # Setup new level layout
            self.setup_level_layout()
            
            # Reset player position
            self.player.x = 50
            self.player.y = SCREEN_HEIGHT - 100
            self.player.vel_x = 0
            self.player.vel_y = 0
        else:
            # Game completed
            self.game_won = True
            self.show_name_input = True
    
    def handle_name_input_start(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                if self.player_name.strip():
                    self.show_name_input_start = False
                    self.game_started = True
            elif event.key == pygame.K_BACKSPACE:
                self.player_name = self.player_name[:-1]
            else:
                if len(self.player_name) < 15 and event.unicode.isprintable():
                    self.player_name += event.unicode
    
    def handle_name_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                if self.player_name.strip():
                    self.leaderboard.add_score(self.player_name.strip(), self.score, self.current_level)
                    self.show_name_input = False
                    self.show_leaderboard = True
            elif event.key == pygame.K_BACKSPACE:
                self.player_name = self.player_name[:-1]
            else:
                if len(self.player_name) < 15 and event.unicode.isprintable():
                    self.player_name += event.unicode
    
    def draw_question(self):
        # Semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(220)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        # Question box - adjusted size to prevent overlaps
        box_width = 650
        box_height = 520
        box_x = SCREEN_WIDTH // 2 - box_width // 2
        box_y = SCREEN_HEIGHT // 2 - box_height // 2
        
        # Draw box with rounded corners effect
        pygame.draw.rect(self.screen, WHITE, (box_x, box_y, box_width, box_height))
        pygame.draw.rect(self.screen, PURPLE, (box_x, box_y, box_width, box_height), 6)
        
        # Header background
        header_height = 70
        pygame.draw.rect(self.screen, LIGHT_BLUE, (box_x, box_y, box_width, header_height))
        pygame.draw.rect(self.screen, PURPLE, (box_x, box_y, box_width, header_height), 6)
        
        # Level and question info - adjusted positioning
        level_text = self.font_large.render(f"Level {self.current_level}", True, PURPLE)
        level_rect = level_text.get_rect(center=(SCREEN_WIDTH // 2, box_y + 25))
        self.screen.blit(level_text, level_rect)
        
        # Show doors opened instead of questions answered
        doors_opened = sum(1 for door in self.doors if door.opened)
        question_info = self.font_medium.render(f"Door {doors_opened + 1} of {QUESTIONS_PER_LEVEL}", True, BLACK)
        info_rect = question_info.get_rect(center=(SCREEN_WIDTH // 2, box_y + 50))
        self.screen.blit(question_info, info_rect)
        
        # Question text - slightly smaller but still prominent
        question_font = pygame.font.Font(None, 52)  # Reduced from 64
        question_text = question_font.render(self.current_question.question, True, BLACK)
        question_rect = question_text.get_rect(center=(SCREEN_WIDTH // 2, box_y + 110))
        self.screen.blit(question_text, question_rect)
        
        # Answer buttons - smaller and better spaced
        button_width = 250
        button_height = 55  # Reduced height
        start_x = SCREEN_WIDTH // 2 - button_width // 2
        start_y = box_y + 160  # Moved up slightly
        button_spacing = 70  # Reduced spacing
        
        for i, answer in enumerate(self.current_question.answers):
            button_y = start_y + i * button_spacing
            button_color = LIGHT_BLUE
            text_color = BLACK
            
            # Highlight correct/incorrect answers if result is shown
            if self.question_result:
                if i == self.current_question.correct_index:
                    button_color = GREEN
                    text_color = WHITE
                elif self.question_result == "incorrect" and i != self.current_question.correct_index:
                    button_color = RED
                    text_color = WHITE
            
            # Draw button with shadow effect
            shadow_offset = 2
            pygame.draw.rect(self.screen, (100, 100, 100), 
                           (start_x + shadow_offset, button_y + shadow_offset, button_width, button_height))
            pygame.draw.rect(self.screen, button_color, (start_x, button_y, button_width, button_height))
            pygame.draw.rect(self.screen, BLACK, (start_x, button_y, button_width, button_height), 3)
            
            # Answer text - more reasonable font size
            answer_font = pygame.font.Font(None, 32)  # Reduced from 42
            answer_text = answer_font.render(f"{i+1}. {answer}", True, text_color)
            answer_rect = answer_text.get_rect(center=(start_x + button_width // 2, button_y + button_height // 2))
            self.screen.blit(answer_text, answer_rect)
        
        # Instructions and results - positioned to avoid overlap
        instruction_y = box_y + box_height - 70  # Moved up more
        result_y = box_y + box_height - 40
        
        if not self.question_result:
            instruction_text = self.font_medium.render("Click on an answer or press 1-4", True, PURPLE)
            instruction_rect = instruction_text.get_rect(center=(SCREEN_WIDTH // 2, instruction_y))
            self.screen.blit(instruction_text, instruction_rect)
        else:
            if self.question_result == "correct":
                points = POINTS_PER_CORRECT
                if self.consecutive_correct >= 3:
                    points *= BONUS_POINTS_MULTIPLIER
                    result_text = self.font_medium.render(f"Correct! +{points} points (BONUS!)", True, GREEN)  # Reduced font size
                else:
                    result_text = self.font_medium.render(f"Correct! +{points} points", True, GREEN)
            else:
                result_text = self.font_medium.render("Try again!", True, RED)
            result_rect = result_text.get_rect(center=(SCREEN_WIDTH // 2, instruction_y))
            self.screen.blit(result_text, result_rect)
            
            continue_text = self.font_small.render("Press SPACE to continue", True, PURPLE)  # Made smaller
            continue_rect = continue_text.get_rect(center=(SCREEN_WIDTH // 2, result_y))
            self.screen.blit(continue_text, continue_rect)
    
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
        # Create a semi-transparent background for UI elements
        ui_bg = pygame.Surface((300, 120))
        ui_bg.set_alpha(180)
        ui_bg.fill(WHITE)
        self.screen.blit(ui_bg, (10, 10))
        
        # Border for UI panel
        pygame.draw.rect(self.screen, BLACK, (10, 10, 300, 120), 3)
        
        # Score and level info with better formatting
        score_text = self.font_large.render(f"Score: {self.score}", True, PURPLE)
        self.screen.blit(score_text, (20, 20))
        
        level_text = self.font_medium.render(f"Level: {self.current_level}", True, BLACK)
        self.screen.blit(level_text, (20, 50))
        
        # Count doors opened instead of questions answered
        doors_opened = sum(1 for door in self.doors if door.opened)
        progress_text = self.font_medium.render(f"Doors: {doors_opened}/{QUESTIONS_PER_LEVEL}", True, BLACK)
        self.screen.blit(progress_text, (20, 75))
        
        # Bonus streak indicator - more prominent
        if self.consecutive_correct >= 3:
            bonus_bg = pygame.Surface((200, 30))
            bonus_bg.set_alpha(200)
            bonus_bg.fill(GOLD)
            self.screen.blit(bonus_bg, (20, 95))
            
            bonus_text = self.font_medium.render(f"🔥 STREAK: {self.consecutive_correct}!", True, RED)
            self.screen.blit(bonus_text, (25, 100))
        
        # Instructions - better positioned and more readable
        if not self.show_question:
            instruction_bg = pygame.Surface((SCREEN_WIDTH - 20, 40))
            instruction_bg.set_alpha(150)
            instruction_bg.fill(WHITE)
            self.screen.blit(instruction_bg, (10, SCREEN_HEIGHT - 50))
            
            instruction_text = self.font_medium.render("Use arrow keys to move and jump. Touch doors to answer math questions!", True, BLACK)
            self.screen.blit(instruction_text, (20, SCREEN_HEIGHT - 40))
            
            # Controls hint
            controls_text = self.font_small.render("Press L for Leaderboard", True, PURPLE)
            self.screen.blit(controls_text, (20, SCREEN_HEIGHT - 20))
    
    def draw_start_screen(self):
        # Gradient background
        self.draw_background()
        
        # Welcome overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill(PURPLE)
        self.screen.blit(overlay, (0, 0))
        
        # Welcome box
        box_width = 600
        box_height = 400
        box_x = SCREEN_WIDTH // 2 - box_width // 2
        box_y = SCREEN_HEIGHT // 2 - box_height // 2
        
        pygame.draw.rect(self.screen, WHITE, (box_x, box_y, box_width, box_height))
        pygame.draw.rect(self.screen, GOLD, (box_x, box_y, box_width, box_height), 8)
        
        # Title
        title_font = pygame.font.Font(None, 64)
        title_text = title_font.render("🎮 Math Quiz Adventure 🎮", True, PURPLE)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, box_y + 60))
        self.screen.blit(title_text, title_rect)
        
        # Subtitle
        subtitle_text = self.font_medium.render("Enhanced Edition with 5 Levels!", True, GOLD)
        subtitle_rect = subtitle_text.get_rect(center=(SCREEN_WIDTH // 2, box_y + 100))
        self.screen.blit(subtitle_text, subtitle_rect)
        
        # Name input prompt
        prompt_text = self.font_large.render("Enter your name:", True, BLACK)
        prompt_rect = prompt_text.get_rect(center=(SCREEN_WIDTH // 2, box_y + 160))
        self.screen.blit(prompt_text, prompt_rect)
        
        # Name input field
        input_rect = pygame.Rect(box_x + 100, box_y + 200, box_width - 200, 40)
        pygame.draw.rect(self.screen, LIGHT_BLUE, input_rect)
        pygame.draw.rect(self.screen, BLACK, input_rect, 3)
        
        name_text = self.font_large.render(self.player_name, True, BLACK)
        self.screen.blit(name_text, (input_rect.x + 10, input_rect.y + 8))
        
        # Instructions
        instruction1 = self.font_medium.render("• Use arrow keys to move and jump", True, BLACK)
        self.screen.blit(instruction1, (box_x + 50, box_y + 270))
        
        instruction2 = self.font_medium.render("• Touch doors to answer math questions", True, BLACK)
        self.screen.blit(instruction2, (box_x + 50, box_y + 300))
        
        instruction3 = self.font_medium.render("• Complete 5 questions per level", True, BLACK)
        self.screen.blit(instruction3, (box_x + 50, box_y + 330))
        
        # Start instruction
        start_text = self.font_medium.render("Press ENTER to start your adventure!", True, GREEN)
        start_rect = start_text.get_rect(center=(SCREEN_WIDTH // 2, box_y + 370))
        self.screen.blit(start_text, start_rect)
    
    def draw_level_transition(self):
        # Background with current level layout
        self.draw_background()
        self.draw_ground()
        self.draw_platforms()
        
        for door in self.doors:
            door.draw(self.screen)
        
        # Transition overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        # Transition box
        box_width = 500
        box_height = 250
        box_x = SCREEN_WIDTH // 2 - box_width // 2
        box_y = SCREEN_HEIGHT // 2 - box_height // 2
        
        pygame.draw.rect(self.screen, WHITE, (box_x, box_y, box_width, box_height))
        pygame.draw.rect(self.screen, PURPLE, (box_x, box_y, box_width, box_height), 6)
        
        # Level announcement
        level_font = pygame.font.Font(None, 72)
        level_text = level_font.render(f"🚀 LEVEL {self.current_level} 🚀", True, PURPLE)
        level_rect = level_text.get_rect(center=(SCREEN_WIDTH // 2, box_y + 60))
        self.screen.blit(level_text, level_rect)
        
        # Level description
        level_descriptions = {
            1: "Simple Addition & Subtraction",
            2: "Medium Problems",
            3: "Larger Numbers + Multiplication",
            4: "Advanced Multiplication",
            5: "Ultimate Math Challenge!"
        }
        
        desc_text = self.font_large.render(level_descriptions[self.current_level], True, BLACK)
        desc_rect = desc_text.get_rect(center=(SCREEN_WIDTH // 2, box_y + 120))
        self.screen.blit(desc_text, desc_rect)
        
        # Player info
        player_text = self.font_medium.render(f"Player: {self.player_name}", True, GOLD)
        player_rect = player_text.get_rect(center=(SCREEN_WIDTH // 2, box_y + 160))
        self.screen.blit(player_text, player_rect)
        
        score_text = self.font_medium.render(f"Current Score: {self.score}", True, GREEN)
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, box_y + 190))
        self.screen.blit(score_text, score_rect)
        
        # Countdown or ready message
        if self.transition_timer > 60:
            ready_text = self.font_medium.render("Get Ready!", True, RED)
        else:
            ready_text = self.font_medium.render("GO!", True, GREEN)
        ready_rect = ready_text.get_rect(center=(SCREEN_WIDTH // 2, box_y + 220))
        self.screen.blit(ready_text, ready_rect)
    
    def draw_level_complete(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(230)
        overlay.fill(PURPLE)
        self.screen.blit(overlay, (0, 0))
        
        # Celebration box
        box_width = 600
        box_height = 300
        box_x = SCREEN_WIDTH // 2 - box_width // 2
        box_y = SCREEN_HEIGHT // 2 - box_height // 2
        
        pygame.draw.rect(self.screen, WHITE, (box_x, box_y, box_width, box_height))
        pygame.draw.rect(self.screen, GOLD, (box_x, box_y, box_width, box_height), 8)
        
        # Celebration header - show the level that was just completed
        celebration_font = pygame.font.Font(None, 72)
        complete_text = celebration_font.render(f"🎉 Level {self.current_level} Complete! 🎉", True, PURPLE)
        complete_rect = complete_text.get_rect(center=(SCREEN_WIDTH // 2, box_y + 60))
        self.screen.blit(complete_text, complete_rect)
        
        # Score breakdown
        score_font = pygame.font.Font(None, 48)
        score_text = score_font.render(f"Level Bonus: +{LEVEL_COMPLETION_BONUS} points", True, GOLD)
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, box_y + 120))
        self.screen.blit(score_text, score_rect)
        
        total_font = pygame.font.Font(None, 56)
        total_text = total_font.render(f"Total Score: {self.score}", True, GREEN)
        total_rect = total_text.get_rect(center=(SCREEN_WIDTH // 2, box_y + 170))
        self.screen.blit(total_text, total_rect)
        
        # Continue instruction
        continue_font = pygame.font.Font(None, 40)
        if self.current_level < 5:
            continue_text = continue_font.render(f"Press SPACE to continue to Level {self.current_level + 1}", True, BLACK)
        else:
            continue_text = continue_font.render("Press SPACE to finish the game!", True, BLACK)
        continue_rect = continue_text.get_rect(center=(SCREEN_WIDTH // 2, box_y + 230))
        self.screen.blit(continue_text, continue_rect)
    
    def draw_name_input(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        # Input box
        box_width = 400
        box_height = 200
        box_x = SCREEN_WIDTH // 2 - box_width // 2
        box_y = SCREEN_HEIGHT // 2 - box_height // 2
        
        pygame.draw.rect(self.screen, WHITE, (box_x, box_y, box_width, box_height))
        pygame.draw.rect(self.screen, BLACK, (box_x, box_y, box_width, box_height), 5)
        
        # Congratulations text
        congrats_text = self.font_medium.render("Congratulations!", True, BLACK)
        congrats_rect = congrats_text.get_rect(center=(SCREEN_WIDTH // 2, box_y + 40))
        self.screen.blit(congrats_text, congrats_rect)
        
        score_text = self.font_medium.render(f"Final Score: {self.score}", True, PURPLE)
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, box_y + 70))
        self.screen.blit(score_text, score_rect)
        
        # Name input
        name_prompt = self.font_small.render("Enter your name for the leaderboard:", True, BLACK)
        name_rect = name_prompt.get_rect(center=(SCREEN_WIDTH // 2, box_y + 100))
        self.screen.blit(name_prompt, name_rect)
        
        # Name input field
        input_rect = pygame.Rect(box_x + 50, box_y + 120, box_width - 100, 30)
        pygame.draw.rect(self.screen, LIGHT_BLUE, input_rect)
        pygame.draw.rect(self.screen, BLACK, input_rect, 2)
        
        name_text = self.font_medium.render(self.player_name, True, BLACK)
        self.screen.blit(name_text, (input_rect.x + 5, input_rect.y + 5))
        
        # Instructions
        enter_text = self.font_small.render("Press ENTER to submit", True, BLACK)
        enter_rect = enter_text.get_rect(center=(SCREEN_WIDTH // 2, box_y + 170))
        self.screen.blit(enter_text, enter_rect)
    
    def draw_leaderboard(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        # Leaderboard box
        box_width = 600
        box_height = 500
        box_x = SCREEN_WIDTH // 2 - box_width // 2
        box_y = SCREEN_HEIGHT // 2 - box_height // 2
        
        pygame.draw.rect(self.screen, WHITE, (box_x, box_y, box_width, box_height))
        pygame.draw.rect(self.screen, BLACK, (box_x, box_y, box_width, box_height), 5)
        
        # Title
        title_text = self.font_large.render("🏆 LEADERBOARD 🏆", True, GOLD)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, box_y + 40))
        self.screen.blit(title_text, title_rect)
        
        # Headers
        rank_text = self.font_medium.render("Rank", True, BLACK)
        self.screen.blit(rank_text, (box_x + 50, box_y + 80))
        
        name_text = self.font_medium.render("Name", True, BLACK)
        self.screen.blit(name_text, (box_x + 150, box_y + 80))
        
        score_text = self.font_medium.render("Score", True, BLACK)
        self.screen.blit(score_text, (box_x + 300, box_y + 80))
        
        level_text = self.font_medium.render("Level", True, BLACK)
        self.screen.blit(level_text, (box_x + 400, box_y + 80))
        
        date_text = self.font_medium.render("Date", True, BLACK)
        self.screen.blit(date_text, (box_x + 480, box_y + 80))
        
        # Scores
        scores = self.leaderboard.get_top_scores()
        for i, entry in enumerate(scores[:8]):  # Show top 8
            y_pos = box_y + 120 + i * 35
            color = GOLD if i == 0 else BLACK
            
            rank_text = self.font_small.render(f"{i+1}.", True, color)
            self.screen.blit(rank_text, (box_x + 50, y_pos))
            
            name_text = self.font_small.render(entry['name'][:12], True, color)
            self.screen.blit(name_text, (box_x + 150, y_pos))
            
            score_text = self.font_small.render(str(entry['score']), True, color)
            self.screen.blit(score_text, (box_x + 300, y_pos))
            
            level_text = self.font_small.render(str(entry['level']), True, color)
            self.screen.blit(level_text, (box_x + 400, y_pos))
            
            date_text = self.font_small.render(entry['date'][-5:], True, color)  # Show time only
            self.screen.blit(date_text, (box_x + 480, y_pos))
        
        # Instructions
        instruction_text = self.font_small.render("Press R to play again, L to toggle leaderboard, or ESC to quit", True, BLACK)
        instruction_rect = instruction_text.get_rect(center=(SCREEN_WIDTH // 2, box_y + box_height - 30))
        self.screen.blit(instruction_text, instruction_rect)
    
    def run(self):
        running = True
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_l and self.game_started:  # Toggle leaderboard
                        self.show_leaderboard = not self.show_leaderboard
                    elif event.key == pygame.K_r and (self.game_won or self.show_leaderboard):
                        self.reset_game()
                        self.show_leaderboard = False
                        self.show_name_input = False
                        self.player_name = ""
                    elif event.key == pygame.K_SPACE:
                        if self.show_question and self.question_result:
                            if self.question_result == "correct":
                                self.show_question = False
                                self.question_result = None
                                
                                # Check if level is completed
                                if self.level_completed:
                                    if self.current_level < 5:
                                        self.advance_level()
                                    else:
                                        self.game_won = True
                                        self.show_name_input = True
                            else:
                                self.question_result = None
                        elif self.level_completed and not self.game_won and not self.show_level_transition:
                            self.advance_level()
                
                # Handle different input screens
                if self.show_name_input_start:
                    self.handle_name_input_start(event)
                elif self.show_name_input:
                    self.handle_name_input(event)
                elif self.show_question and not self.question_result and self.game_started:
                    self.handle_question_input(event)
            
            # Update transition timer
            if self.show_level_transition:
                self.transition_timer -= 1
                if self.transition_timer <= 0:
                    self.show_level_transition = False
            
            # Game logic - only when game is active
            if (self.game_started and not self.show_question and not self.game_won and 
                not self.show_leaderboard and not self.level_completed and not self.show_level_transition):
                self.player.update(self.platforms)
                if self.check_door_collision():
                    pass  # Question will be shown
            
            # Draw everything based on current state
            if self.show_name_input_start:
                self.draw_start_screen()
            elif self.show_level_transition:
                self.draw_level_transition()
            elif self.show_leaderboard:
                self.draw_leaderboard()
            elif self.show_name_input:
                self.draw_name_input()
            else:
                # Draw main game
                self.draw_background()
                self.draw_ground()
                self.draw_platforms()
                
                for door in self.doors:
                    door.draw(self.screen)
                
                if self.game_started and not self.show_question:
                    self.player.draw(self.screen)
                
                if self.game_started:
                    self.draw_ui()
                
                if self.show_question:
                    self.draw_question()
                elif self.level_completed and not self.game_won:
                    self.draw_level_complete()
            
            pygame.display.flip()
            self.clock.tick(FPS)
        
        pygame.quit()

if __name__ == "__main__":
    game = Game()
    game.run()
