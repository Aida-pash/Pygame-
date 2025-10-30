import pygame
import random
from datetime import datetime
from pathlib import Path

# Drawing helpers

def draw_line(surface, start_pos, end_pos, color=(255, 255, 255), width=1):
    """Draw a line with given width and color."""
    pygame.draw.line(surface, color, start_pos, end_pos, width)


def draw_rect(surface, rect, color=(255, 255, 255), width=0):
    """Draw rectangle. width=0 fills the rect, otherwise draws border of thickness width."""
    pygame.draw.rect(surface, color, rect, width)


def draw_circle(surface, center, radius, color=(255, 255, 255), width=0):
    """Draw circle. width=0 fills the circle, otherwise draws border."""
    pygame.draw.circle(surface, color, center, radius, width)


def draw_polygon(surface, point_list, color=(255, 255, 255), width=0):
    """Draw polygon given a list of points (>=3)."""
    pygame.draw.polygon(surface, color, point_list, width)


def draw_ellipse(surface, rect, color=(255, 255, 255), width=0):
    """Optional ellipse helper."""
    pygame.draw.ellipse(surface, color, rect, width)


# Utility helpers

def random_color():
    """Return a random RGB color tuple."""
    return (random.randint(30, 255), random.randint(30, 255), random.randint(30, 255))


def save_screenshot(surface, folder='screenshots'):
    """Save the current surface to a timestamped PNG file in folder.

    Returns the file path as a string.
    """
    Path(folder).mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = Path(folder) / f'screenshot_{ts}.png'
    try:
        pygame.image.save(surface, str(filename))
        print(f'Screenshot saved: {filename}')
        return str(filename)
    except Exception as e:
        print('Failed to save screenshot:', e)
        return None
