from src.bits_operations import *
from src.pixel_operations import *
from src.file_operations import *
from src.visualizer import *

import time
from tqdm import tqdm

conceal_mods = ["simple", "square"]
conceal_mod_bitlength = 3
data_bitlength = 64
already_used_coordinates = set()
verbose_time_sleep = 0.001

def process_single_bit(image: Image, function_pointer: int, x, y, color_id, width, height, conceal_mod) -> (int, int, int):
    """Process to get the next single bit on the image
    Returns: x, y, color_id"""

    # process pixel
    valid_coordinates = False
    false_counter = 0

    # specify the number of tries depending on the minimum size side of the image
    max_number_fail_pixel = min(width, height) + 10
    while not valid_coordinates and false_counter < max_number_fail_pixel:
        try:
            x, y, color_id = next_pixel(function_pointer, x, y, color_id, width, height, conceal_mod_bitlength, conceal_mod)
            get_pixel_color(image, x, y)

            # check if the coordinates have been already used
            if (x, y, color_id) in already_used_coordinates:
                raise ValueError('These coordinates have already been used before.')

            valid_coordinates = True
        except (IndexError, ValueError):
            false_counter += 1

    if false_counter == max_number_fail_pixel:
        print(" error! Can't add any more bits to the image. You must find a bigger one.")
        image.close()
        exit()

    already_used_coordinates.add((x, y, color_id))

    return x, y, color_id

def hide_single_bit(image: Image, bit: str, x: int, y: int, color_id: int, verbose: bool):
    """Will hide the given bit on the given location"""
    pixel_color = get_pixel_color(image, x, y)
    pixel_color_binary = list(rgb_to_binary(pixel_color))

    # new pixel
    # make all changed pixel to red
    if verbose:
        pixel_color_binary[color_id] = "11" + pixel_color_binary[color_id][2:]

    pixel_color_binary[color_id] = pixel_color_binary[color_id][:-1] + bit
    r = pixel_color_binary[0]
    g = pixel_color_binary[1]
    b = pixel_color_binary[2]

    new_color = (int(r, 2), int(g, 2), int(b, 2))

    # change pixel
    image = change_pixel_color(image, x, y, new_color)
    return image

def extract_conceal_mod(image, width, height) -> (str, int):
    """Extract the bits containing the index of the conceal mod used
    Returns: bits containing the conceal mod, current color_id
    """
    x, y, color_id = (0, 0, 0)
    output_conceal_mod_bits = ""
    for function_pointer in range(conceal_mod_bitlength):
        x, y, color_id = next_pixel(function_pointer, x, y, color_id, width, height, conceal_mod_bitlength, "simple")
        pixel_color = get_pixel_color(image, x, y)
        pixel_color_binary = list(rgb_to_binary(pixel_color))
        output_conceal_mod_bits += pixel_color_binary[color_id][-1]

        already_used_coordinates.add((x, y, color_id))

    return output_conceal_mod_bits, color_id

def data_to_image(data: bytes, isfile: bool, image_path: str, output_path: str, conceal_mod: str, verbose: bool) -> str:
    print("Checking image properties...", end="")
    if is_image(image_path):
        if not image_path.endswith(".png"):
            image_path = convert_to_png(image_path)
        print(" done.")
    else:
        print(" error! File provided is not an image.")
        exit()

    print("Converting data to bits...", end="") # , flush=True)
    data = bytes_to_bits(data)
    print(" done.")

    global conceal_mods

    data_length = format(len(data), '08b').zfill(data_bitlength)
    conceal_mod_bits = format(conceal_mods.index(conceal_mod), "0{}b".format(conceal_mod_bitlength))
    data = conceal_mod_bits + data_length + ("1" if isfile else "0") + data

    # which byte to use from the data
    data_pointer = 0

    # where are we in the function x value (the iterator)
    function_pointer = 0

    # the first variables that will be changed
    x, y, color_id = (0, 0, 0)

    image = Image.open(image_path)
    width, height = image.size
    progress_bar = tqdm(total = len(data), colour="red", desc="Writing data to image...")

    # check file length
    if not check_input_file_length(data, image_path, data_bitlength, conceal_mod_bitlength):
        exit()

    if verbose:
        image_updater = ImageDisplayer(image)

    while data_pointer < len(data):
        # get the bit to insert
        bit = data[data_pointer]

        # first, write the mod used to conceal data on the first pixels (3 bits)
        if data_pointer < conceal_mod_bitlength:
            x, y, color_id = process_single_bit(image, function_pointer, x, y, color_id, width, height, "simple")
            image = hide_single_bit(image, bit, x, y, color_id, verbose)
        # then write using the correct conceal mod
        else:
            x, y, color_id = process_single_bit(image, function_pointer, x, y, color_id, width, height, conceal_mod)
            image = hide_single_bit(image, bit, x, y, color_id, verbose)

        # Will display pixel by pixel the progression
        if verbose:
            image_updater.refresh_image(image)
            time.sleep(verbose_time_sleep)

        data_pointer += 1
        function_pointer += 1
        progress_bar.update()

    progress_bar.close()
    image.save(output_path, "PNG")
    image.close()

    if verbose:
        os.system("pause")
        image_updater.close_plot()

    print("Checking data lentgh writing...", end="", flush=True)
    image = Image.open(output_path)

    output_data_length = ""
    output_conceal_mod_bits, color_id = extract_conceal_mod(image, width, height)
    x, y = (0, 0)

    function_pointer = conceal_mod_bitlength
    for _ in range(conceal_mod_bitlength, data_bitlength + conceal_mod_bitlength):
        x, y, color_id = next_pixel(function_pointer, x, y, color_id, width, height, conceal_mod_bitlength, conceal_mod)
        pixel_color = get_pixel_color(image, x, y)
        pixel_color_binary = list(rgb_to_binary(pixel_color))
        output_data_length += pixel_color_binary[color_id][-1]
        function_pointer += 1

    image.close()

    if output_data_length == data_length:
        print(" done.")
        return output_path
    else:
        print(" error, data length don't match.")
        if verbose:
            print("conceal_mod: ", conceal_mod_bits, "data:   " + data_length)
            print("conceal_mod: ", output_conceal_mod_bits, "output: " + output_data_length)
        exit()

def extract_data_from_image(image_path: str, output_path: str, verbose: bool):
    image = Image.open(image_path)
    width, height = image.size

    data_length_bits = ''
    data_bits = ''

    # init the first variables
    data_pointer = 0
    x, y = (0, 0)

    # start the function from after finding the conceal mod
    function_pointer = conceal_mod_bitlength

    conceal_mod_bits, color_id = extract_conceal_mod(image, width, height)
    conceal_mod = conceal_mods[int(conceal_mod_bits, 2)]
    print("Conceal mod detected:", conceal_mod[0].upper() + conceal_mod[1:] + ".")

    # Get the data length and the data type (file / text)
    while data_pointer < 65:
        # process pixel
        x, y, color_id = process_single_bit(image, function_pointer, x, y, color_id, width, height, conceal_mod)

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

    data_length = int(data_length_bits, 2)
    data_pointer = 0
    progress_bar = tqdm(total = data_length, colour="magenta", desc="Fetching data from image...")

    if verbose:
        image_updater = ImageDisplayer(image)
        image_updater.refresh_image(image)

    # Get the bulk data
    while data_pointer < data_length:
        # process pixel
        x, y, color_id = process_single_bit(image, function_pointer, x, y, color_id, width, height, conceal_mod)
        pixel_color = get_pixel_color(image, x, y)
        pixel_color_binary = list(rgb_to_binary(pixel_color))

        # extract bit
        data_bits += pixel_color_binary[color_id][-1]

        # will make the processed pixels go black (data length / file / conceal_mod bits not included)
        if verbose:
            pixel_color_binary[color_id] = "00" + pixel_color_binary[color_id][2:]
            r = pixel_color_binary[0]
            g = pixel_color_binary[1]
            b = pixel_color_binary[2]
            new_color = (int(r, 2), int(g, 2), int(b, 2))
            image = change_pixel_color(image, x, y, new_color)
            image_updater.refresh_image(image)
            time.sleep(verbose_time_sleep)

        function_pointer += 1
        data_pointer += 1
        progress_bar.update()

    if verbose:
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