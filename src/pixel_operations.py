from PIL import Image

def change_pixel_color(image: Image, x, y, new_color):
    image.putpixel((x, y), new_color)
    return image

def get_pixel_color(image, x, y):
    pixel_color = image.getpixel((x, y))

    return pixel_color


def pixel_to_xy(pixel_index, image_width, image_height) -> (int, int, int):
    # returns x, y and the color_id (0: red, 1: green, 2: blue)
    if 0 <= pixel_index < (image_width * image_height):
        y = pixel_index // image_width
        x = pixel_index % image_width
        return x, y, 0
    else:
        raise ValueError(f"Invalid pixel_index: {pixel_index}. Out of range for the given image size.")


def next_pixel_nb(x):
    # function that will say where the next pixel nb will be
    return x