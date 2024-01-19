from PIL import Image
from src.file_operations import get_magic_numbers

def rgb_to_binary(rgb):
    binary_values = [format(value, '08b') for value in rgb]
    return binary_values

def bytes_to_bits(byte_data):
    bits = ''
    for byte in byte_data:
        bits += format(byte, '08b')  # '08b' ensures that each byte is represented as 8 bits
    return bits

def bits_to_text(bits):
    text = ''.join([chr(int(bits[i:i+8], 2)) for i in range(0, len(bits), 8)])
    return text

def image_to_bits(image_path):
    image = Image.open(image_path)
    width, height = image.size

    pixel_values = list(image.getdata())
    bits = ''.join(format(value, '08b') for pixel in pixel_values for value in pixel)

    return bits, width, height

def get_magic_signature(data: bytes) -> str:
    # Define magic signatures for common file types
    magic_signatures = get_magic_numbers()

    # Check if any magic signature matches
    for signature, file_type in magic_signatures.items():
        if starts_with_hex_signature(signature, data):
            return file_type

    # Return None if no match is found
    return None

def starts_with_hex_signature(hex_signature: str, bytes_data: bytes) -> bool:
    # Remove spaces and non-hex characters from the signature
    cleaned_signature = ''.join(char for char in hex_signature if char.isdigit() or char.isalpha() or char == '?')

    for i in range(len(cleaned_signature) // 2):
        signature_hex = cleaned_signature[i*2:(i*2)+2]

        if signature_hex == "??":
            continue

        # Convert the single byte to hex
        data_hex = hex(bytes_data[i])[2:].upper().zfill(2)

        if data_hex != signature_hex:
            return False

    return True