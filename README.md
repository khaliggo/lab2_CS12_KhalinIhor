# Operating Systems Lab 2 - Process Environment Utilities

## About Project

This project was created for Operating Systems Laboratory Work #2, "Program
Environment of a Process". The laboratory work focuses on the standard ways a
Linux process receives data from its environment and returns results:

- command-line arguments;
- short and long command-line options;
- environment variables;
- basic system parameter detection;
- output through stdout or through a file;
- automated checking with `pytest`;
- code quality checking with `flake8`.

The main educational goal of the lab is to practice how a program communicates
with its process environment. In Linux, every process can receive configuration
from several sources: arguments passed during startup, environment variables
inherited from the parent process, and values hardcoded as defaults. This
project demonstrates those mechanisms in two independent Python utilities.

The laboratory assignment contains two tasks.

Task 1 asks for a Python program that returns a configuration file path. The
path must be chosen by a strict priority order:

1. command-line option `-c` or `--config`;
2. environment variable `CONFIG_PATH`;
3. default value `~/.config.yaml`.

The program must return only the path string. It must not check whether the file
really exists. This is important because the task is about resolving a value from
the process environment, not about validating a filesystem object.

Task 2 asks for a Python utility that collects system information depending on
the options selected by the user. The utility can collect:

- operating system name with `-o` or `--os`;
- kernel or OS release version with `-v` or `--version`;
- processor architecture with `-p` or `--processor`;
- number of logical CPU cores with `-k` or `--kernels`.

The result must be represented as a Python dictionary. The dictionary keys must
match the long option names: `os`, `version`, `processor`, and `kernels`. If the
user does not pass any information-selection option, the program must collect
all available fields. If the user passes `-f FILE_NAME` or `--file FILE_NAME`,
the dictionary is written to that file as text. Otherwise, the dictionary is
printed to standard output.

The project also includes automated tests. The tests use `pytest` and the
`monkeypatch` fixture to imitate different command-line arguments, environment
variables, and system information. This matches the lab requirement to test the
programs without depending only on the real current shell or the real current
machine.

## About Code

The project is organized into source files and test files:

```text
lab2_CS12_KhalinIhor/
|-- README.md
|-- src/
|   |-- task1/
|   |   `-- config_path.py
|   `-- task2/
|       `-- sysinfo.py
`-- tests/
    |-- task1/
    |   `-- test_config_path.py
    `-- task2/
        `-- test_sysinfo.py
```

The implementation uses only Python standard library modules in the runtime
code:

- `argparse` for command-line parsing;
- `os` for environment variables and CPU count;
- `platform` for operating system, kernel, and architecture information;
- `sys` for reading command-line arguments when the scripts are run directly.

The project uses `argparse` for option parsing because it is included in the
Python standard library, supports both short and long options, generates useful
`--help` output automatically, and returns parsed arguments in a convenient
object. This makes the code simple, readable, and appropriate for a laboratory
assignment about command-line interfaces.

The code is written in a testable style. The main logic is inside functions that
accept an optional `argv` argument. This allows the tests to pass artificial
argument lists directly, for example `["-c", "/tmp/config.yaml"]`, instead of
needing to launch a separate process. When `argv` is `None`, `argparse` reads the
real `sys.argv[1:]`, which is the normal behavior when a user runs the script
from a terminal.

### Source File: `src/task1/config_path.py`

This file implements Task 1. Its main function is:

```python
get_config_path(argv=None)
```

The function resolves a configuration path from three possible sources. It does
not open the file, normalize the path, check permissions, or verify that the
path exists. It only decides which string should be used according to priority.

Important parts of the file:

- module docstring: describes the priority order required by the lab;
- imports: `argparse`, `os`, and `sys`;
- `get_config_path`: parses arguments, checks the environment, and returns a
  string;
- `if __name__ == "__main__"` block: allows the file to work as a standalone
  command-line program.

The command-line interface for this task supports:

```text
-c PATH
--config PATH
```

Examples:

```bash
python3 src/task1/config_path.py
python3 src/task1/config_path.py -c /tmp/app.yaml
python3 src/task1/config_path.py --config /etc/myapp/config.yml
CONFIG_PATH=/opt/project/config.yaml python3 src/task1/config_path.py
```

### Source File: `src/task2/sysinfo.py`

This file implements Task 2. It contains small collector functions, a parser
builder, the main collection function, and a command-line entry point.

Main public functions:

```python
build_parser()
collect_sysinfo(argv=None)
main(argv=None)
```

Internal collector functions:

```python
_os_name()
_kernel_version()
_processor_arch()
_logical_cores()
```

The collector functions isolate the system-specific calls. This makes the code
easier to read and easier to test. Tests can replace these collectors with fake
functions and check the command-line logic without depending on the real
operating system or CPU of the test machine.

The `_COLLECTORS` dictionary connects option names to functions:

```python
{
    "os": _os_name,
    "version": _kernel_version,
    "processor": _processor_arch,
    "kernels": _logical_cores,
}
```

This mapping is the central design idea of Task 2. It avoids repeated `if`
blocks for every field. The same keys are used as:

- long option names;
- attributes created by `argparse`;
- keys in the final result dictionary;
- keys expected by the tests.

The command-line interface for this task supports:

```text
-o, --os          include operating system name
-v, --version     include kernel or OS release version
-p, --processor   include CPU architecture
-k, --kernels     include logical CPU core count
-f, --file FILE   write result to FILE instead of stdout
```

Examples:

```bash
python3 src/task2/sysinfo.py
python3 src/task2/sysinfo.py -o
python3 src/task2/sysinfo.py --os --version
python3 src/task2/sysinfo.py -p -k
python3 src/task2/sysinfo.py -o -v -p -k
python3 src/task2/sysinfo.py -o -f os_info.txt
python3 src/task2/sysinfo.py --processor --kernels --file cpu_info.txt
```

### Test Files

The tests are located in `tests/task1/` and `tests/task2/`.

`tests/task1/test_config_path.py` checks:

- default path behavior;
- use of `CONFIG_PATH`;
- use of short option `-c`;
- use of long option `--config`;
- priority of command-line options over environment variables;
- fallback to default after the environment variable is removed;
- behavior when arguments are supplied through `sys.argv`;
- behavior when an empty environment variable value is present.

`tests/task2/test_sysinfo.py` checks:

- default full dictionary when no information options are selected;
- every short and long information option;
- combinations of several options;
- output file option `-f` and `--file`;
- `main()` writing the dictionary into a file;
- `sys.argv` monkeypatching;
- result dictionary key names;
- sanity checks against the real machine.

To run the tests:

```bash
pytest
```

To run a style check, if `flake8` is installed:

```bash
flake8 src tests
```

## How Code Works Detailed

### Task 1 Detailed Flow: Configuration Path Resolution

The first script answers one question: which configuration file path should the
program use?

The function starts by creating an `ArgumentParser`:

```python
parser = argparse.ArgumentParser(
    description="Resolve configuration file path"
)
```

This parser describes the command-line interface. The description text is shown
when the user runs:

```bash
python3 src/task1/config_path.py --help
```

Then the script registers the configuration option:

```python
parser.add_argument(
    "-c", "--config",
    default=None,
    metavar="PATH",
    help="Path to the configuration file",
)
```

This means the user can pass either a short option or a long option:

```bash
python3 src/task1/config_path.py -c /tmp/config.yaml
python3 src/task1/config_path.py --config /tmp/config.yaml
```

Both forms produce the same parsed value: `args.config`.

The code then parses arguments with:

```python
args, _ = parser.parse_known_args(argv)
```

`parse_known_args` is used instead of `parse_args` so that unrelated arguments
do not break the function in testing or embedded execution contexts. For
example, `pytest` often adds its own command-line arguments. This function cares
only about `-c` and `--config`; unknown options are ignored.

After parsing, the priority algorithm begins.

First priority: command-line option.

```python
if args.config is not None:
    return args.config
```

If the user explicitly passed `-c` or `--config`, that value wins immediately.
The environment variable and default value are not checked after this point.
This follows the assignment requirement that command-line options have the
highest priority.

Example:

```bash
CONFIG_PATH=/env/config.yaml python3 src/task1/config_path.py -c /cli/config.yaml
```

Result:

```text
/cli/config.yaml
```

Second priority: environment variable.

```python
env_path = os.environ.get("CONFIG_PATH")
if env_path is not None:
    return env_path
```

If no command-line config option was given, the function looks for
`CONFIG_PATH`. `os.environ.get("CONFIG_PATH")` returns the value if it exists,
or `None` if it does not exist.

The code checks `is not None`, not truthiness. This means an empty string is
still considered a real environment value. The tests confirm this behavior:
when `CONFIG_PATH` is set to `""`, the function returns `""`.

Example:

```bash
CONFIG_PATH=/env/config.yaml python3 src/task1/config_path.py
```

Result:

```text
/env/config.yaml
```

Third priority: default value.

```python
return os.path.expanduser("~/.config.yaml")
```

If neither the command-line option nor the environment variable is present, the
function returns the default path. `os.path.expanduser` converts `~` into the
current user's home directory.

Example result:

```text
/home/ihor/.config.yaml
```

The exact home directory depends on the user account running the script.

When the file is executed directly, this block runs:

```python
if __name__ == "__main__":
    print(get_config_path(sys.argv[1:]))
```

`sys.argv[1:]` contains all command-line arguments after the script name. The
function returns the selected path, and `print` sends it to stdout.

Complete Task 1 decision table:

| Command-line option | `CONFIG_PATH` | Returned value |
| --- | --- | --- |
| present | present | command-line option value |
| present | absent | command-line option value |
| absent | present | `CONFIG_PATH` value |
| absent | absent | expanded `~/.config.yaml` |

### Task 2 Detailed Flow: System Information Collection

The second script builds a dictionary with selected system parameters.

The system-specific work is separated into four small functions:

```python
def _os_name():
    return platform.system()
```

This returns the operating system name, for example `Linux`.

```python
def _kernel_version():
    return platform.release()
```

This returns the kernel or operating system release string, for example a Linux
kernel version.

```python
def _processor_arch():
    return platform.machine()
```

This returns the processor architecture, for example `x86_64`.

```python
def _logical_cores():
    return os.cpu_count()
```

This returns the number of logical CPU cores visible to Python.

These functions are connected by `_COLLECTORS`:

```python
_COLLECTORS = {
    "os":        _os_name,
    "version":   _kernel_version,
    "processor": _processor_arch,
    "kernels":   _logical_cores,
}
```

The keys are intentionally the same strings that must appear in the result
dictionary. This keeps the implementation aligned with the lab requirement.

The parser is created in `build_parser()`:

```python
parser = argparse.ArgumentParser(
    description="Collect system information"
)
```

Then every supported option is added. The information options use
`action="store_true"`, which means the parsed value is `False` by default and
becomes `True` when the user includes the option.

For example:

```python
parser.add_argument(
    "-o", "--os",
    action="store_true",
    default=False,
    help="Include OS name",
)
```

If the user runs:

```bash
python3 src/task2/sysinfo.py -o
```

then `args.os` becomes `True`.

If the user does not include `-o` or `--os`, then `args.os` stays `False`.

The output file option is different:

```python
parser.add_argument(
    "-f", "--file",
    default=None,
    metavar="FILE_NAME",
    help="Write output to FILE_NAME instead of stdout",
)
```

This option accepts a value. If the user runs:

```bash
python3 src/task2/sysinfo.py -o -f result.txt
```

then `args.file` becomes `"result.txt"`.

The main logic starts in `collect_sysinfo(argv=None)`:

```python
parser = build_parser()
args, _ = parser.parse_known_args(argv)
```

As in Task 1, `parse_known_args` is used to parse the known options while
ignoring unrelated arguments. This is useful for tests and for execution inside
larger command-line environments.

Next, the function detects which information fields were selected:

```python
selected = {key for key in _COLLECTORS if getattr(args, key)}
```

This set comprehension loops through every key in `_COLLECTORS`:

- for key `"os"`, it checks `args.os`;
- for key `"version"`, it checks `args.version`;
- for key `"processor"`, it checks `args.processor`;
- for key `"kernels"`, it checks `args.kernels`.

Only keys whose parsed argument value is `True` are added to `selected`.

Example:

```bash
python3 src/task2/sysinfo.py -o -v
```

Selected set:

```python
{"os", "version"}
```

If the user does not select any information option, `selected` is empty. The lab
requires that this case should return full information. The code handles that
with:

```python
if not selected:
    selected = set(_COLLECTORS.keys())
```

So this command:

```bash
python3 src/task2/sysinfo.py
```

selects all fields:

```python
{"os", "version", "processor", "kernels"}
```

After the selected keys are known, the result dictionary is created:

```python
result = {
    key: _COLLECTORS[key]()
    for key in _COLLECTORS
    if key in selected
}
```

This dictionary comprehension loops through `_COLLECTORS` in its defined order.
For every selected key, it calls the matching collector function and stores the
returned value.

Example command:

```bash
python3 src/task2/sysinfo.py -o -p
```

Possible result:

```python
{"os": "Linux", "processor": "x86_64"}
```

The function returns two values:

```python
return result, args.file
```

The first value is the information dictionary. The second value is either the
file path from `-f` or `--file`, or `None` if no file output was requested.

The `file` option is not included in the dictionary. It controls where the
result goes, but it is not system information. The tests explicitly check that
`"file"` is not present in the returned info dictionary.

The `main(argv=None)` function is responsible for output:

```python
info, output_file = collect_sysinfo(argv)
text = str(info)
```

The dictionary is converted into a text representation with `str(info)`.

If the user provided an output file:

```python
if output_file:
    with open(output_file, "w", encoding="utf-8") as fh:
        fh.write(text + "\n")
    print(f"Result written to '{output_file}'")
```

The program writes the dictionary text into the file using UTF-8 encoding and
prints a confirmation message to stdout.

If no output file was provided:

```python
else:
    print(text)
```

The program prints the dictionary directly to stdout.

When the file is executed directly, this block runs:

```python
if __name__ == "__main__":
    main(sys.argv[1:])
```

That makes `sysinfo.py` usable as a terminal utility.

Complete Task 2 behavior table:

| Command | Meaning | Output destination |
| --- | --- | --- |
| `python3 src/task2/sysinfo.py` | collect all fields | stdout |
| `python3 src/task2/sysinfo.py -o` | collect OS name only | stdout |
| `python3 src/task2/sysinfo.py -v` | collect kernel version only | stdout |
| `python3 src/task2/sysinfo.py -p` | collect processor architecture only | stdout |
| `python3 src/task2/sysinfo.py -k` | collect logical core count only | stdout |
| `python3 src/task2/sysinfo.py -o -v` | collect OS name and version | stdout |
| `python3 src/task2/sysinfo.py -p -k -f cpu.txt` | collect CPU info | `cpu.txt` |
| `python3 src/task2/sysinfo.py --os --file os.txt` | collect OS name | `os.txt` |

### How The Tests Work

The tests are written with `pytest`. They are not only checking final output;
they also demonstrate how command-line programs can be tested without manually
typing commands in a terminal.

For Task 1, tests use:

```python
monkeypatch.setenv("CONFIG_PATH", "/tmp/from_env.yaml")
monkeypatch.delenv("CONFIG_PATH", raising=False)
monkeypatch.setattr(sys, "argv", ["script.py", "-c", "/argv.yaml"])
```

This allows the test suite to simulate different process environments:

- no environment variable;
- environment variable set;
- environment variable removed;
- command-line arguments passed directly to the function;
- command-line arguments read from `sys.argv`.

The Task 1 tests prove the priority order:

```text
CLI option -> CONFIG_PATH -> default path
```

For Task 2, tests use fake collectors:

```python
monkeypatch.setattr(m, "_os_name", lambda: FAKE_INFO["os"])
monkeypatch.setattr(m, "_kernel_version", lambda: FAKE_INFO["version"])
monkeypatch.setattr(m, "_processor_arch", lambda: FAKE_INFO["processor"])
monkeypatch.setattr(m, "_logical_cores", lambda: FAKE_INFO["kernels"])
```

This is useful because real system values differ from machine to machine. One
computer may have a different kernel version, CPU architecture, or number of
cores than another. By replacing the collector functions with deterministic fake
values, the tests can focus on checking the program logic.

The Task 2 tests also include real hardware sanity checks. These do not expect
specific values, but they verify that:

- OS name is a non-empty string;
- version is a string;
- processor architecture is a string;
- logical core count is a positive integer.

This combination gives good coverage: fake values check exact logic, while real
values confirm that the program can actually communicate with the current
system.

### Expected Usage Workflow

1. Run Task 1 to resolve a configuration path:

```bash
python3 src/task1/config_path.py
python3 src/task1/config_path.py --config /custom/config.yaml
CONFIG_PATH=/env/config.yaml python3 src/task1/config_path.py
```

2. Run Task 2 to collect system information:

```bash
python3 src/task2/sysinfo.py
python3 src/task2/sysinfo.py -o -v
python3 src/task2/sysinfo.py --processor --kernels
python3 src/task2/sysinfo.py -o -v -p -k -f full_sysinfo.txt
```

3. Run automated tests:

```bash
pytest
```

4. Run linting:

```bash
flake8 src tests
```

### Summary Of Program Logic

Task 1 demonstrates configuration priority. The script chooses the most explicit
value available. A command-line option is treated as the user's direct request,
so it has the highest priority. An environment variable is less direct but still
external configuration, so it has second priority. The default path is used only
when nothing else is provided.

Task 2 demonstrates option-based data collection. Each option enables one field
in the result dictionary. No selected fields means the user wants the default
full report. The output file option does not change what information is
collected; it only changes where the final dictionary is written.

Together, the two tasks show the core idea of Laboratory Work #2: a process does
not work in isolation. It receives arguments, reads environment variables,
inspects the operating system, and sends results either to stdout or to files.
