"""
Tests for task1/config_path.py

Monkey-patching strategies used:
  - monkeypatch.setattr(sys, 'argv', [...])  -- simulate CLI arguments
  - monkeypatch.setenv / monkeypatch.delenv  -- simulate env variables
"""

import os
import sys
from pathlib import Path
import importlib.util

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC_DIR))

try:
    from task1.config_path import get_config_path  # noqa: E402
except ModuleNotFoundError:
    # Fallback import by file path for environments where package discovery
    # differs (e.g., direct test invocation from nested directories).
    module_path = SRC_DIR / "task1" / "config_path.py"
    spec = importlib.util.spec_from_file_location(
        "task1_config_path", module_path
         )
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load module from {module_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    get_config_path = module.get_config_path


def _strip_env(monkeypatch):
    """Remove CONFIG_PATH so tests don't interfere with each other."""
    monkeypatch.delenv("CONFIG_PATH", raising=False)


# ------------------------------------------------------------------ #
# Priority 3 - default value                                          #
# ------------------------------------------------------------------ #

class TestDefaultValue:
    """When neither CLI arg nor env var is present, use ~/.config.yaml."""

    def test_returns_default(self, monkeypatch):
        _strip_env(monkeypatch)
        result = get_config_path([])
        assert result == os.path.expanduser("~/.config.yaml")

    def test_default_ends_with_config_yaml(self, monkeypatch):
        _strip_env(monkeypatch)
        assert get_config_path([]).endswith(".config.yaml")

    def test_default_has_no_tilde(self, monkeypatch):
        _strip_env(monkeypatch)
        assert not get_config_path([]).startswith("~")


# ------------------------------------------------------------------ #
# Priority 2 - environment variable                                   #
# ------------------------------------------------------------------ #

class TestEnvVar:
    """CONFIG_PATH env var overrides the default."""

    def test_env_var_used_when_set(self, monkeypatch):
        monkeypatch.setenv("CONFIG_PATH", "/tmp/from_env.yaml")
        assert get_config_path([]) == "/tmp/from_env.yaml"

    def test_env_var_arbitrary_path(self, monkeypatch):
        monkeypatch.setenv("CONFIG_PATH", "/etc/myapp/settings.yml")
        assert get_config_path([]) == "/etc/myapp/settings.yml"

    def test_env_var_relative_path(self, monkeypatch):
        monkeypatch.setenv("CONFIG_PATH", "relative/path.yaml")
        assert get_config_path([]) == "relative/path.yaml"

    def test_env_var_empty_string_is_used(self, monkeypatch):
        monkeypatch.setenv("CONFIG_PATH", "")
        assert get_config_path([]) == ""

    def test_env_var_cleared_falls_back_to_default(self, monkeypatch):
        monkeypatch.setenv("CONFIG_PATH", "/some/path.yaml")
        monkeypatch.delenv("CONFIG_PATH")
        assert get_config_path([]) == os.path.expanduser("~/.config.yaml")


# ------------------------------------------------------------------ #
# Priority 1 - CLI option                                             #
# ------------------------------------------------------------------ #

class TestCliOption:
    """The -c / --config option has the highest priority."""

    def test_short_option_c(self, monkeypatch):
        _strip_env(monkeypatch)
        assert get_config_path(["-c", "/cli/short.yaml"]) == "/cli/short.yaml"

    def test_long_option_config(self, monkeypatch):
        _strip_env(monkeypatch)
        result = get_config_path(["--config", "/cli/long.yaml"])
        assert result == "/cli/long.yaml"

    def test_cli_overrides_env_var(self, monkeypatch):
        monkeypatch.setenv("CONFIG_PATH", "/env/path.yaml")
        assert get_config_path(["-c", "/cli/wins.yaml"]) == "/cli/wins.yaml"

    def test_cli_overrides_default(self, monkeypatch):
        _strip_env(monkeypatch)
        result = get_config_path(["--config", "/explicit/config.yaml"])
        assert result == "/explicit/config.yaml"

    def test_cli_path_preserved_exactly(self, monkeypatch):
        _strip_env(monkeypatch)
        path = "/some/unusual/../path.yaml"
        assert get_config_path(["-c", path]) == path


# ------------------------------------------------------------------ #
# sys.argv monkeypatch pattern (as shown in course examples)          #
# ------------------------------------------------------------------ #

class TestSysArgvMonkeypatch:
    """Demonstrate the sys.argv monkeypatch pattern."""

    def test_no_args_via_sys_argv(self, monkeypatch):
        monkeypatch.setattr(sys, "argv", ["script.py"])
        _strip_env(monkeypatch)
        result = get_config_path(None)
        assert result == os.path.expanduser("~/.config.yaml")

    def test_short_opt_via_sys_argv(self, monkeypatch):
        monkeypatch.setattr(sys, "argv", ["script.py", "-c", "/argv.yaml"])
        _strip_env(monkeypatch)
        assert get_config_path(None) == "/argv.yaml"

    def test_long_opt_via_sys_argv(self, monkeypatch):
        monkeypatch.setattr(
            sys, "argv", ["script.py", "--config", "/long/argv.yaml"]
        )
        _strip_env(monkeypatch)
        assert get_config_path(None) == "/long/argv.yaml"

    def test_env_via_sys_argv_session(self, monkeypatch):
        monkeypatch.setattr(sys, "argv", ["script.py"])
        monkeypatch.setenv("CONFIG_PATH", "/env/via_argv_test.yaml")
        assert get_config_path(None) == "/env/via_argv_test.yaml"
