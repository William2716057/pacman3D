import pygame
import math
import time
 
#Configuration 
SCREEN_RES = (1600, 800)
TILE_SIZE = 25
FOV = math.pi / 3  # 60 degrees
HALF_FOV = FOV / 2
CASTED_RAYS = 120  # Number of vertical lines
STEP_ANGLE = FOV / CASTED_RAYS
MAX_DEPTH = 800
 
orbs = []


 
#1 is wall, 0 is space
MAP = [
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], 
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 1, 1, 1, 0, 1, 1, 1, 0, 1, 0, 1, 1, 1, 0, 1, 1, 1, 0, 1],
    [1, 0, 1, 1, 1, 0, 1, 1, 1, 0, 1, 0, 1, 1, 1, 0, 1, 1, 1, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 1, 1, 1, 0, 1, 0, 1, 1, 1, 1, 1, 0, 1, 0, 1, 1, 1, 0, 1],
    [1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1],
    [1, 1, 1, 1, 1, 0, 1, 1, 1, 0, 1, 0, 1, 1, 1, 0, 1, 1, 1, 1, 1],
    [1, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 1],
    [1, 1, 1, 1, 1, 0, 1, 0, 1, 1, 0, 1, 1, 0, 1, 0, 1, 1, 1, 1, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1], #tunnel row
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

def get_orb_animation(orb_index):
    t = pygame.time.get_ticks() / 1000.0  # seconds since start
    phase = orb_index * 0.3  # stagger so orbs don't all pulse in lockstep
    bob_offset = math.sin(t * 2 + phase) * 4      # vertical float, +/- 4px
    pulse_scale = 1.0 + math.sin(t * 4 + phase) * 0.15  # size breathing
    return bob_offset, pulse_scale

for row in range(len(MAP)):
    for col in range(len(MAP[0])):
        if MAP[row][col] == 0:  # only place on open floor
            orb_x = (col + 0.5) * TILE_SIZE
            orb_y = (row + 0.5) * TILE_SIZE
            orbs.append({'x': orb_x, 'y': orb_y, 'active': True})
            
def render_orbs():
    for i, orb in enumerate(orbs):
        if not orb['active']:
            continue

        dx = orb['x'] - player_x
        dy = orb['y'] - player_y
        dist = math.hypot(dx, dy)

        angle_to_orb = math.atan2(dy, dx) - player_angle
        # normalize angle to [-pi, pi]
        angle_to_orb = (angle_to_orb + math.pi) % (2 * math.pi) - math.pi

        if abs(angle_to_orb) < HALF_FOV and dist > 1:
            ray_index = int((angle_to_orb + HALF_FOV) / STEP_ANGLE)
            if 0 <= ray_index < CASTED_RAYS:
                corrected_dist = dist * math.cos(angle_to_orb)
                screen_x = ray_index * (SCREEN_RES[0] / CASTED_RAYS)

                bob_offset, pulse_scale = get_orb_animation(i)
                base_size = 21000 / (corrected_dist + 0.0001) * 0.15
                size = base_size * pulse_scale

                screen_y = SCREEN_RES[1] / 2 + bob_offset

                pygame.draw.circle(
                    screen,
                    (255, 220, 100),
                    (int(screen_x), int(screen_y)),
                    max(1, int(size / 2))
                )
 
# Open the border on the tunnel row so the player can walk out either side
MAP[10][0] = 0
MAP[10][20] = 0
 
TUNNEL_ROWS = [10]
 
#initialise game
pygame.init()
screen = pygame.display.set_mode(SCREEN_RES)
clock = pygame.time.Clock()
 
#Position
player_x = (len(MAP[0]) / 2) * TILE_SIZE
player_y = (len(MAP) / 2) * TILE_SIZE
player_angle = math.pi
 
 
def is_wall(x, y):
    col = int(x / TILE_SIZE)
    row = int(y / TILE_SIZE)
 
    if row < 0 or row >= len(MAP) or col < 0 or col >= len(MAP[0]):
        return True  # outside map = treat as wall
 
    return MAP[row][col] == 1
 
#for wraparound to reappear at other side of map
def try_wrap(x, y):
    
    row = int(y / TILE_SIZE)
    col = int(x / TILE_SIZE)
    max_col = len(MAP[0])
 
    if row in TUNNEL_ROWS:
        if col <= 0:
            x = (max_col - 2) * TILE_SIZE + (TILE_SIZE / 2)
        elif col >= max_col - 1:
            x = 1 * TILE_SIZE + (TILE_SIZE / 2)
 
    return x, y
 
 
#raycasting functions
def cast_rays():
    start_angle = player_angle - HALF_FOV
    max_col = len(MAP[0])
 
    for ray in range(CASTED_RAYS):
        for depth in range(1, MAX_DEPTH):
            target_x = player_x + math.cos(start_angle) * depth
            target_y = player_y + math.sin(start_angle) * depth
 
            col = int(target_x / TILE_SIZE)
            row = int(target_y / TILE_SIZE)
 
            # Wrap horizontally if we're passing through a tunnel row
            if 0 <= row < len(MAP) and row in TUNNEL_ROWS:
                if col < 0:
                    col = max_col + col
                elif col >= max_col:
                    col = col - max_col
 
            if row < 0 or row >= len(MAP) or col < 0 or col >= max_col:
                break
 
            if MAP[row][col] == 1:
                # Fix Fisheye effect
                depth *= math.cos(player_angle - start_angle)
 
                # Calculate wall height
                wall_height = 21000 / (depth + 0.0001)
 
                # Draw vertical slice
                color = 240 / (1 + depth * depth * 0.0001)  # Simple shading
                pygame.draw.rect(screen, (20, 20, color), (
                    ray * (SCREEN_RES[0] / CASTED_RAYS),
                    (SCREEN_RES[1] / 2) - wall_height / 2,
                    (SCREEN_RES[0] / CASTED_RAYS) + 1,
                    wall_height
                ))
                break
        start_angle += STEP_ANGLE

#render_orbs()
 
#Main Loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
 
    # Movement
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]: player_angle -= 0.05  # turn left
    if keys[pygame.K_RIGHT]: player_angle += 0.05  # turn right
 
    new_x = player_x
    new_y = player_y
 
    if keys[pygame.K_UP]:  # move forward
        new_x += math.cos(player_angle) * 3
        new_y += math.sin(player_angle) * 3
    if keys[pygame.K_DOWN]:  # move back
        new_x -= math.cos(player_angle) * 3
        new_y -= math.sin(player_angle) * 3
 
    # move X
    if not is_wall(new_x, player_y):
        player_x = new_x
 
    # move Y
    if not is_wall(player_x, new_y):
        player_y = new_y
 
    # tunnel teleport check (after movement resolved)
    player_x, player_y = try_wrap(player_x, player_y)
 
    # Rendering
    screen.fill((50, 50, 50))  # Ceiling
    pygame.draw.rect(screen, (20, 20, 20), (0, SCREEN_RES[1]/2, SCREEN_RES[0], SCREEN_RES[1]/2))  # Floor
    cast_rays()
    render_orbs()
 
    pygame.display.flip()
    clock.tick(60)
 
pygame.quit()