# stegval
 Simple steganography project to hide data inside images.

# Usage

```
 _______________________ _______         _______ _
(  ____ \__   __(  ____ (  ____ \     /(  ___  | \
| (    \/  ) (  | (    \/ (    \/ )   ( | (   ) | (
| (_____   | |  | (__   | |     | |   | | (___) | |
(_____  )  | |  |  __)  | | ____( (   ) )  ___  | |
      ) |  | |  | (     | | \_  )\ \_/ /| (   ) | |
/\____) |  | |  | (____/\ (___) | \   / | )   ( | (____/\ v1.0 by Valenwe
\_______)  )_(  (_______(_______)  \_/  |/     \(_______/
usage: StegaVal [-h] -m {conceal,reveal} -i INPUT [-t {text,file}] [-o OUTPUT] [-v]

options:
  -h, --help            show this help message and exit
  -m {conceal,reveal}, --mode {conceal,reveal}
                        The mode selected, between hide data in an image, or fetch data from an image.
  -i INPUT, --input INPUT
                        The image to begin the script from.
  -t {text,file}, --type {text,file}
                        [conceal mode] The type of data to hide inside.
  -o OUTPUT, --output OUTPUT
                        The output filename.
  -v, --verbose         Verbosity for debugging purpose
  ```

  # Examples

- `python .\main.py -m conceal -i fig.jpg -t file "vic.png"` : from file `fig.jpg`, hide the data of the `vic.png` file inside.
- `python .\main.py -m reveal -i output_image.png` : from file `output_image.png`, find the concealed data.