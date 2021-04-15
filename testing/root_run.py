import pytest
import argparse


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Lorem Ipsum')
    parser.add_argument('-a', '--run-all',
                        help='Run all tests. By default, markers in ./pytest.ini are used.',
                        required=False,
                        action='store_true')
    args = parser.parse_args()

    if args.run_all:
        pytest.main(["-c", "pytest-run-all.ini"])
    else:
        pytest.main(["-c", "pytest.ini"])
