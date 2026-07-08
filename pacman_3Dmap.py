import pygame
import math

#Configuration 
SCREEN_RES = (1600, 800)
TILE_SIZE = 25
FOV = math.pi / 3  # 60 degrees
HALF_FOV = FOV / 2
CASTED_RAYS = 120  # Number of vertical lines
STEP_ANGLE = FOV / CASTED_RAYS
MAX_DEPTH = 800

#1 is wall, 0 is space
MAP = [
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1], #can remove this line
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 1, 1, 1, 0, 1, 1, 1, 0, 1, 0, 1, 1, 1, 0, 1, 1, 1, 0, 1],
    [1, 0, 1, 1, 1, 0, 1, 1, 1, 0, 1, 0, 1, 1, 1, 0, 1, 1, 1, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 1, 1, 1, 0, 1, 0, 1, 1, 1, 1, 1, 0, 1, 0, 1, 1, 1, 0, 1],
    [1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1],
    [1, 1, 1, 1, 1, 0, 1, 1, 1, 0, 1, 0, 1, 1, 1, 0, 1, 1, 1, 1, 1],
    [1, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 1],
    [1, 1, 1, 1, 1, 0, 1, 0, 1, 1, 0, 1, 1, 0, 1, 0, 1, 1, 1, 1, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1], #teleport here
    [1, 1, 1, 1, 1, 0, 1, 0, 1, 1, 1, 1, 1, 0, 1, 0, 1, 1, 1, 1, 1],
    [1, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 1],
    [1, 1, 1, 1, 1, 0, 1, 0, 1, 1, 1, 1, 1, 0, 1, 0, 1, 1, 1, 1, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 1, 1, 1, 0, 1, 1, 1, 0, 1, 0, 1, 1, 1, 0, 1, 1, 1, 0, 1],
    [1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1],
    [1, 1, 1, 0, 1, 0, 1, 0, 1, 1, 1, 1, 1, 0, 1, 0, 1, 0, 1, 1, 1],
    [1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1],
    [1, 0, 1, 1, 1, 1, 1, 1, 1, 0, 1, 0, 1, 1, 1, 1, 1, 1, 1, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
]

#initialise game
pygame.init()
screen = pygame.display.set_mode(SCREEN_RES)
clock = pygame.time.Clock()

#Position
player_x = (len(MAP[0]) / 2) * TILE_SIZE
player_y = (len(MAP) / 2) * TILE_SIZE
player_angle = math.pi

#raycasting functions
def cast_rays():
    start_angle = player_angle - HALF_FOV
    
    for ray in range(CASTED_RAYS):
        for depth in range(1, MAX_DEPTH):
            target_x = player_x + math.cos(start_angle) * depth
            target_y = player_y + math.sin(start_angle) * depth
            
            # Convert coordinate to map index
            col = int(target_x / TILE_SIZE)
            row = int(target_y / TILE_SIZE)
            
            #prevents crash
            if row < 0 or row >= len(MAP) or col < 0 or col >= len(MAP[0]):
                break
            
            if MAP[row][col] == 1:
                # Fix Fisheye effect
                depth *= math.cos(player_angle - start_angle)
                
                # Calculate wall height
                wall_height = 21000 / (depth + 0.0001)
                
                # Draw vertical slice
                color = 240 / (1 + depth * depth * 0.0001) # Simple shading to make far away walls look darker
                pygame.draw.rect(screen, (20, 20, color), ( #edit colours here
                    ray * (SCREEN_RES[0] / CASTED_RAYS),
                    (SCREEN_RES[1] / 2) - wall_height / 2,
                    (SCREEN_RES[0] / CASTED_RAYS) + 1,
                    wall_height
                ))
                break
        start_angle += STEP_ANGLE

#Main Loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            

    
    # Movement
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]: player_angle -= 0.05 #turn left
    if keys[pygame.K_RIGHT]: player_angle += 0.05 #turn right
    
    new_x = player_x
    new_y = player_y
    
    if keys[pygame.K_UP]: #move forward
        new_x += math.cos(player_angle) * 3
        new_y += math.sin(player_angle) * 3
    if keys[pygame.K_DOWN]: #move back
        new_x -= math.cos(player_angle) * 3
        new_y -= math.sin(player_angle) * 3
        
    #collision check 
    buffer = 10 #if keys[pygame.K_w] else -10
    check_x = new_x + math.cos(player_angle) * buffer
    check_y = new_y + math.sin(player_angle) * buffer
    
    #update pos only if 0
    def is_wall(x, y):
        col = int(x / TILE_SIZE)
        row = int(y / TILE_SIZE)

        if row < 0 or row >= len(MAP) or col < 0 or col >= len(MAP[0]):
            return True  # outside map = treat as wall

        return MAP[row][col] == 1
    
    if not is_wall(new_x, player_y):
        player_x = new_x

# move Y
    if not is_wall(player_x, new_y):
        player_y = new_y

    # Rendering
    screen.fill((50, 50, 50)) # Ceiling
    pygame.draw.rect(screen, (20, 20, 20), (0, SCREEN_RES[1]/2, SCREEN_RES[0], SCREEN_RES[1]/2)) # Floor
    cast_rays()
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()