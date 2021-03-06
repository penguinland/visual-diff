#!/usr/bin/env python3

import argparse
import numpy
import sys
import token
import tokenize

try:
    # To get the GUI to work, you'll need to be able to install the TK bindings
    # for PIL (in Ubuntu, it's the python3-pil.imagetk package). We put this in
    # a try block so that the non-GUI functionality will still work even if you
    # can't install this.
    import gui
    can_use_gui = True
except ImportError:
    can_use_gui = False


parser = argparse.ArgumentParser()
parser.add_argument("filename_a", help="File to analyze")
parser.add_argument("filename_b", nargs="?", help="Second file to analyze")
parser.add_argument("--gui", "-g", action="store_true",
                    help="Explore the results in a GUI")
parser.add_argument("--output_location", "-o", default="output.png",
                    help="Location of output image (default: output.png)")
args = parser.parse_args(sys.argv[1:])


def get_tokens(filename):
    with open(filename) as f:
        tokens = tokenize.generate_tokens(f.readline)
        # Ignore non-significant whitespace
        ignore_types = [token.NEWLINE, token.ENDMARKER, tokenize.NL,
                        tokenize.COMMENT]
        tokens = [tok for tok in tokens if tok.type not in ignore_types]
        f.seek(0)
        lines = [line.rstrip() for line in f.readlines()]

    # We treat all constants as identical to other constants of the same type.
    constant_types = (token.STRING, token.NUMBER)
    token_array = numpy.array(
            [tok.type if tok.type in constant_types else tok.string
             for tok in tokens])
    boundaries = [(tok.start, tok.end) for tok in tokens]
    return token_array, lines, boundaries


data_a = get_tokens(args.filename_a)
data_b = get_tokens(args.filename_b or args.filename_a)
tokens_a = data_a[0]
tokens_b = data_b[0]

matrix = numpy.zeros([len(tokens_a), len(tokens_b)], numpy.uint8)
for i, value in enumerate(tokens_a):
    matrix[i, :] = (tokens_b == value)

if args.gui:
    if can_use_gui:
        gui.launch(matrix, data_a, data_b)
    else:
        print("ERROR: Cannot load GUI. Try doing a `sudo apt-get install "
              "python3-pil.imagetk`. If that doesn't help, open a python3 "
              "shell, `import gui`, and see what's going wrong.")
        sys.exit(1)
else:
    # Only import matplotlib if we're going to use it. There's some weird
    # behavior on Macs in which matplotlib works fine on its own, and PIL works
    # fine on its own, but if you import matplotlib and then try *using* PIL for
    # the GUI, we have an uncaught NSException. Consequently, we don't import
    # matplotlib at the top of the file, and instead only import it if we're
    # actually going to use it.
    from matplotlib import pyplot

    # WARNING: Converting large arrays to images can take up so many resources
    # that your computer freezes. For example, on a 1000-line file with 10
    # tokens per line, we're generating a 100 megapixel image, and pyplot has
    # trouble with images that large. Do not try this with very large programs!
    pyplot.imsave(args.output_location, matrix)
