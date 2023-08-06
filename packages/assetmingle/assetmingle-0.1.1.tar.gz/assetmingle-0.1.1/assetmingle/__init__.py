"""Usage: assetmingle [-hvo] [--root=<path>] [INPUT ...]

Options:
    -root=<path> The directory where your images or assets can be referenced from.
    -o           Output everything to standard out
    -h --help    Show this screen.
    -v           Be verbose.

"""

import fileinput
import docopt
import mimetypes
import base64
import os
import re
import sys

def base64encode_url(filename):
    """Generates a Data URL with the base64 encoded contents of the passed file
    """
    encoded_file = None

    if os.path.exists(filename):
        mime_type, encoding = mimetypes.guess_type(filename)

        if not mime_type is None:
            with open(filename) as f:
                encoded_file = 'data:%s;base64,%s' % (mime_type, base64.b64encode(f.read()))

    return encoded_file

def encode_assets(filename, anchor, base_dir=None):
    """Returns a dictionary containing filenames and Data URLs for each file
    """
    assets = {}
    regex = re.compile('[\'\"]([^\'\"]+)#%s[\'\"]' % anchor)

    with open(filename) as f:
        for match in regex.finditer(f.read(), re.M):
            url = match.group(1)

            if url.startswith('/'):
                url = url[1:]

            assets[url] = base64encode_url(os.path.join(base_dir, url))

    return assets

def cli_main():
    arguments = docopt.docopt(__doc__, version='assetmingle 0.1.1')

    files = arguments['INPUT']
    root = arguments['--root']
    verbose = arguments['-v']
    stdout = arguments['-o']

    for filename in files:
        base_path = os.path.dirname(filename) if root is None else root
        assets = encode_assets(filename, 'mingle', base_dir=base_path)

        for asset in assets.keys():
            if assets[asset] is None:
                if verbose:
                    print >>sys.stderr, 'WARNING: Could not encode/open %s. Skipping...' % asset
                del assets[asset]

        for line in fileinput.input(filename, inplace=not stdout):
            for asset, encoded_value in assets.iteritems():
                line = line.replace(asset + '#mingle', encoded_value)

            print line,
