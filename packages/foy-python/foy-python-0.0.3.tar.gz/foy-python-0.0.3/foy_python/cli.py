import argparse
import logging
from foy_python import check_pypi_for_updates
from foy_python import requirements_parser


def main():
    parser = argparse.ArgumentParser("Fountain of Youth's python handler for Pypi packages")
    parser.add_argument('-R', '--requirements', dest="file", help="""Get packages and versions from requirements.txt file.
        Usage foy.python -R <file_path>""")
    parser.add_argument('-C', '--check', dest="package", help="""Get some package's latest avaliable version.
        Usage foy.python -V <package_name>""")

    args = parser.parse_args()
    if args.file:
        requirements_parser(args.file)
    if args.package:
        check_pypi_for_updates(args.package)

def get_logger(log_path):
    handler = logging.StreamHandler() if log_path is None else logging.FileHandler(log_path)
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    handler.setFormatter(formatter)
    logger = logging.getLogger("foy_python")
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)
    return logger


if __name__  == '__main__':
    main()