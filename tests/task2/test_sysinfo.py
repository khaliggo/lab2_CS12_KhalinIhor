"""
Tests for task2/sysinfo.py

Monkey-patching strategies:
  - monkeypatch.setattr(sys, 'argv', [...])  -- simulate CLI arguments
  - monkeypatch.setattr on collector fns    -- isolate from real hardware
"""

import os
import sys
from pathlib import Path
import importlib.util

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC_DIR))

try:
    from task2.sysinfo import collect_sysinfo  # noqa: E402
except ModuleNotFoundError:
    # Fallback import by file path for environments where package discovery
    # differs (e.g., direct script execution from nested directories).
    module_path = SRC_DIR / "task2" / "sysinfo.py"
    spec = importlib.util.spec_from_file_location("task2_sysinfo", module_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load module from {module_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    collect_sysinfo = module.collect_sysinfo


FAKE_INFO = {
    "os":        "TestOS",
    "version":   "9.9.9-test",
    "processor": "test_arch",
    "kernels":   8,
}


@pytest.fixture()
def patch_collectors(monkeypatch):
    """Replace all collector functions with deterministic fakes."""
    import task2.sysinfo as m
    monkeypatch.setattr(m, "_os_name", lambda: FAKE_INFO["os"])
    monkeypatch.setattr(m, "_kernel_version", lambda: FAKE_INFO["version"])
    monkeypatch.setattr(m, "_processor_arch", lambda: FAKE_INFO["processor"])
    monkeypatch.setattr(m, "_logical_cores", lambda: FAKE_INFO["kernels"])
    monkeypatch.setattr(
        m,
        "_COLLECTORS",
        {
            "os":        m._os_name,
            "version":   m._kernel_version,
            "processor": m._processor_arch,
            "kernels":   m._logical_cores,
        },
    )


# ------------------------------------------------------------------ #
# No options -> full info                                             #
# ------------------------------------------------------------------ #

class TestNoOptions:
    def test_all_keys_present(self, patch_collectors):
        info, _ = collect_sysinfo([])
        assert set(info.keys()) == {"os", "version", "processor", "kernels"}

    def test_all_values_match_fakes(self, patch_collectors):
        info, _ = collect_sysinfo([])
        assert info == FAKE_INFO

    def test_file_is_none_when_not_specified(self, patch_collectors):
        _, file_path = collect_sysinfo([])
        assert file_path is None


# ------------------------------------------------------------------ #
# Individual info flags                                               #
# ------------------------------------------------------------------ #

class TestSingleFlags:
    def test_os_flag_short(self, patch_collectors):
        info, _ = collect_sysinfo(["-o"])
        assert info == {"os": FAKE_INFO["os"]}

    def test_os_flag_long(self, patch_collectors):
        info, _ = collect_sysinfo(["--os"])
        assert info == {"os": FAKE_INFO["os"]}

    def test_version_flag_short(self, patch_collectors):
        info, _ = collect_sysinfo(["-v"])
        assert info == {"version": FAKE_INFO["version"]}

    def test_version_flag_long(self, patch_collectors):
        info, _ = collect_sysinfo(["--version"])
        assert info == {"version": FAKE_INFO["version"]}

    def test_processor_flag_short(self, patch_collectors):
        info, _ = collect_sysinfo(["-p"])
        assert info == {"processor": FAKE_INFO["processor"]}

    def test_processor_flag_long(self, patch_collectors):
        info, _ = collect_sysinfo(["--processor"])
        assert info == {"processor": FAKE_INFO["processor"]}

    def test_kernels_flag_short(self, patch_collectors):
        info, _ = collect_sysinfo(["-k"])
        assert info == {"kernels": FAKE_INFO["kernels"]}

    def test_kernels_flag_long(self, patch_collectors):
        info, _ = collect_sysinfo(["--kernels"])
        assert info == {"kernels": FAKE_INFO["kernels"]}


# ------------------------------------------------------------------ #
# Multiple info flags                                                 #
# ------------------------------------------------------------------ #

class TestMultipleFlags:
    def test_os_and_version(self, patch_collectors):
        info, _ = collect_sysinfo(["-o", "-v"])
        assert set(info.keys()) == {"os", "version"}

    def test_processor_and_kernels(self, patch_collectors):
        info, _ = collect_sysinfo(["-p", "-k"])
        assert set(info.keys()) == {"processor", "kernels"}

    def test_three_flags(self, patch_collectors):
        info, _ = collect_sysinfo(["-o", "-v", "-p"])
        assert set(info.keys()) == {"os", "version", "processor"}

    def test_all_four_flags_explicit(self, patch_collectors):
        info, _ = collect_sysinfo(["-o", "-v", "-p", "-k"])
        assert info == FAKE_INFO


# ------------------------------------------------------------------ #
# File output option                                                  #
# ------------------------------------------------------------------ #

class TestFileOption:
    def test_short_f_returns_filename(self, patch_collectors):
        _, fp = collect_sysinfo(["-f", "out.txt"])
        assert fp == "out.txt"

    def test_long_file_returns_filename(self, patch_collectors):
        _, fp = collect_sysinfo(["--file", "result.txt"])
        assert fp == "result.txt"

    def test_file_with_info_flag(self, patch_collectors):
        info, fp = collect_sysinfo(["-o", "-f", "os_info.txt"])
        assert info == {"os": FAKE_INFO["os"]}
        assert fp == "os_info.txt"

    def test_main_writes_file(self, tmp_path, patch_collectors):
        from task2.sysinfo import main
        out_file = str(tmp_path / "sysinfo_out.txt")
        main(["-o", "-f", out_file])
        assert os.path.exists(out_file)
        content = open(out_file).read()
        assert "os" in content
        assert FAKE_INFO["os"] in content

    def test_no_file_option_returns_none(self, patch_collectors):
        _, fp = collect_sysinfo(["-o"])
        assert fp is None


# ------------------------------------------------------------------ #
# sys.argv monkeypatch pattern (as in course examples)               #
# ------------------------------------------------------------------ #

class TestSysArgvMonkeypatch:
    def test_no_argv_gives_full_info(self, monkeypatch, patch_collectors):
        monkeypatch.setattr(sys, "argv", ["sysinfo.py"])
        info, _ = collect_sysinfo(None)
        assert set(info.keys()) == {"os", "version", "processor", "kernels"}

    def test_os_flag_via_sys_argv(self, monkeypatch, patch_collectors):
        monkeypatch.setattr(sys, "argv", ["sysinfo.py", "--os"])
        info, _ = collect_sysinfo(None)
        assert list(info.keys()) == ["os"]

    def test_file_via_sys_argv(self, monkeypatch, tmp_path, patch_collectors):
        out = str(tmp_path / "argv_test.txt")
        monkeypatch.setattr(sys, "argv", ["sysinfo.py", "-k", "-f", out])
        from task2.sysinfo import main
        main(None)
        assert os.path.exists(out)


# ------------------------------------------------------------------ #
# Keys in result match long option names (spec requirement)           #
# ------------------------------------------------------------------ #

class TestKeyNames:
    def test_keys_match_long_option_names(self, patch_collectors):
        info, _ = collect_sysinfo(["-o", "-v", "-p", "-k"])
        assert "os" in info
        assert "version" in info
        assert "processor" in info
        assert "kernels" in info

    def test_no_file_key_in_info_dict(self, patch_collectors):
        info, _ = collect_sysinfo(["-f", "x.txt"])
        assert "file" not in info


# ------------------------------------------------------------------ #
# Real hardware sanity checks (no monkeypatching)                    #
# ------------------------------------------------------------------ #

class TestRealHardware:
    def test_os_is_non_empty_string(self):
        info, _ = collect_sysinfo(["-o"])
        assert isinstance(info["os"], str) and len(info["os"]) > 0

    def test_version_is_string(self):
        info, _ = collect_sysinfo(["-v"])
        assert isinstance(info["version"], str)

    def test_processor_is_string(self):
        info, _ = collect_sysinfo(["-p"])
        assert isinstance(info["processor"], str)

    def test_kernels_is_positive_int(self):
        info, _ = collect_sysinfo(["-k"])
        assert isinstance(info["kernels"], int)
        assert info["kernels"] >= 1
