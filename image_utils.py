from msvcrt import locking

from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import os

BLACK_RECT_PATH = Path('images', 'empty_black_rectangle.png')
STARTING_FONT_SIZE = 72
QUOTE_MAX_TEXT_WIDTH = 555
QUOTE_MAX_TEXT_HEIGHT = 500

def draw_quote(text, author="Abraham Lincoln"):
    text = f'\"{text}\"'

    my_image = Image.open(BLACK_RECT_PATH)
    draw = ImageDraw.Draw(my_image)

    i_width, i_height = my_image.size

    font_size = STARTING_FONT_SIZE
    font = ImageFont.truetype("arial.ttf", font_size)

    while True:
        font = ImageFont.truetype("arial.ttf", font_size)

        loc_left, loc_top, loc_right, loc_down = draw.multiline_textbbox((0, 0), text, font=font)
        t_width = loc_right - loc_left
        t_height = loc_top - loc_down

        if t_width <= QUOTE_MAX_TEXT_WIDTH and t_height <= QUOTE_MAX_TEXT_HEIGHT:
            break
        else:
            font_size -= 2

    position = (0.2 * i_width + i_width / 2, -0.1 * i_height + i_height / 2)

    draw.multiline_text(position, text, (255, 255, 255), font=font, anchor='mm')

    my_image.save('temp\\temp_image.png')


if __name__ == '__main__':
    draw_quote("a\n\n\n\na")