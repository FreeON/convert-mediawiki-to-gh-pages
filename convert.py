#!/usr/bin/env python

def main ():
    """
    The main function.
    """

    import argparse
    import os
    import re
    import subprocess
    import sys

    parser = argparse.ArgumentParser()

    parser.add_argument("INPUT",
            help = "The mediawiki input. One page per line.")

    options = parser.parse_args()

    os.mkdir("pages")

    fd = open(options.INPUT)

    pandoc_cmd = [ "pandoc", "--from", "mediawiki", "--to", "markdown" ]
    for line in fd:
        page = line.split(maxsplit=1)
        if len(page) < 2:
            continue
        page_title = page[0]
        page_text = page[1]
        page_title = re.sub(" ", "_", page_title)
        pandoc = subprocess.Popen( pandoc_cmd, stdin=subprocess.PIPE,
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                universal_newlines=True)
        pandoc.stdin.write(page_text)
        stdout_lines, stderr_lines = pandoc.communicate()

        new_page = open(os.path.join("./pages", page_title + ".markdown"), "w")
        for i in stdout_lines.splitlines():
            new_page.write(i)
        new_page.close()

    fd.close()

if __name__ == "__main__":
    main()
