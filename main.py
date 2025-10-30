
import sys
import random
import time
from pathlib import Path
import pygame
from utils import (
    draw_line,
    draw_rect,
    draw_circle,
    draw_polygon,
    draw_ellipse,
    random_color,
    save_screenshot,
)

# --- Constants ---
WIDTH, HEIGHT = 900, 650
FPS = 60
BG_COLOR = (30, 30, 40)

# --- Initialize Pygame ---
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pygame — Drawing Shapes (Enhanced)")
clock = pygame.time.Clock()

# --- State ---
moving_circle = {
    "pos": [100.0, 100.0],
    "radius": 30,
    "color": (200, 80, 80, 255),  # RGBA
    "vel": [3.5, 2.7],
}

moving_ellipse = {
    "rect": pygame.Rect(300, 300, 140, 80),
    "vel": [2.1, -1.6],
    "color": (120, 180, 240, 200),
}

# A list to keep user-created circles (from mouse clicks)
circles = []
polygons = []

# Interactive polygon creation
is_creating_polygon = False
current_polygon = []  # list of (x,y)

# Color picker state (simple RGB sliders)
color_picker = {
    'rect': pygame.Rect(10, HEIGHT - 130, 260, 120),
    'r': 120,
    'g': 200,
    'b': 150,
    'active': False,  # whether user is dragging a slider
    'selected': False,
}

# Alpha toggle
use_alpha = True

# Predefined polygon (static)
polygon_points = [(400, 150), (460, 190), (440, 260), (360, 260), (340, 190)]

# Running flag
running = True

# --- Helper functions for color picker ---

def draw_color_picker(surface, picker):
    """Draw a simple RGB slider box. User can click/drag inside each slider to set R/G/B."""
    x, y = picker['rect'].topleft
    w, h = picker['rect'].size
    # Background box
    box = pygame.Surface((w, h))
    box.fill((50, 50, 60))
    surface.blit(box, (x, y))

    font = pygame.font.SysFont(None, 18)
    labels = ['R', 'G', 'B']
    for i, comp in enumerate(['r','g','b']):
        ly = y + 8 + i*36
        # Slider track
        track_rect = pygame.Rect(x+28, ly, w-40, 16)
        pygame.draw.rect(surface, (100,100,100), track_rect)
        # Filled portion
        val = picker[comp]
        fill_w = int((val/255.0) * track_rect.width)
        pygame.draw.rect(surface, (200,200,200), (track_rect.x, track_rect.y, fill_w, track_rect.height))
        # Thumb
        thumb_x = track_rect.x + fill_w
        pygame.draw.circle(surface, (230,230,230), (thumb_x, track_rect.y + track_rect.height//2), 8)
        # Label and numeric
        txt = font.render(f"{labels[i]}: {val}", True, (240,240,240))
        surface.blit(txt, (x+6, ly-2))

    # Current color preview
    preview = pygame.Surface((w-16, 26), pygame.SRCALPHA)
    preview.fill((picker['r'], picker['g'], picker['b'], 200))
    surface.blit(preview, (x+8, y + h - 34))


def color_picker_handle_event(event, picker):
    if event.type == pygame.MOUSEBUTTONDOWN:
        if picker['rect'].collidepoint(event.pos):
            picker['selected'] = True
            update_color_picker_with_pos(event.pos, picker)
    elif event.type == pygame.MOUSEBUTTONUP:
        picker['selected'] = False
    elif event.type == pygame.MOUSEMOTION:
        if picker['selected']:
            update_color_picker_with_pos(event.pos, picker)


def update_color_picker_with_pos(pos, picker):
    x, y = picker['rect'].topleft
    w, h = picker['rect'].size
    px, py = pos
    # Determine which slider row
    rel_y = py - y
    if 0 <= rel_y <= h:
        row = rel_y // 36
        if 0 <= row <= 2:
            track_rect = pygame.Rect(x+28, y + 8 + row*36, w-40, 16)
            val = int(((px - track_rect.x) / track_rect.width) * 255)
            val = max(0, min(255, val))
            if row == 0:
                picker['r'] = val
            elif row == 1:
                picker['g'] = val
            elif row == 2:
                picker['b'] = val


def get_picker_color(picker):
    return (picker['r'], picker['g'], picker['b'], 200 if use_alpha else 255)

# --- Drawing all shapes ---

def draw_shapes(surface):
    """Draw all required shapes on the surface, using alpha where appropriate."""
    # Line (thick)
    draw_line(surface, (50, 40), (WIDTH-50, 40), color=(255, 220, 60), width=6)

    # Filled rect and border-only rect (use alpha)
    # For alpha we draw onto a temporary surface
    if use_alpha:
        temp = pygame.Surface((200,120), pygame.SRCALPHA)
        draw_rect(temp, pygame.Rect(0,0,140,90), color=(80,180,220,180), width=0)
        surface.blit(temp, (50, 350))
        # border rect without alpha
        draw_rect(surface, pygame.Rect(220, 350, 140, 90), color=(220, 180, 80), width=4)
    else:
        draw_rect(surface, pygame.Rect(50,350,140,90), color=(80,180,220), width=0)
        draw_rect(surface, pygame.Rect(220,350,140,90), color=(220,180,80), width=4)

    # Filled circle + circle border
    circle_center = (WIDTH-150, 120)
    if use_alpha:
        temp = pygame.Surface((140,140), pygame.SRCALPHA)
        draw_circle(temp, (70,70), 40, color=(120,200,120,160), width=0)
        draw_circle(temp, (70,70), 60, color=(120,200,120,220), width=4)
        surface.blit(temp, (circle_center[0]-70, circle_center[1]-70))
    else:
        draw_circle(surface, circle_center, 40, color=(120,200,120), width=0)
        draw_circle(surface, circle_center, 60, color=(120,200,120), width=4)

    # Polygon (>=5 vertices)
    draw_polygon(surface, polygon_points, color=(180,120,220), width=0)

    # Ellipse (animated)
    if use_alpha:
        temp = pygame.Surface((moving_ellipse['rect'].width, moving_ellipse['rect'].height), pygame.SRCALPHA)
        draw_ellipse(temp, pygame.Rect(0,0,moving_ellipse['rect'].width, moving_ellipse['rect'].height), color=moving_ellipse['color'], width=0)
        surface.blit(temp, moving_ellipse['rect'].topleft)
    else:
        draw_ellipse(surface, moving_ellipse['rect'], color=moving_ellipse['color'][:3], width=0)

    # Draw moving circle (uses alpha)
    mc_pos = (int(moving_circle['pos'][0]), int(moving_circle['pos'][1]))
    if use_alpha:
        temp = pygame.Surface((moving_circle['radius']*2+4, moving_circle['radius']*2+4), pygame.SRCALPHA)
        draw_circle(temp, (moving_circle['radius']+2, moving_circle['radius']+2), moving_circle['radius'], color=moving_circle['color'], width=0)
        surface.blit(temp, (mc_pos[0]-moving_circle['radius']-2, mc_pos[1]-moving_circle['radius']-2))
    else:
        draw_circle(surface, mc_pos, moving_circle['radius'], color=moving_circle['color'][:3], width=0)

    # Draw user circles
    for c in circles:
        if use_alpha:
            temp = pygame.Surface((c['radius']*2+2, c['radius']*2+2), pygame.SRCALPHA)
            draw_circle(temp, (c['radius']+1, c['radius']+1), c['radius'], color=c['color'], width=0)
            surface.blit(temp, (int(c['pos'][0]) - c['radius'] -1, int(c['pos'][1]) - c['radius'] -1))
        else:
            draw_circle(surface, (int(c['pos'][0]), int(c['pos'][1])), c['radius'], color=c['color'][:3], width=0)

    # Draw completed polygons
    for poly in polygons:
        if use_alpha:
            # bounding box
            xs = [p[0] for p in poly]
            ys = [p[1] for p in poly]
            minx, miny = min(xs), min(ys)
            maxx, maxy = max(xs), max(ys)
            w, h = maxx-minx+4, maxy-miny+4
            temp = pygame.Surface((w,h), pygame.SRCALPHA)
            shifted = [(p[0]-minx+2, p[1]-miny+2) for p in poly]
            draw_polygon(temp, shifted, color=(200,120,180,160), width=0)
            surface.blit(temp, (minx-2, miny-2))
        else:
            draw_polygon(surface, poly, color=(200,120,180), width=0)

    # If currently creating polygon, draw its lines
    if is_creating_polygon and current_polygon:
        for i in range(len(current_polygon)-1):
            pygame.draw.line(surface, (255,255,255), current_polygon[i], current_polygon[i+1], 2)
        # draw points
        for p in current_polygon:
            pygame.draw.circle(surface, (255,255,0), p, 4)

    # Draw UI text
    font = pygame.font.SysFont(None, 18)
    info = [
        "Left click: add circle (normal mode) / add vertex (polygon mode)",
        "Right click: change nearest circle color",
        "p: toggle polygon creation mode",
        "Enter: finish polygon (when in polygon mode)",
        "t: toggle alpha (transparency)",
        "s: save screenshot, c: clear user circles & polygons",
    ]
    for i, line in enumerate(info):
        surf = font.render(line, True, (230, 230, 230))
        surface.blit(surf, (10, 10 + i * 18))

    # Draw color picker
    draw_color_picker(surface, color_picker)


def handle_events():
    """Handle pygame events: mouse, keyboard, quit."""
    global running, is_creating_polygon, current_polygon, use_alpha
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            elif event.key == pygame.K_c:
                # Clear user circles and polygons
                circles.clear()
                polygons.clear()
            elif event.key == pygame.K_s:
                # Save screenshot
                save_screenshot(screen)
            elif event.key == pygame.K_p:
                # Toggle polygon creation mode
                is_creating_polygon = not is_creating_polygon
                if not is_creating_polygon:
                    current_polygon.clear()
            elif event.key == pygame.K_RETURN:
                if is_creating_polygon and len(current_polygon) >= 3:
                    polygons.append(list(current_polygon))
                    current_polygon.clear()
                    is_creating_polygon = False
            elif event.key == pygame.K_t:
                use_alpha = not use_alpha
        # Delegate color-picker events first
        color_picker_handle_event(event, color_picker)

        if event.type == pygame.MOUSEBUTTONDOWN:
            if is_creating_polygon and event.button == 1:
                # Add vertex
                current_polygon.append(event.pos)
            else:
                if event.button == 1:  # left click - add a circle at mouse
                    mx, my = event.pos
                    new_circle = {
                        'pos': [mx, my],
                        'radius': random.randint(12, 36),
                        'color': get_picker_color(color_picker),
                    }
                    circles.append(new_circle)
                elif event.button == 3:  # right click - change color of nearest user circle
                    mx, my = event.pos
                    if circles:
                        nearest = min(circles, key=lambda c: (c['pos'][0]-mx)**2 + (c['pos'][1]-my)**2)
                        nearest['color'] = get_picker_color(color_picker)


def update(dt):
    """Update animation state.

    dt: seconds passed since last frame (float)
    """
    # Move the moving_circle and bounce on window edges
    pos = moving_circle['pos']
    vel = moving_circle['vel']
    r = moving_circle['radius']

    pos[0] += vel[0] * dt * FPS
    pos[1] += vel[1] * dt * FPS

    # Bounce on X
    if pos[0] - r < 0:
        pos[0] = r
        vel[0] = -vel[0]
    if pos[0] + r > WIDTH:
        pos[0] = WIDTH - r
        vel[0] = -vel[0]

    # Bounce on Y
    if pos[1] - r < 0:
        pos[1] = r
        vel[1] = -vel[1]
    if pos[1] + r > HEIGHT:
        pos[1] = HEIGHT - r
        vel[1] = -vel[1]

    # Move ellipse
    er = moving_ellipse['rect']
    er.x += moving_ellipse['vel'][0] * dt * FPS
    er.y += moving_ellipse['vel'][1] * dt * FPS
    # bounce ellipse
    if er.left < 0 or er.right > WIDTH:
        moving_ellipse['vel'][0] *= -1
    if er.top < 0 or er.bottom > HEIGHT:
        moving_ellipse['vel'][1] *= -1


# --- Main loop ---

def main():
    global running
    prev_time = time.time()
    while running:
        # dt in seconds
        now = time.time()
        dt = now - prev_time
        prev_time = now

        handle_events()
        update(dt)

        # Draw
        screen.fill(BG_COLOR)
        draw_shapes(screen)

        pygame.display.flip()
        clock.tick(FPS)

    # Graceful exit
    pygame.quit()
    sys.exit()


if __name__ == '__main__':
    main()
