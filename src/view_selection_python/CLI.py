"""
While developing the tool, I will use manual calling of the main file through
the cli including args which specify the working directory to choose. Later,
when I get the actual tool ready for release, the user should do `vst command`
from the correct location. This correct location, is now given through the argument
in the cli.
"""

import argparse


def get_wd() -> str:
    """
    Return the working directory as specified in cli. Later, this working
    dir should be recognized automatically, as the user calls `vst command`
    from that location.
    """
    parser = argparse.ArgumentParser(
        prog='View Selection Tool',
        description='Advice on which models to materialize in dbt')

    parser.add_argument('-rwd', '--root_working_dir',
                        type=str,
                        help='The path to use as root working directory')

    args = parser.parse_args()

    return args.root_working_dir
