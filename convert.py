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

    pandoc_cmd = [ "pandoc", "--from", "mediawiki", "--to", "markdown_github",
            "--base-header-level", "2" ]
    for line in fd:
        page = line.split(maxsplit=1)
        if len(page) < 2:
            continue
        page_title = page[0]
        page_text = page[1]
        page_title = re.sub(" ", "_", page_title)
        page_text = page_text.split("\\n")
        pandoc = subprocess.Popen( pandoc_cmd, stdin=subprocess.PIPE,
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                universal_newlines=True)
        for i in page_text:
            pandoc.stdin.write(i + "\n")
        stdout_lines, stderr_lines = pandoc.communicate()

        new_page = open(os.path.join("./pages", page_title + ".md"), "w")
        new_page.write("---\n")
        new_page.write("layout: default\n")
        new_page.write("title: %s\n" % (re.sub("_", " ", page_title)))
        new_page.write("---\n")
        new_page.write("\n")

        for i in stdout_lines.splitlines():
            new_page.write(i + "\n")
        new_page.close()

    fd.close()

if __name__ == "__main__":
    main()
