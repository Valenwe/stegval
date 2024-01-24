from src.bits_operations import *
from src.pixel_operations import *
from src.file_operations import *
from src.visualizer import *
from src.pixel_ordering import *
from src.settings import CONCEAL_MOD_BIT_LENGTH, RANDOM_SEED_BIT_LENGTH, DATA_BIT_LENGTH, CONCEAL_MODS, VERBOSE_TIME_SLEEP


import secrets
import time
from tqdm import tqdm
import hashlib

def init_random_iterator(passworded = False) -> (str, str):
    """Will define seed & list of coordinates to fill
    Returns the seed, seed bits"""

    if not passworded:
        # Generate a secure random byte string with the specified length
        random_bytes = secrets.token_bytes(RANDOM_SEED_BIT_LENGTH // 4)

        # Convert the byte string to an integer
        seed = int.from_bytes(random_bytes, "big")
    else:
        password = input("What is the password for your data?\n>>> ")
        salt = b'segval_passworded'

        # Use PBKDF2 to derive a key from the password and salt
        key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
        seed = int.from_bytes(key, 'big')

    # Convert the integer to a binary string and zero-pad it
    seed_binary = format(seed, f'08b')[:RANDOM_SEED_BIT_LENGTH]

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

    data_length = format(len(data), '08b').zfill(DATA_BIT_LENGTH)
    conceal_mod_bits = format(CONCEAL_MODS.index(conceal_mod), "0{}b".format(CONCEAL_MOD_BIT_LENGTH))

    # init variables in case of random based conceal mod
    seed = None
    if conceal_mod == "random" or conceal_mod == "password":
        seed, seed_bits = init_random_iterator(conceal_mod == "password")

    # real data line
    data = conceal_mod_bits + (seed_bits if conceal_mod == "random" else "") + data_length + ("1" if isfile else "0") + data

    # which byte to use from the data
    data_pointer = 0

    # check file length
    if not check_input_file_length(data, image_path, DATA_BIT_LENGTH, CONCEAL_MOD_BIT_LENGTH):
        exit()

    pixel_order = generate_pixel_order(conceal_mod, width, height, len(data) + 1, seed, True)
    progress_bar = tqdm(total = len(data), colour="red", desc="Writing data to image...")

    if verbose >= 2:
        image_updater = ImageDisplayer(image)


    while data_pointer < len(data):
        # get the bit to insert
        bit = data[data_pointer]

        x, y, color_id = pixel_order[data_pointer]
        image = hide_single_bit(image, bit, x, y, color_id, verbose)

        # Will display pixel by pixel the progression
        if verbose >= 2:
            image_updater.refresh_image(image)
            time.sleep(VERBOSE_TIME_SLEEP)

        data_pointer += 1
        progress_bar.update()

    progress_bar.close()
    image.save(output_path, "PNG")
    image.close()

    if verbose >= 2:
        os.system("pause")
        image_updater.close_plot()

    print("Checking data lentgh writing...", flush=True)
    reset_added_coordinates()
    output_conceal_mod_bits, output_data_length, output_seed = extract_data_from_image(output_path, None, verbose, only_data_length=True)

    if output_data_length == data_length:
        print("Output has valid data lentgh.")
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

    if verbose >= 2:
        image_updater = ImageDisplayer(image)
        image_updater.refresh_image(image)

    # init data length variables
    data_length_bits = ""
    data_bits = ""

    conceal_mod_bits = ""
    conceal_mod_pixel_order = generate_simple_order(CONCEAL_MOD_BIT_LENGTH, width, height)
    for pixel in conceal_mod_pixel_order:
        conceal_mod_bits += get_bit_from_pixel(image, pixel)

        if verbose >= 2:
            image = set_pixel_black(image, pixel)
            image_updater.refresh_image(image)

    conceal_mod = CONCEAL_MODS[int(conceal_mod_bits, 2)]

    print("Conceal mod detected:", conceal_mod[0].upper() + conceal_mod[1:] + ".")

    # In case of random mod, fetch the seed
    seed = None
    if conceal_mod == "random" or conceal_mod == "password":
        if conceal_mod == "random":
            seed_pixel_order = generate_square_order(RANDOM_SEED_BIT_LENGTH, width, height)
            seed_bits = ""
            for pixel in seed_pixel_order:
                seed_bits += get_bit_from_pixel(image, pixel)
                if verbose >= 2:
                    image = set_pixel_black(image, pixel)
                    image_updater.refresh_image(image)

            seed = str(int(seed_bits[:RANDOM_SEED_BIT_LENGTH], 2))
        else:
            seed, _ = init_random_iterator(conceal_mod == "password")

    # generate the order from beginning to the end of the data length bits
    bits_before_data_length = CONCEAL_MOD_BIT_LENGTH + (RANDOM_SEED_BIT_LENGTH if conceal_mod == "random" else 0)
    total_data_length = bits_before_data_length + DATA_BIT_LENGTH + 1

    # reset to be able to get the whole pixel order without previous added coordinates
    reset_added_coordinates()
    data_length_pixel_order = generate_pixel_order(conceal_mod, width, height, total_data_length, seed)

    # init the pointer variable to after reading conceal mod & seed
    data_pointer = bits_before_data_length

    # Get the data length and the data type (file / text)
    while data_pointer < total_data_length:
        # process pixel
        pixel = data_length_pixel_order[data_pointer]
        bit = get_bit_from_pixel(image, pixel)

        # extract bit
        if data_pointer < bits_before_data_length + DATA_BIT_LENGTH:
            data_length_bits += bit
        else:
            isfile = bit == "1"
            print("File data detected." if isfile else "Text data detected.")

        if verbose >= 2:
            image = set_pixel_black(image, pixel)
            image_updater.refresh_image(image)

        data_pointer += 1

    if verbose >= 2:
        os.system("pause")

    # for verification purpose
    if only_data_length:
        return conceal_mod_bits, data_length_bits, seed

    total_data_length = bits_before_data_length + DATA_BIT_LENGTH + 1 + int(data_length_bits, 2)
    reset_added_coordinates()
    pixel_order = generate_pixel_order(conceal_mod, width, height, total_data_length, seed, True)
    data_pointer = bits_before_data_length + DATA_BIT_LENGTH + 1

    # Check if the password seems to be false
    if conceal_mod == "password" and total_data_length > (width * height) or total_data_length == data_pointer:
        logging.error("This password seems to be wrong...")
        if verbose:
            print("Data length detected:", total_data_length)
        exit()

    progress_bar = tqdm(total = total_data_length - data_pointer, colour="magenta", desc="Fetching data from image...")

    # Get the bulk data
    while data_pointer < total_data_length:
        # process pixel
        x, y, color_id = pixel_order[data_pointer]
        pixel_color = get_pixel_color(image, x, y)
        pixel_color_binary = list(rgb_to_binary(pixel_color))

        # extract bit
        data_bits += pixel_color_binary[color_id][-1]

        # will make the processed pixels go black (data length / file / conceal_mod bits not included)
        if verbose >= 1:
            image = set_pixel_black(image, (x, y, color_id))

            if verbose >= 2:
                image_updater.refresh_image(image)
                time.sleep(VERBOSE_TIME_SLEEP)

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