import argparse
import os
import sys

def main():
    " Main command to dynconf cli"

    # Read args.
    parser = argparse.ArgumentParser(description="Dynamic configuration.")

    # Filename to replace.
    parser.add_argument('--filename', help="Filename to replace")
    parser.add_argument('--keep-file', help="Don't delete the original file.",
                        default=False, action='store_true')

    # Parse the arguments.
    args = parser.parse_args()

    if not args.keep_file:

        # Remove file.
        if os.path.exists(args.filename):
            os.unlink(args.filename)

        # Create fifo.
        os.mkfifo(args.filename)

    # Read content.
    content = sys.stdin.read()

    # Open to read.
    fd = os.open(args.filename, os.O_WRONLY)

    # Pass stdin to filename.
    os.write(fd, content)

    # Close the fifo.
    os.close(fd)

