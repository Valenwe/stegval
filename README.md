# stegval
 Simple steganography project to hide data inside images.
 Warning, this prototype is not fitted for high amount of data, its purpose is to show how to hide small amount of data.

# Usage

```
 _______________________ _______         _______ _
(  ____ \__   __(  ____ (  ____ \     /(  ___  | \
| (    \/  ) (  | (    \/ (    \/ )   ( | (   ) | (
| (_____   | |  | (__   | |     | |   | | (___) | |
(_____  )  | |  |  __)  | | ____( (   ) )  ___  | |
      ) |  | |  | (     | | \_  )\ \_/ /| (   ) | |
/\____) |  | |  | (____/\ (___) | \   / | )   ( | (____/\ v1.1 by Valenwe
\_______)  )_(  (_______(_______)  \_/  |/     \(_______/

usage: StegaVal [-h] -m {conceal,reveal} -i INPUT [-t {text,file}] [-c {simple,square}] [-o OUTPUT] [-v]

options:
  -h, --help            show this help message and exit
  -m {conceal,reveal}, --mode {conceal,reveal}
                        The mode selected, between hide data in an image, or fetch data from an image.
  -i INPUT, --input INPUT
                        The image to begin the script from.
  -t {text,file}, --type {text,file}
                        [conceal mode] The type of data to hide inside.
  -c {simple,square}, --conceal_mode {simple,square}
                        [conceal mode] How the data will be concealed in the image.
  -o OUTPUT, --output OUTPUT
                        The output filename.
  -v, --verbose         Verbosity for debugging purpose
  ```

  # Examples

- `python .\main.py -m conceal -i fig.jpg -t file vic.png` : from file `fig.jpg`, hide the data of the `vic.png` file inside.
- `python .\main.py -m reveal -i output_image.png` : from file `output_image.png`, find the concealed data.
- `python .\main.py -m conceal -i fig.png -c square` : from file `fig.jpg`, hide the data of the `vic.png` file inside as a square starting from the center.