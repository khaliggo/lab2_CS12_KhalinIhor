"""
Task 1: Determine config file path by priority:
  1. Command-line option  -c / --config
  2. Environment variable CONFIG_PATH
  3. Default value        ~/.config.yaml
"""

import argparse
import os
import sys


def get_config_path(argv=None):
    """
    Parse command-line arguments and environment to resolve the config path.

    Priority (highest → lowest):
      1. -c / --config CLI option
      2. CONFIG_PATH environment variable
      3. Default: ~/.config.yaml

    Args:
        argv: list of CLI args (defaults to sys.argv[1:]).
              Accepting it as a parameter makes the function easy to test
              without monkey-patching sys.argv.

    Returns:
        str: resolved path string (file existence is NOT checked).
    """
    # argparse was chosen because it is part of the stdlib, produces
    # automatic --help, and gives clean attribute access to parsed values.
    parser = argparse.ArgumentParser(
        description="Resolve configuration file path"
    )
    parser.add_argument(
        "-c", "--config",
        default=None,
        metavar="PATH",
        help="Path to the configuration file",
    )

    # parse_known_args lets the program ignore unrelated flags when tested
    # inside a larger pytest session that injects its own sys.argv entries.
    args, _ = parser.parse_known_args(argv)

    if args.config is not None:
        return args.config

    env_path = os.environ.get("CONFIG_PATH")
    if env_path is not None:
        return env_path

    return os.path.expanduser("~/.config.yaml")


if __name__ == "__main__":
    print(get_config_path(sys.argv[1:]))
