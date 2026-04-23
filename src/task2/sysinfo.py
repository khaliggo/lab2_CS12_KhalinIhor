"""
Task 2: Collect system information based on CLI options.

Options:
  -o / --os          Operating system name
  -v / --version     Kernel version
  -p / --processor   CPU architecture
  -k / --kernels     Number of logical CPU cores
  -f / --file NAME   Write result to file instead of stdout

If no info-selection option is given, all four fields are collected.
"""

import argparse
import os
import platform
import sys


def _os_name():
    """Return the OS name (e.g. 'Linux')."""
    return platform.system()


def _kernel_version():
    """Return the kernel / OS release string."""
    return platform.release()


def _processor_arch():
    """Return the CPU architecture (e.g. 'x86_64')."""
    return platform.machine()


def _logical_cores():
    """Return the number of logical CPU cores as an int."""
    return os.cpu_count()


# Mapping: long-option-name -> collector function
_COLLECTORS = {
    "os":        _os_name,
    "version":   _kernel_version,
    "processor": _processor_arch,
    "kernels":   _logical_cores,
}


def build_parser():
    """Build and return the ArgumentParser.

    argparse was chosen because it is part of the stdlib, produces
    automatic --help, and gives clean attribute access to parsed values.
    """
    parser = argparse.ArgumentParser(
        description="Collect system information"
    )
    parser.add_argument(
        "-o", "--os",
        action="store_true",
        default=False,
        help="Include OS name",
    )
    parser.add_argument(
        "-v", "--version",
        action="store_true",
        default=False,
        help="Include kernel version",
    )
    parser.add_argument(
        "-p", "--processor",
        action="store_true",
        default=False,
        help="Include CPU architecture",
    )
    parser.add_argument(
        "-k", "--kernels",
        action="store_true",
        default=False,
        help="Include logical core count",
    )
    parser.add_argument(
        "-f", "--file",
        default=None,
        metavar="FILE_NAME",
        help="Write output to FILE_NAME instead of stdout",
    )
    return parser


def collect_sysinfo(argv=None):
    """Parse *argv* and return a (dict, file_path_or_None) tuple.

    Keys in the returned dict match the long option names:
    "os", "version", "processor", "kernels".

    If no info flag is given, all four keys are included.

    Args:
        argv: list of CLI argument strings (or None to use sys.argv[1:]).

    Returns:
        tuple[dict, str | None]: (info_dict, output_file_path_or_None)
    """
    parser = build_parser()
    args, _ = parser.parse_known_args(argv)

    selected = {key for key in _COLLECTORS if getattr(args, key)}

    # No flag given -> collect everything
    if not selected:
        selected = set(_COLLECTORS.keys())

    result = {
        key: _COLLECTORS[key]()
        for key in _COLLECTORS
        if key in selected
    }

    return result, args.file


def main(argv=None):
    """Run the utility: collect info and write to file or stdout."""
    info, output_file = collect_sysinfo(argv)
    text = str(info)

    if output_file:
        with open(output_file, "w", encoding="utf-8") as fh:
            fh.write(text + "\n")
        print(f"Result written to '{output_file}'")
    else:
        print(text)


if __name__ == "__main__":
    main(sys.argv[1:])
