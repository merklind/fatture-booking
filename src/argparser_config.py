from argparse import ArgumentParser, Namespace


def setup_parser() -> Namespace:
    parser = ArgumentParser(description="Script to edit Booking invoice")
    parser.add_argument("filename", help="Filename of the root folder containing Booking invoice")
    parsed_arg = parser.parse_args()

    return parsed_arg
