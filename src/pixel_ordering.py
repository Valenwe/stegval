import random
from tqdm import tqdm

from src.settings import CONCEAL_MOD_BIT_LENGTH, RANDOM_SEED_BIT_LENGTH
already_used_coordinates = set()

def reset_added_coordinates():
    """Will remove all entries in the already_used_coordinates set"""
    global already_used_coordinates
    already_used_coordinates = set()

def generate_simple_order(nb_iteration, image_width, image_height, starting_from=0, color_id=0, ordering_progress: tqdm = None) -> list[tuple[int, int, int]]:
    """Simple pixel order from top left to bottom right"""

    global already_used_coordinates
    pixel_order = []
    pixel_index = starting_from
    nb_fail = 0
    while len(pixel_order) < nb_iteration:
        x = pixel_index % image_width
        y = pixel_index // image_width

        is_already_added = False
        for col in range(3):
            if (x, y, col) in already_used_coordinates:
                is_already_added = True
                break

        if not is_already_added:
            pixel_order.append((x, y, color_id))

            # add to already added coordinates
            already_used_coordinates.add((x, y, color_id))

            if ordering_progress is not None:
                ordering_progress.update()
            nb_fail = 0
        else:
            nb_fail += 1

        if nb_fail > min(image_width, image_height) + 10:
            raise ValueError("Unable to add more pixels.")

        pixel_index += 1

    return pixel_order

def generate_square_order(nb_iteration, image_width, image_height, ordering_progress: tqdm = None) -> list[tuple[int, int, int]]:
    """Squared pixel order around the center of the image"""
    global already_used_coordinates

    # set the center as the first value
    x, y, color_id = image_width // 2, image_height // 2, 0
    pixel_order = [(x, y, color_id)]
    nb_fail = 0

    while len(pixel_order) < nb_iteration:
        color_id = (color_id + 1) % 3
        center_x = image_width // 2
        center_y = image_height // 2

        distance = max(abs(center_x - x), abs(center_y - y))

        # if the square ends, go for next one
        if (x == center_x and y == center_y) or (x == center_x - distance and y == center_y - distance + 1):
            x = center_x - distance - 1
            y = center_y - distance - 1

        # go right
        elif y == center_y - distance and x < center_x + distance:
            x = x + 1
            y = y

        # go down
        elif x == center_x + distance and y < center_y + distance:
            x = x
            y = y + 1

        # go left
        elif y == center_y + distance and x > center_x - distance:
            x = x - 1
            y = y

        # go up
        elif x == center_x - distance and y > center_y - distance:
            x = x
            y = y - 1

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

        is_already_added = False
        for col in range(3):
            if (x, y, col) in already_used_coordinates:
                is_already_added = True
                break

        if not is_already_added:
            pixel_order.append((x, y, color_id))

            # add to already added coordinates
            already_used_coordinates.add((x, y, color_id))
            if ordering_progress is not None:
                ordering_progress.update()
            nb_fail = 0
        else:
            nb_fail += 1

        if nb_fail > min(image_width, image_height) + 10:
            raise ValueError("Unable to add more pixels.")

    return pixel_order

def generate_random_order(nb_iteration, seed, image_width, image_height, ordering_progress: tqdm = None) -> list[tuple[int, int, int]]:
    """Random propagation of pixels"""
    pixel_order = []
    global already_used_coordinates
    current_seed = "{}{}{}".format(image_width, image_height, seed)
    rng = random.Random(current_seed)

    nb_fail = 0
    for x in range(image_width):
        for y in range(image_height):
            is_already_added = False
            for col in range(3):
                if (x, y, col) in already_used_coordinates:
                    is_already_added = True
                    break

            if not is_already_added:
                color_id = rng.randint(0, 2)
                if ordering_progress is not None and len(pixel_order) < nb_iteration:
                    ordering_progress.update()
                pixel_order.append((x, y, color_id))
                nb_fail = 0
            else:
                nb_fail += 1

            if nb_fail > min(image_width, image_height) + 10:
                raise ValueError("Unable to add more pixels.")

    # if we have enough values
    rng.shuffle(pixel_order)

    # add to already added coordinates
    for coord in pixel_order:
        already_used_coordinates.add(coord)

    return pixel_order


def generate_pixel_order(conceal_mod: str, image_width: int, image_height: int, data_length: int, seed: str = None, progress: bool = False) -> list[tuple[int, int, int]]:
    """Main function to generate the correct order of pixels depending on different sizes
    Args:
      conceal_mod: the mod used
      image_width: image shape
      image_height: image shape
      data_length: the size of the ordered array to return
      seed: the seed in case of random propagation
      progress: display a progress bar

    Returns: list of all pixels in order depending on the mod used"""

    ordering_progress = None
    if progress:
        ordering_progress = tqdm(total=data_length, desc="Generating pixel order...", colour="GREEN")

    # generate first conceal mod bits
    pixel_order = generate_simple_order(CONCEAL_MOD_BIT_LENGTH, image_width, image_height, ordering_progress=ordering_progress)

    # seed as a square
    if conceal_mod == "random":
        pixel_order += generate_square_order(RANDOM_SEED_BIT_LENGTH, image_width, image_height, ordering_progress=ordering_progress)

    if conceal_mod == "simple":
        pixel_order += generate_simple_order(data_length, image_width, image_height, starting_from=CONCEAL_MOD_BIT_LENGTH, ordering_progress=ordering_progress)

    elif conceal_mod == "square":
        pixel_order += generate_square_order(data_length, image_width, image_height, ordering_progress=ordering_progress)

    elif conceal_mod == "random" or conceal_mod == "password":
        pixel_order += generate_random_order(data_length, seed, image_width, image_height, ordering_progress=ordering_progress)

    if progress:
        ordering_progress.close()

    return pixel_order