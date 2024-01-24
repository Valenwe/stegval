from src.bits_operations import rgb_to_binary
from PIL import Image

class Pixel(tuple):
    def __init__(self, x, y, color_id):
        self.x = x
        self.y = y
        self.color_id = color_id

def change_pixel_color(image: Image, x, y, new_color):
    image.putpixel((x, y), new_color)
    return image

def get_pixel_color(image: Image, x, y):
    pixel_color = image.getpixel((x, y))
    return pixel_color

def hide_single_bit(image: Image, bit: str, x: int, y: int, color_id: int, verbose: int) -> Image:
    """Will hide the given bit on the given location"""
    pixel_color = get_pixel_color(image, x, y)
    pixel_color_binary = list(rgb_to_binary(pixel_color))

    # new pixel
    # make all changed pixel to red
    if verbose >= 1:
        pixel_color_binary[color_id] = "11" + pixel_color_binary[color_id][2:]

    pixel_color_binary[color_id] = pixel_color_binary[color_id][:-1] + bit
    r = pixel_color_binary[0]
    g = pixel_color_binary[1]
    b = pixel_color_binary[2]

    new_color = (int(r, 2), int(g, 2), int(b, 2))

    # change pixel
    image = change_pixel_color(image, x, y, new_color)
    return image

def set_pixel_black(image: Image, pixel: Pixel) -> Image:
    """For debugging purpose, will set a given pixel black"""
    x, y, color_id = pixel
    pixel_color = get_pixel_color(image, x, y)
    pixel_color_binary = list(rgb_to_binary(pixel_color))
    pixel_color_binary[color_id] = "00" + pixel_color_binary[color_id][2:]
    r = pixel_color_binary[0]
    g = pixel_color_binary[1]
    b = pixel_color_binary[2]
    new_color = (int(r, 2), int(g, 2), int(b, 2))
    image = change_pixel_color(image, x, y, new_color)
    return image

def get_bit_from_pixel(image: Image, pixel: Pixel) -> str:
    """Get the less significant bit from a given pixel (x, y, color_id)"""
    x, y, color_id = pixel
    pixel_color = get_pixel_color(image, x, y)
    pixel_color_binary = list(rgb_to_binary(pixel_color))
    return pixel_color_binary[color_id][-1]
