from src.bits_operations import *
from src.pixel_operations import *
from src.file_operations import *
from src.visualizer import *

import secrets
import random
import time
from tqdm import tqdm
import hashlib

conceal_mods = ["simple", "square", "random", "password"]
conceal_mod_bitlength = 3
data_bitlength = 64
already_used_coordinates = set()
verbose_time_sleep = 0.01
random_seed_length = 32

def init_pixels_remaining(image_width, image_height, seed):
    """Will create an array of all remaining pixels, and shuffle it depending on the given seed"""
    pixels_remaining = []
    current_seed = "{}{}{}".format(image_width, image_height, seed)
    rng = random.Random(current_seed)

    for x in range(image_width):
        for y in range(image_height):
            is_already_added = False
            for col in range(3):
                if (x, y, col) in already_used_coordinates:
                    is_already_added = True
                    break

            if not is_already_added:
                color_id = rng.randint(0, 2)
                if (x, y, color_id) not in already_used_coordinates:
                    pixels_remaining.append((x, y, color_id))

    rng.shuffle(pixels_remaining)
    return pixels_remaining

def process_single_bit(image: Image, function_pointer: int, x, y, color_id, width, height, conceal_mod, pixels_remaining: list = None) -> (int, int, int, list):
    """Process to get the next single bit on the image
    Returns: x, y, color_id"""

    # process pixel
    valid_coordinates = False
    false_counter = 0

    # specify the number of tries depending on the minimum size side of the image
    max_number_fail_pixel = min(width, height) + 10
    while not valid_coordinates and false_counter < max_number_fail_pixel:
        try:
            x, y, color_id = next_pixel(function_pointer, x, y, color_id, width, height, conceal_mod_bitlength
                                        , conceal_mod, pixels_remaining)
            get_pixel_color(image, x, y)

            # check if the coordinates have been already used
            if (x, y, color_id) in already_used_coordinates:
                raise ValueError('These coordinates have already been used before.')

            valid_coordinates = True
        except (IndexError, ValueError):
            false_counter += 1

    if false_counter == max_number_fail_pixel:
        logging.error("Error! Can't add any more bits to the image. You must find a bigger one.")
        image.close()
        exit()

    already_used_coordinates.add((x, y, color_id))

    return x, y, color_id

def hide_single_bit(image: Image, bit: str, x: int, y: int, color_id: int, verbose: int):
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

def extract_conceal_mod(image, width, height) -> (str, int, int, int):
    """Extract the bits containing the index of the conceal mod used
    Returns: bits containing the conceal mod, current x, current y, current color_id
    """
    x, y, color_id = (0, 0, 0)
    output_conceal_mod_bits = ""
    for function_pointer in range(conceal_mod_bitlength):
        x, y, color_id = next_pixel(function_pointer, x, y, color_id, width, height, conceal_mod_bitlength, "simple")
        pixel_color = get_pixel_color(image, x, y)
        pixel_color_binary = list(rgb_to_binary(pixel_color))
        output_conceal_mod_bits += pixel_color_binary[color_id][-1]

        already_used_coordinates.add((x, y, color_id))

    return output_conceal_mod_bits, x, y, color_id

def extract_seed(image, previous_x, previous_y, previous_color_id, width, height) -> (str, int, int, int):
    """Extract the bits containing the index of the conceal mod used
    Returns: seed, x, y, current color_id
    """
    x, y, color_id = previous_x, previous_y, previous_color_id
    seed_bits = ""
    for function_pointer in range(conceal_mod_bitlength, conceal_mod_bitlength + random_seed_length):
        x, y, color_id = next_pixel(function_pointer, x, y, color_id, width, height, conceal_mod_bitlength, "square")
        pixel_color = get_pixel_color(image, x, y)
        pixel_color_binary = list(rgb_to_binary(pixel_color))
        seed_bits += pixel_color_binary[color_id][-1]

        already_used_coordinates.add((x, y, color_id))

    return str(int(seed_bits[:random_seed_length], 2)), x, y, color_id

def init_random_iterator(passworded = False) -> (str, str):
    """Will define seed & list of coordinates to fill
    Returns the seed, seed bits"""

    if not passworded:
        # Generate a secure random byte string with the specified length
        random_bytes = secrets.token_bytes(random_seed_length // 4)

        # Convert the byte string to an integer
        seed = int.from_bytes(random_bytes, "big")
    else:
        password = input("What is the password for your data?\n>>> ")
        salt = b'segval_passworded'

        # Use PBKDF2 to derive a key from the password and salt
        key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
        seed = int.from_bytes(key, 'big')

    # Convert the integer to a binary string and zero-pad it
    seed_binary = format(seed, f'08b')[:random_seed_length]

    return str(int(seed_binary, 2)), seed_binary

def data_to_image(data: bytes, isfile: bool, image_path: str, output_path: str, conceal_mod: str, verbose: int) -> str:
    print("Checking image properties...", end="")
    if is_image(image_path):
        if not image_path.endswith(".png"):
            image_path = convert_to_png(image_path)
        print(" done.")
    else:
        print(" error! File provided is not an image.")
        exit()

    image = Image.open(image_path)
    width, height = image.size

    print("Converting data to bits...", end="") # , flush=True)
    data = bytes_to_bits(data)
    print(" done.")

    data_length = format(len(data), '08b').zfill(data_bitlength)
    conceal_mod_bits = format(conceal_mods.index(conceal_mod), "0{}b".format(conceal_mod_bitlength))

    # init variables in case of random based conceal mod
    pixels_remaining, seed = None, None
    if conceal_mod == "random" or conceal_mod == "password":
        seed, seed_bits = init_random_iterator(conceal_mod == "password")

    # real data line
    data = conceal_mod_bits + (seed_bits if conceal_mod == "random" else "") + data_length + ("1" if isfile else "0") + data

    # which byte to use from the data
    data_pointer = 0

    # where are we in the function x value (the iterator)
    function_pointer = 0

    # the first variables that will be changed
    x, y, color_id = (0, 0, 0)

    # check file length
    if not check_input_file_length(data, image_path, data_bitlength, conceal_mod_bitlength):
        exit()

    progress_bar = tqdm(total = len(data), colour="red", desc="Writing data to image...")

    if verbose >= 2:
        image_updater = ImageDisplayer(image)

    global already_used_coordinates

    while data_pointer < len(data):
        # get the bit to insert
        bit = data[data_pointer]

        # first, write the mod used to conceal data on the first pixels (3 bits)
        if data_pointer < conceal_mod_bitlength:
            x, y, color_id = process_single_bit(image, function_pointer, x, y, color_id, width, height
                                                , "simple", pixels_remaining)
            image = hide_single_bit(image, bit, x, y, color_id, verbose)

            # set random variables to propagate correctly the pixels
            if conceal_mod == "password" and data_pointer == conceal_mod_bitlength - 1:
                pixels_remaining = init_pixels_remaining(width, height, seed)
        # in the case of a randomly propagated steg, will put the seed at the center of the image
        elif conceal_mod == "random" and data_pointer < conceal_mod_bitlength + random_seed_length:
            x, y, color_id = process_single_bit(image, function_pointer, x, y, color_id, width, height
                                                , "square", pixels_remaining)
            image = hide_single_bit(image, bit, x, y, color_id, verbose)

            # set random variables to propagate correctly the pixels
            if data_pointer == conceal_mod_bitlength + random_seed_length - 1:
                function_pointer = conceal_mod_bitlength - 1
                pixels_remaining = init_pixels_remaining(width, height, seed)

        # then write using the correct conceal mod
        else:
            x, y, color_id = process_single_bit(image, function_pointer, x, y, color_id, width, height
                                                , conceal_mod, pixels_remaining)
            image = hide_single_bit(image, bit, x, y, color_id, verbose)

        # Will display pixel by pixel the progression
        if verbose >= 2:
            image_updater.refresh_image(image)
            time.sleep(verbose_time_sleep)

        data_pointer += 1
        function_pointer += 1
        progress_bar.update()

    progress_bar.close()
    image.save(output_path, "PNG")
    image.close()

    if verbose >= 2:
        os.system("pause")
        image_updater.close_plot()

    print("Checking data lentgh writing...", flush=True)
    output_conceal_mod_bits, output_data_length, output_seed = extract_data_from_image(output_path, None, False, only_data_length=True)

    if output_data_length == data_length:
        print("Done.")
        return output_path
    else:
        logging.error("Error, data length don't match.")
        if verbose >= 1:
            print("conceal_mod: ", conceal_mod_bits, "data:   " + data_length)
            print("conceal_mod: ", output_conceal_mod_bits, "output: " + output_data_length)
            print("seed:", seed, "output seed:", output_seed)
        exit()

def extract_data_from_image(image_path: str, output_path: str, verbose: int, only_data_length: bool = False):
    image = Image.open(image_path)
    width, height = image.size

    global already_used_coordinates
    already_used_coordinates = set()

    data_length_bits = ''
    data_bits = ''

    # init the first variables
    data_pointer = 0

    # start the function from after finding the conceal mod
    function_pointer = conceal_mod_bitlength

    conceal_mod_bits, x, y, color_id = extract_conceal_mod(image, width, height)
    conceal_mod = conceal_mods[int(conceal_mod_bits, 2)]
    print("Conceal mod detected:", conceal_mod[0].upper() + conceal_mod[1:] + ".")

    # In case of random mod
    pixels_remaining, seed = None, None
    if conceal_mod == "random" or conceal_mod == "password":
        if conceal_mod == "random":
            seed, x, y, color_id = extract_seed(image, x, y, color_id, width, height)
        else:
            seed, _ = init_random_iterator(conceal_mod == "password")
        pixels_remaining = init_pixels_remaining(width, height, seed)

    # Get the data length and the data type (file / text)
    while data_pointer < data_bitlength + 1:
        # process pixel
        x, y, color_id = process_single_bit(image, function_pointer, x, y, color_id, width, height, conceal_mod, pixels_remaining)

        pixel_color = get_pixel_color(image, x, y)
        pixel_color_binary = list(rgb_to_binary(pixel_color))
        bit = pixel_color_binary[color_id][-1]

        # extract bit
        if data_pointer < data_bitlength:
            data_length_bits += bit
        else:
            isfile = bit == "1"
            print("File data detected." if isfile else "Text data detected.")

        data_pointer += 1
        function_pointer += 1

    # for verification purpose
    if only_data_length:
        return conceal_mod_bits, data_length_bits, seed

    data_length = int(data_length_bits, 2)
    data_pointer = 0

    # Check if the password seems to be false
    if conceal_mod == "password" and data_length > (width * height) - (data_bitlength + conceal_mod_bitlength):
        logging.error("This password seems to be wrong...")
        if verbose:
            print("Data length detected:", data_length)
        exit()

    progress_bar = tqdm(total = data_length, colour="magenta", desc="Fetching data from image...")

    if verbose >= 2:
        image_updater = ImageDisplayer(image)
        image_updater.refresh_image(image)

    # Get the bulk data
    while data_pointer < data_length:
        # process pixel
        x, y, color_id = process_single_bit(image, function_pointer, x, y, color_id, width, height, conceal_mod, pixels_remaining)
        pixel_color = get_pixel_color(image, x, y)
        pixel_color_binary = list(rgb_to_binary(pixel_color))

        # extract bit
        data_bits += pixel_color_binary[color_id][-1]

        # will make the processed pixels go black (data length / file / conceal_mod bits not included)
        if verbose >= 1:
            pixel_color_binary[color_id] = "00" + pixel_color_binary[color_id][2:]
            r = pixel_color_binary[0]
            g = pixel_color_binary[1]
            b = pixel_color_binary[2]
            new_color = (int(r, 2), int(g, 2), int(b, 2))
            image = change_pixel_color(image, x, y, new_color)

            if verbose >= 2:
                image_updater.refresh_image(image)
                time.sleep(verbose_time_sleep)

        function_pointer += 1
        data_pointer += 1
        progress_bar.update()

    if verbose >= 2:
        os.system("pause")
        image_updater.close_plot()

    progress_bar.close()
    image.close()

    # Convert the bit string to bytes
    byte_array = bytearray(int(data_bits[i:i+8], 2) for i in range(0, len(data_bits), 8))

    if isfile:
        _, file_extension = os.path.splitext(output_path)

        # Specify the file path
        if not bool(file_extension):
            returned_ext = get_magic_signature(byte_array)
            ext = "." + (returned_ext if returned_ext is not None else "")
            file_path = output_path + ext
        else:
            file_path = output_path

        # Write the bytes to the file
        with open(file_path, "wb") as file:
            file.write(byte_array)

        return file_path
    else:
        extracted_text = bits_to_text(data_bits)
        return extracted_text