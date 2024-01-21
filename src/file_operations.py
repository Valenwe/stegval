import requests
from bs4 import BeautifulSoup
import logging
from PIL import Image
import os

from src.bits_operations import starts_with_hex_signature

def get_magic_numbers() -> dict[str, str]:
    print("Fetching magic numbers...", end="", flush=True)
    url = "https://en.wikipedia.org/wiki/List_of_file_signatures"

    response = requests.get(url)
    html_content = response.content

    soup = BeautifulSoup(html_content, 'html.parser')
    table = soup.find('table', {'class': 'wikitable'})

    data = {}
    for row in table.find_all('tr')[1:]:
        columns = row.find_all('td')
        if len(columns) >= 4:
            hex_signature = columns[0].find("code").text
            extension = columns[3].get_text().strip()
            data[hex_signature] = extension

    print(" done.")
    return data

def represent_bytes(bytes_length) -> str:
    if bytes_length >= 1024 ** 3:
        gigabytes_representation = bytes_length / (1024 ** 3)
        str_bytes = f"{gigabytes_representation:.2f} GB"

    elif bytes_length >= 1024 ** 2:
        megabytes_representation = bytes_length / (1024 ** 2)
        str_bytes = f"{megabytes_representation:.2f} MB"

    elif bytes_length >= 1024:
        kilobytes_representation = bytes_length / 1024
        str_bytes = f"{kilobytes_representation:.2f} KB"

    else:
        str_bytes = f"{bytes_length:d} B"

    return str_bytes

def check_input_file_length(data: bytes, input_path: str, data_bitlength: int, conceal_mod_bitlength: int) -> bool:
    """Checks if the data can fit inside the given image"""
    with Image.open(input_path) as img:
        width, height = img.size
        total_pixels = width * height
    input_length = total_pixels

    data_length = len(data)
    minimum_image_required = data_length + (data_bitlength + conceal_mod_bitlength)
    maximum_input_required = input_length - (data_bitlength + conceal_mod_bitlength)

    if input_length < minimum_image_required:

        image_size = "Actual image size: {}".format(represent_bytes(input_length))
        input_size = "Actual input size: {}".format(represent_bytes(data_length))
        warning = "<!> Sizes may vary depending on their bit representation, not their real size <!>"

        minimum_repr = "Minimum image size required for that input is  {}".format(represent_bytes(minimum_image_required))
        maximum_repr = "Maximum input size possible from that image is {}".format(represent_bytes(maximum_input_required))

        logging.error("The input file is too small for the data you're trying to cipher.")
        for line in [image_size, input_size, warning, minimum_repr, maximum_repr]:
            print(line)

        return False
    return True

def is_image(file_path):
    try:
        # Attempt to open the image file
        with Image.open(file_path) as img:
            img.verify()
        return True
    except Exception as e:
        print(e)
        return False

def convert_to_png(input_path):
    try:
        with Image.open(input_path) as img:

            input_directory, input_filename = os.path.split(input_path)
            output_filename = os.path.splitext(input_filename)[0] + ".png"
            output_path = os.path.join(input_directory, output_filename)

            if os.path.exists(output_path):
                os.remove(output_path)

            # Convert to RGB if needed
            img = img.convert('RGB')
            img.save(output_path, format='PNG', mode='RGB')

        os.remove(input_path)
        return output_path
    except Exception as e:
        print(f"Error: {e}")

def get_magic_signature(data: bytes) -> str:
    """Define magic signatures for common file types"""
    magic_signatures = get_magic_numbers()

    # Check if any magic signature matches
    for signature, file_type in magic_signatures.items():
        if starts_with_hex_signature(signature, data):
            return file_type

    if is_text_file(data):
        return "txt"

    # Return None if no match is found
    return None

def is_text_file(data: bytes):
    try:
        content_sample = data.decode("utf-8")[:len(data) // 2]

        if '\x00' in content_sample or '\t' in content_sample or '\x00' in content_sample:
            return False
        return True
    except Exception as e:
        return False