from PIL import Image

def change_pixel_color(image: Image, x, y, new_color):
    image.putpixel((x, y), new_color)
    return image

def get_pixel_color(image: Image, x, y):
    pixel_color = image.getpixel((x, y))

    return pixel_color

def simple_iterator(pixel_index, color_id, image_width) -> (int, int, int):
    """Will iterate pixel by pixel from top left corner of the image"""
    x = pixel_index % image_width
    y = pixel_index // image_width

    return x, y, color_id

def square_iterator(iterator, conceal_mod_bitlength, previous_x, previous_y, color_id, image_width, image_height) -> (int, int, int):
    """Will iterate the pixels from center, then forming a square clockwise"""
    color_id = (color_id + 1) % 3
    center_x = image_width // 2
    center_y = image_height // 2

    if iterator == conceal_mod_bitlength:
        return image_width // 2, image_height // 2, color_id  # Start from the center

    distance = max(abs(center_x - previous_x), abs(center_y - previous_y))

    # if the square ends, go for next one
    if (previous_x == center_x and previous_y == center_y) or (previous_x == center_x - distance and previous_y == center_y - distance + 1):
        x = center_x - distance - 1
        y = center_y - distance - 1

    # go right
    elif previous_y == center_y - distance and previous_x < center_x + distance:
        x = previous_x + 1
        y = previous_y

    # go down
    elif previous_x == center_x + distance and previous_y < center_y + distance:
        x = previous_x
        y = previous_y + 1

    # go left
    elif previous_y == center_y + distance and previous_x > center_x - distance:
        x = previous_x - 1
        y = previous_y

    # go up
    elif previous_x == center_x - distance and previous_y > center_y - distance:
        x = previous_x
        y = previous_y - 1

    # handle if the square is filling the whole image size (depends on its size)
    if image_width > image_height:
        if y < 0:
            x = center_x + distance + 1
            y = 0
        elif y >= image_height:
            x = center_x - distance
            y = center_y + image_height // 2
    else:
        if x < 0:
            x = center_x - image_width // 2
            y = center_y - distance - 1
        elif x >= image_width:
            x = center_x + image_width // 2
            y = center_y + distance

    return x, y, color_id


def next_pixel(iterator, previous_x, previous_y, previous_color_id, image_width, image_height, conceal_mod_bitlength, mod="simple") -> (int, int, int):
    """function that will say what next pixel will be changed
    Returns x, y, color_id (0: red, 1: green, 2: blue)"""

    if mod == "simple":
        x, y, color_id = simple_iterator(iterator, previous_color_id, image_width)
    elif mod == "square":
        x, y, color_id = square_iterator(iterator, conceal_mod_bitlength, previous_x, previous_y, previous_color_id, image_width, image_height)

    return x, y, color_id
