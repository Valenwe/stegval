import os
import argparse
import logging
import sys

from src.settings import CONCEAL_MODS
from src.data_writing import *

banner = """ _______________________ _______         _______ _
(  ____ \__   __(  ____ (  ____ \\     /(  ___  | \\
| (    \/  ) (  | (    \/ (    \/ )   ( | (   ) | (
| (_____   | |  | (__   | |     | |   | | (___) | |
(_____  )  | |  |  __)  | | ____( (   ) )  ___  | |
      ) |  | |  | (     | | \_  )\ \_/ /| (   ) | |
/\____) |  | |  | (____/\ (___) | \   / | )   ( | (____/\\ v1.3 by Valenwe
\_______)  )_(  (_______(_______)  \_/  |/     \(_______/
"""

if __name__ == "__main__":
    print(banner)
    parser = argparse.ArgumentParser(prog="StegVal", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-m", "--mode", dest="mode", choices=["conceal", "reveal"], required=True, help="The mode selected, between hide data in an image, or fetch data from an image.")
    parser.add_argument("-i", "--input", dest="input", required=True, help="The image to begin the script from.")

    parser.add_argument("-t", "--type", dest="type", choices=["text", "file"], default="file", help="[conceal mode] The type of data to hide inside.")
    parser.add_argument("-c", "--conceal_mode", dest="conceal_mode", choices=CONCEAL_MODS, default="simple", help="[conceal mode] How the data will be concealed in the image.")

    parser.add_argument("-o", "--output", dest="output", default='output/concealed' if "conceal" in sys.argv else 'output/revealed', help="The output filename.")
    parser.add_argument("-v", "--verbose", dest="verbose", action="store_true", default=False, help="Verbosity to display modified pixels and error logs")
    parser.add_argument("-vv", "--vverbose", dest="vverbose", action="store_true", default=False, help="Verbosity for debugging purpose, enable image modification GUI (slow)")


    args, unknownargs = parser.parse_known_args()
    args = vars(args)

    if not os.path.exists(args["input"]):
        logging.error("Input file does not exist.")
        exit()

    if not os.path.exists("output"):
        os.makedirs("output")

    if args["vverbose"]:
        args["verbose"] = True

    if args["vverbose"]:
        args["verbose"] = True

    # Hide data in a given image
    if args["mode"] == "conceal":
        if args["type"] == "text" and len(unknownargs) == 0:
            logging.error("No text has been provided. Please add your text as an argument call.")
            exit()
        elif args["type"] == "file" and len(unknownargs) == 0:
            logging.error("No filepath has been provided. Please add your file as an argument call.")
            exit()

        if not args["output"].endswith(".png"):
            args["output"] += ".png"

        # get the data as bytes
        if args["type"] == "text":
            data = unknownargs[0].encode("utf8")
        else:
            print("Reading file...", end="", flush=True)
            with open(unknownargs[0], "rb") as f:
                data = f.read()
            print(" done.")

        # remove the output image if exists
        if os.path.exists(args["output"]):
            os.remove(args["output"])

        generated_filepath = data_to_image(data, args["type"] == "file", args["input"], args["output"], args["conceal_mode"], verbose=args["verbose"] + args["vverbose"])
        generated_filepath = data_to_image(data, args["type"] == "file", args["input"], args["output"], args["conceal_mode"], verbose=args["verbose"] + args["vverbose"])
        print("New image generated:", generated_filepath)

    # Reveal the data from an image
    elif args["mode"] == "reveal":
        text_or_file = extract_data_from_image(args["input"], args["output"], verbose=args["verbose"] + args["vverbose"])
        text_or_file = extract_data_from_image(args["input"], args["output"], verbose=args["verbose"] + args["vverbose"])
        print("Data fetched:", text_or_file)