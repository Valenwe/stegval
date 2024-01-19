from src.bits_operations import *
from src.pixel_operations import *
from src.file_operations import *

def data_to_image(data: bytes, isfile: bool, image_path: str, output_path: str, verbose: bool) -> str:
    print("Converting data to bits...", end="") # , flush=True)
    data = bytes_to_bits(data)
    print(" done.")

    data_length = format(len(data), '08b').zfill(64)
    data = data_length + ("1" if isfile else "0") + data
    # which byte to use
    data_pointer = 0

    # where are we in the function x value
    function_pointer = 0

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

    # check file length
    if not check_input_file_length(data, image_path):
        exit()

    print("Writing data to image...", end="", flush=True)

    while data_pointer < len(data):
        # get the bit to insert
        bit = data[data_pointer]

        # process pixel
        pixel_nb = next_pixel_nb(function_pointer)
        x, y, color_id = pixel_to_xy(pixel_nb, width, height)
        pixel_color = get_pixel_color(image, x, y)
        pixel_color_binary = list(rgb_to_binary(pixel_color))

        # new pixel
        pixel_color_binary[color_id] = pixel_color_binary[color_id][:-1] + bit
        r = pixel_color_binary[0]
        g = pixel_color_binary[1]
        b = pixel_color_binary[2]

        # make all changed pixel to red
        if verbose:
            r = "1" + r[1:]

        new_color = (int(r, 2), int(g, 2), int(b, 2))

        # change pixel
        image = change_pixel_color(image, x, y, new_color)
        data_pointer += 1
        function_pointer += 1

        # pixel_color = get_pixel_color(image, x, y)

    print(" done.")
    image.save(output_path, "PNG")
    image.close()

    print("Checking data lentgh writing...", end="", flush=True)
    image = Image.open(output_path)
    output_data_length = ""

    for function_pointer in range(64):
        pixel_nb = next_pixel_nb(function_pointer)
        x, y, color_id = pixel_to_xy(pixel_nb, width, height)
        pixel_color = get_pixel_color(image, x, y)
        pixel_color_binary = list(rgb_to_binary(pixel_color))
        output_data_length += pixel_color_binary[color_id][-1]
    image.close()

    if output_data_length == data_length:
        print(" done.")
        return output_path
    else:
        print(" error, data length don't match.")
        if verbose:
            print("data:   " + data_length)
            print("output: " + output_data_length)
        exit()

def extract_data_from_image(image_path: str, output_path: str, verbose: bool):
    image = Image.open(image_path)
    width, height = image.size

    data_length_bits = ''
    data_bits = ''

    data_pointer = 0
    function_pointer = 0

    # Assuming the first 64 bits encode the data length and 65th is the type
    while data_pointer < 65:
        # process pixel
        pixel_nb = next_pixel_nb(function_pointer)
        x, y, color_id = pixel_to_xy(pixel_nb, width, height)
        pixel_color = get_pixel_color(image, x, y)
        pixel_color_binary = list(rgb_to_binary(pixel_color))
        bit = pixel_color_binary[color_id][-1]

        # extract bit
        if data_pointer < 64:
            data_length_bits += bit
        else:
            isfile = bit == "1"
            print("File data detected." if isfile else "Text data detected.")
        data_pointer += 1
        function_pointer += 1

    data_length = int(data_length_bits, 2)
    data_pointer = 0
    while data_pointer < data_length:
        # process pixel
        pixel_nb = next_pixel_nb(function_pointer)
        x, y, color_id = pixel_to_xy(pixel_nb, width, height)
        pixel_color = get_pixel_color(image, x, y)
        pixel_color_binary = list(rgb_to_binary(pixel_color))

        # extract bit
        data_bits += pixel_color_binary[color_id][-1]
        function_pointer += 1
        data_pointer += 1

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