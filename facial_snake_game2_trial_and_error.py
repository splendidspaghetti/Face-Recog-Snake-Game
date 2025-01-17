import cv2
import mediapipe as mp
import pygame
import random

# Initialize Mediapipe Face Mesh
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh()

# Initialize Pygame
pygame.init()

WIDTH, HEIGHT = 600, 400
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Face-Controlled Snake Game by Hazel Lee')

# Colors
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLACK = (0, 0, 0)
YELLOW = (255, 255, 102)
BLUE = (50, 153, 213)

# Snake and Food size and speed (FPS)
BLOCK_SIZE = 20
FPS = 8

# Font for text rendering
font = pygame.font.SysFont("bahnschrift", 25)

def show_message(message, color, y_offset=0):
    text = font.render(message, True, color)
    text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + y_offset))
    screen.blit(text, text_rect)
    pygame.display.flip()

# Function to check collision with boundaries or itself
def check_collision(snake_head, snake_body):
    x, y = snake_head
    if x < 0 or x >= WIDTH or y < 0 or y >= HEIGHT:
        return True  # Collided with the wall
    if snake_head in snake_body[1:]:
        return True  # Collided with itself
    return False

# Function to render the snake and food
def draw_game(snake, food, score):
    screen.fill(BLACK)
    for segment in snake:
        pygame.draw.rect(screen, GREEN, (segment[0], segment[1], BLOCK_SIZE, BLOCK_SIZE))
    pygame.draw.rect(screen, RED, (food[0], food[1], BLOCK_SIZE, BLOCK_SIZE))

    # Display the score
    score_text = font.render(f"Score: {score}", True, WHITE)
    screen.blit(score_text, (10, 10))

    pygame.display.flip()

# Function to generate new food location
def generate_food(snake_body):
    while True:
        new_food = (random.randint(0, (WIDTH // BLOCK_SIZE) - 1) * BLOCK_SIZE,
                    random.randint(0, (HEIGHT // BLOCK_SIZE) - 1) * BLOCK_SIZE)
        if new_food not in snake_body:  # Ensure food doesn't appear on the snake
            return new_food

def start_screen():
    screen.fill(BLUE)
    show_message("Welcome to Hazel's Snake Game!", WHITE, -30)
    show_message("Press ENTER to Start", YELLOW, 30)

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                waiting = False

def end_screen(final_score):
    screen.fill(BLUE)
    show_message("Game Over!", RED, -30)
    show_message(f"Final Score: {final_score}", WHITE, 0)
    show_message("Press R to Restart or Q to Quit", YELLOW, 30)

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    return True  # Restart the game
                if event.key == pygame.K_q:
                    return False  # Quit the game

# Main game loop
def game_loop():
    global direction
    snake = [(100, 100)]
    direction = "RIGHT"
    food = (random.randint(0, (WIDTH // BLOCK_SIZE) - 1) * BLOCK_SIZE,
            random.randint(0, (HEIGHT // BLOCK_SIZE) - 1) * BLOCK_SIZE)
    score = 0

    cap = cv2.VideoCapture(0)

    running = True
    while running:
        ret, frame = cap.read()
        if not ret:
            print("Failed to capture frame from camera. Exiting.")
            break

        # Flip frame for mirrored view
        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Process the frame to detect face landmarks
        results = face_mesh.process(rgb_frame)

        # Determine snake direction based on face movement
        if results.multi_face_landmarks:
            for face_landmarks in results.multi_face_landmarks:
                # Get nose tip position
                nose_tip = face_landmarks.landmark[1]  # Nose tip index in Mediapipe is 1
                x = int(nose_tip.x * WIDTH)
                y = int(nose_tip.y * HEIGHT)

                # Determine movement direction based on nose position
                if x < WIDTH // 3 and direction != "RIGHT":
                    direction = "LEFT"
                elif x > 2 * (WIDTH // 4) and direction != "LEFT":
                    direction = "RIGHT"
                elif y < HEIGHT // 2 and direction != "DOWN":
                    direction = "UP"
                elif y > 2 * (HEIGHT // 3) and direction != "UP":
                    direction = "DOWN"

        # Update snake position
        head_x, head_y = snake[0]
        if direction == "UP":
            head_y -= BLOCK_SIZE
        elif direction == "DOWN":
            head_y += BLOCK_SIZE
        elif direction == "LEFT":
            head_x -= BLOCK_SIZE
        elif direction == "RIGHT":
            head_x += BLOCK_SIZE

        new_head = (head_x, head_y)
        snake.insert(0, new_head)

        # Check for collision with food
        if new_head == food:
            score += 1
            food = generate_food(snake)
        else:
            snake.pop()  # Remove tail if no food eaten

        # Check for collisions with wall or itself
        if check_collision(new_head, snake):
            running = False

        # Draw game state
        draw_game(snake, food, score)

        # Limit the game speed
        pygame.time.Clock().tick(FPS)

    cap.release()
    return score

# Run the game
while True:
    start_screen()
    final_score = game_loop()
    if not end_screen(final_score):
        break

pygame.quit()
