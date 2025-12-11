import pygame
import os

# --- Config / constants ---
VIRTUAL_SIZE = (1080, 720)
FPS = 60

# physics
GRAVITY = 0.1
MOVE_SPEED = 5
JUMP_SPEED = -6

# camera
DEADZONE_WIDTH = 0.2
DEADZONE_HEIGHT = 0.2
CAMERA_LERP = 0.15

# --- files ---
AssetDir = "assets"
Background1 = os.path.join(AssetDir, "Background.png")
PlayerSprite = os.path.join(AssetDir, "nisa-nur-celik-astronaut.gif")
TILE_DIR = os.path.join(AssetDir, "tiles")

level_map = [
    "0000000000000000000000000000000",
    "0000000000000000000000000000000",
    "0000001100000000000000000000000",
    "0000011111000000000000000000000",
    "1111111111111111111111111111111",
]

def load_tile_images(tile_dir, tile_size):
    tiles = {}
    for fname in os.listdir(tile_dir):
        name, _ = os.path.splitext(fname)
        if name.isdigit():
            img = pygame.image.load(os.path.join(tile_dir, fname)).convert_alpha()
            img = pygame.transform.smoothscale(img, (tile_size, tile_size))
            tiles[name] = img
    return tiles

def create_level_tiles_and_colliders(level_data, tile_images, tile_size):
    tiles = []
    colliders = []
    rows = len(level_data)
    y_offset = VIRTUAL_SIZE[1] - rows * tile_size
    for r, row in enumerate(level_data):
        for c, cell in enumerate(row):
            if cell != "0" and cell in tile_images:
                x = c * tile_size
                y = y_offset + r * tile_size
                tiles.append((tile_images[cell], (x, y)))
                colliders.append(pygame.Rect(x, y, tile_size, tile_size))
    return tiles, colliders

def load_image(name, size=None, position=(0, 0)):
    try:
        img = pygame.image.load(name).convert_alpha()
        if size:
            img = pygame.transform.smoothscale(img, size)
        rect = img.get_rect(topleft=position)
        return img, rect
    except Exception as e:
        print(f"Failed to load '{name}': {e}")
        return None, None

def compute_scale_and_offset(screen_size):
    """Compute scale factor and letterbox offset for preserving aspect."""
    sw, sh = screen_size
    vw, vh = VIRTUAL_SIZE
    scale = min(sw / vw, sh / vh)
    scaled_w = int(vw * scale)
    scaled_h = int(vh * scale)
    offset_x = (sw - scaled_w) // 2
    offset_y = (sh - scaled_h) // 2
    return scale, offset_x, offset_y

def main():
    pygame.init()
    fullscreen = False
    screen = pygame.display.set_mode(VIRTUAL_SIZE)
    world_surface = pygame.Surface(VIRTUAL_SIZE)
    clock = pygame.time.Clock()

    rows = len(level_map)
    tile_size = VIRTUAL_SIZE[1] // rows
    player_size = (tile_size, tile_size)

    bg_raw = None
    if os.path.exists(Background1):
        bg_raw = pygame.image.load(Background1).convert_alpha()
        bg_raw = pygame.transform.smoothscale(bg_raw, VIRTUAL_SIZE)

    tile_images = load_tile_images(TILE_DIR, tile_size)
    level_tiles, level_colliders = create_level_tiles_and_colliders(level_map, tile_images, tile_size)

    player_img, player_rect = load_image(PlayerSprite, size=player_size, position=(100, 100))
    if player_img:
        player_img.set_colorkey((0, 0, 0))

    HITBOX_OFFSET_X = 35
    HITBOX_OFFSET_Y = 42
    HITBOX_WIDTH_REDUCTION = 70
    HITBOX_HEIGHT_REDUCTION = 42

    player_hitbox = pygame.Rect(
        player_rect.x + HITBOX_OFFSET_X,
        player_rect.y + HITBOX_OFFSET_Y,
        player_size[0] - HITBOX_WIDTH_REDUCTION,
        player_size[1] - HITBOX_HEIGHT_REDUCTION
    )

    show_hitboxes = False
    vel_x = 0
    vel_y = 0
    on_ground = False

    cam_x = 0
    cam_y = 0
    dzw = VIRTUAL_SIZE[0] * DEADZONE_WIDTH
    dzh = VIRTUAL_SIZE[1] * DEADZONE_HEIGHT

    world_width = len(level_map[0]) * tile_size
    world_height = len(level_map) * tile_size

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F1:
                    show_hitboxes = not show_hitboxes
                if event.key == pygame.K_F11:
                    fullscreen = not fullscreen
                    if fullscreen:
                        screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
                    else:
                        screen = pygame.display.set_mode(VIRTUAL_SIZE)

        # input
        keys = pygame.key.get_pressed()
        vel_x = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            vel_x = -MOVE_SPEED
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            vel_x = MOVE_SPEED
        if (keys[pygame.K_SPACE] or keys[pygame.K_UP] or keys[pygame.K_w]) and on_ground:
            vel_y = JUMP_SPEED
            on_ground = False

        # physics
        player_hitbox.x += vel_x
        for col in level_colliders:
            if player_hitbox.colliderect(col):
                if vel_x > 0:
                    player_hitbox.right = col.left
                elif vel_x < 0:
                    player_hitbox.left = col.right

        vel_y += GRAVITY
        player_hitbox.y += vel_y
        on_ground = False
        for col in level_colliders:
            if player_hitbox.colliderect(col):
                if vel_y > 0:
                    player_hitbox.bottom = col.top
                    vel_y = 0
                    on_ground = True
                elif vel_y < 0:
                    player_hitbox.top = col.bottom
                    vel_y = 0

        player_rect.centerx = player_hitbox.centerx - HITBOX_OFFSET_X + (HITBOX_WIDTH_REDUCTION // 2)
        player_rect.centery = player_hitbox.centery - HITBOX_OFFSET_Y + (HITBOX_HEIGHT_REDUCTION // 2)

        # camera (virtual coords)
        target_x = player_rect.centerx - VIRTUAL_SIZE[0] / 2
        target_y = player_rect.centery - VIRTUAL_SIZE[1] / 2

        if player_rect.centerx - cam_x < dzw:
            target_x = player_rect.centerx - dzw
        elif player_rect.centerx - cam_x > VIRTUAL_SIZE[0] - dzw:
            target_x = player_rect.centerx - (VIRTUAL_SIZE[0] - dzw)

        if player_rect.centery - cam_y < dzh:
            target_y = player_rect.centery - dzh
        elif player_rect.centery - cam_y > VIRTUAL_SIZE[1] - dzh:
            target_y = player_rect.centery - (VIRTUAL_SIZE[1] - dzh)

        cam_x += (target_x - cam_x) * CAMERA_LERP
        cam_y += (target_y - cam_y) * CAMERA_LERP

        cam_x = max(0, min(cam_x, world_width - VIRTUAL_SIZE[0]))
        cam_y = max(0, min(cam_y, world_height - VIRTUAL_SIZE[1]))

        # draw to virtual surface
        if bg_raw:
            world_surface.blit(bg_raw, (0, 0))
        else:
            world_surface.fill((100, 150, 200))

        for img, (x, y) in level_tiles:
            world_surface.blit(img, (x - cam_x, y - cam_y))

        world_surface.blit(player_img, (player_rect.x - cam_x, player_rect.y - cam_y))

        if show_hitboxes:
            dbg_hitbox = pygame.Rect(
                player_hitbox.x - cam_x,
                player_hitbox.y - cam_y,
                player_hitbox.width,
                player_hitbox.height
            )
            pygame.draw.rect(world_surface, (0, 255, 0), dbg_hitbox, 2)
            for col in level_colliders:
                pygame.draw.rect(world_surface, (255, 0, 0),
                                 pygame.Rect(col.x - cam_x, col.y - cam_y, col.width, col.height), 2)

        # scale virtual to actual screen
        sw, sh = screen.get_size()
        scale, ox, oy = compute_scale_and_offset((sw, sh))
        scaled_surface = pygame.transform.smoothscale(world_surface,
                                                     (int(VIRTUAL_SIZE[0] * scale),
                                                      int(VIRTUAL_SIZE[1] * scale)))
        screen.fill((0, 0, 0))
        screen.blit(scaled_surface, (ox, oy))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()
