#!/usr/bin/env python

def main ():
    """
    The main function.
    """

    import argparse

    parser = argparse.ArgumentParser()

    parser.add_argument("INPUT",
            help = "The mediawiki input. One page per line.")

    options = parser.parse_args()

if __name__ == "__main__":
    main()
