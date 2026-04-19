import io
import sys
from contextlib import redirect_stdout
from pathlib import Path

import pytest

from gool.log_clustering import Arguments, ErrorCode, main, main_cli, surrogate_non_printable

"""
this file contains tests for the gool main function, by running it on different files and with different options,
and comparing the output to expected files. It also contains some tests for error handling.
"""

data_dir_path = Path(__file__).parents[0] / "data"
output_dir_path = data_dir_path / "results"
input_dir_path = data_dir_path / "log"
cfg_path = data_dir_path / "drain3.ini"
cfg_path_baseline = data_dir_path / "drain3_compare_baseline.ini"
zookeeper_path_log = input_dir_path / "Zookeeper_2k.log"
apache_path_log = input_dir_path / "Apache_2k.log"


class TestMisc:
    def test_surrogate_non_printable(self) -> None:
        assert surrogate_non_printable("foo") == "foo"


def run_gool_on_file_and_check(
    logfile_paths: tuple[Path, ...],
    path_expected_output: Path,
    similarity: float | None = None,
    depth: int | None = None,
    line_filter: str | None = None,
    lex_order: bool = False,
    size_order: bool = False,
) -> bool:
    args = Arguments(
        logfile_paths=logfile_paths,
        cfg_file=cfg_path,
        raw=True,
    )
    if depth:
        args.tree_depth = depth
    if similarity:
        args.similarity_threshold = similarity
    if line_filter:
        args.filter = line_filter
    if lex_order:
        args.lex_order = True
    if size_order:
        args.size_order = True
    f = io.StringIO()
    with redirect_stdout(f):
        main(args)
    output = f.getvalue()
    expected = path_expected_output.read_text()
    return output == expected


def run_gool_on_file_from_cli_and_check(
    cmd_args: list[str],
    path_input: Path,
    path_expected_output: Path | None = None,
    return_code_expected: int = ErrorCode.NO_ERROR.value,
) -> None:
    # Save original argv
    original_argv = sys.argv.copy()
    try:
        # Set argv to simulate no arguments (just the script name)
        sys.argv = ["gool", "--raw", "--cfg_file", str(cfg_path), str(path_input), *cmd_args]
        f = io.StringIO()
        with redirect_stdout(f):
            ret = main_cli()
        assert ret == return_code_expected
        output = f.getvalue()
        if path_expected_output is not None:
            expected = path_expected_output.read_text()
            assert output == expected
    finally:
        # Restore original argv
        sys.argv = original_argv


def run_gool_on_file_from_cli_and_check_raise(cmd_args: list[str], error_code: int) -> None:
    # Save original argv
    original_argv = sys.argv.copy()
    try:
        # Set argv to simulate no arguments (just the script name)
        sys.argv = ["gool", "--raw", "--cfg_file", str(cfg_path), *cmd_args]
        with pytest.raises(SystemExit) as exec_info:
            main_cli()
        assert exec_info.value.code == error_code

    finally:
        # Restore original argv
        sys.argv = original_argv


class TestNormalOutput:
    """Tests the normal output of gool on different files and with different options, by comparing the raw output to expected files."""

    def test_zookeeper_2k_output(self) -> None:
        """Test the raw output for Zookeeper_2k.log matches the expected file."""
        input_paths_tuple = (zookeeper_path_log,)
        expected_path = output_dir_path / "Zookeeper_2k_raw_output.txt"
        assert run_gool_on_file_and_check(input_paths_tuple, expected_path)

    def test_apache_2k_output(self) -> None:
        """Test the raw output for Zookeeper_2k.log matches the expected file."""
        input_paths_tuple = (apache_path_log,)
        expected_path = output_dir_path / "Apache_2k_raw_output.txt"
        assert run_gool_on_file_and_check(input_paths_tuple, expected_path)

    def test_6times_zookeeper_2k_output(self) -> None:
        """Test several files in input"""
        input_paths_tuple = (zookeeper_path_log,) * 6
        expected_path = output_dir_path / "6times_Zookeeper_2k_raw_output.txt"
        assert run_gool_on_file_and_check(input_paths_tuple, expected_path)

    def test_zookeeper_2k_output_similarity_5(self) -> None:
        """Test manually setting similarity threshold to 0.5."""
        input_paths_tuple = (zookeeper_path_log,)
        expected_path = output_dir_path / "Zookeeper_2k_sim_thres_5.txt"
        assert run_gool_on_file_and_check(input_paths_tuple, expected_path, similarity=0.5)

    def test_zookeeper_2k_output_depth_10(self) -> None:
        """Test manually setting depth to 10."""
        input_paths_tuple = (zookeeper_path_log,)
        expected_path = output_dir_path / "Zookeeper_2k_depth10.txt"
        assert run_gool_on_file_and_check(input_paths_tuple, expected_path, depth=10)

    def test_zookeeper_2k_output_filter_warn(self) -> None:
        """Test manually setting warn filter."""
        input_paths_tuple = (zookeeper_path_log,)
        expected_path = output_dir_path / "Zookeeper_2k_warn.txt"
        assert run_gool_on_file_and_check(input_paths_tuple, expected_path, line_filter=".*WARN.*")

    def test_zookeeper_2k_output_lex_order(self) -> None:
        """Test manually setting lex order."""
        input_paths_tuple = (zookeeper_path_log,)
        expected_path = output_dir_path / "Zookeeper_2k_lex_order.txt"
        assert run_gool_on_file_and_check(input_paths_tuple, expected_path, lex_order=True)

    def test_zookeeper_2k_output_size_order(self) -> None:
        """Test manually setting size order."""
        input_paths_tuple = (zookeeper_path_log,)
        expected_path = output_dir_path / "Zookeeper_2k_size_order.txt"
        assert run_gool_on_file_and_check(input_paths_tuple, expected_path, size_order=True)

    def test_apache_2k_output_time_filter(self) -> None:
        """Test manually setting time filter."""
        expected_path = output_dir_path / "Apache_2k_time_filter.txt"
        cmd = ["--time-min", "18:46:00", "--time-max", "19:00:00", "--filter", ".*Mon Dec 05.*"]
        run_gool_on_file_from_cli_and_check(cmd, apache_path_log, expected_path)

    def test_apache_2k_output_time_filter_custom_time(self) -> None:
        """Test manually setting time filter."""
        expected_path = output_dir_path / "Apache_2k_time_filter.txt"
        cmd = [
            "--time_format",
            "%a %b %d %H:%M:%S %Y",
            "--time_pattern",
            "(\\w{3} \\w{3} \\d{2} \\d{2}:\\d{2}:\\d{2} \\d{4})",
            "--time_min",
            "Mon Dec 05 18:46:00 2005",
            "--time_max",
            "Mon Dec 05 19:00:00 2005",
        ]
        run_gool_on_file_from_cli_and_check(cmd, apache_path_log, expected_path)

    def test_apache_2k_compare_baseline(self) -> None:
        """Test manually setting time filter."""
        expected_path = output_dir_path / "Apache_2K_baseline_compare.txt"
        apache_mon_dec_05 = input_dir_path / "Apache_2K_MonDec05.log"
        apache_sun_dec_04 = input_dir_path / "Apache_2K_SunDec04.log"
        cmd = [
            "--cfg-file",
            str(cfg_path_baseline),
            "--baseline",
            str(apache_sun_dec_04),
        ]
        run_gool_on_file_from_cli_and_check(cmd, apache_mon_dec_05, expected_path)

    def test_apache_2k_compare_baseline_common(self) -> None:
        """Test manually setting time filter."""
        expected_path = output_dir_path / "Apache_2K_baseline_compare_common.txt"
        apache_mon_dec_05 = input_dir_path / "Apache_2K_MonDec05.log"
        apache_sun_dec_04 = input_dir_path / "Apache_2K_SunDec04.log"
        cmd = [
            "--display_common",
            "--cfg-file",
            str(cfg_path_baseline),
            "--baseline",
            str(apache_sun_dec_04),
        ]
        run_gool_on_file_from_cli_and_check(cmd, apache_mon_dec_05, expected_path)

    def test_zookeeper_2k_no_raw(self) -> None:
        """Test that gool called with a file without raw produce an output without throw."""
        args = Arguments(
            logfile_paths=(zookeeper_path_log,),
            cfg_file=cfg_path,
        )
        result = main(args)
        assert result == 0

    def test_zookeeper_2k_no_raw_no_config(self) -> None:
        """Test that gool called with a file without raw produce an output without throw."""
        cfg_path = data_dir_path / "drain3_no_exist.ini"
        args = Arguments(
            logfile_paths=(zookeeper_path_log,),
            cfg_file=cfg_path,
        )
        result = main(args)
        assert result == 0

    def test_version_cli_outputs_one_line(self) -> None:
        original_argv = sys.argv.copy()
        try:
            sys.argv = ["gool", "--version"]
            f = io.StringIO()
            with redirect_stdout(f):
                ret = main_cli()
            output = f.getvalue().strip()
            assert ret == 0
            assert output != ""
            assert len(output.splitlines()) == 1
        finally:
            sys.argv = original_argv


class TestErrorHandling:
    """Tests error handling."""

    def test_no_args_exits_with_error(self) -> None:
        cmd: list[str] = []
        run_gool_on_file_from_cli_and_check_raise(cmd, error_code=ErrorCode.NO_LOG_FILES.value)

    def test_non_existing_file_raises_error(self) -> None:
        cmd = ["non_existing.log"]
        run_gool_on_file_from_cli_and_check_raise(cmd, error_code=ErrorCode.FILE_NOT_FOUND.value)

    def test_non_file_raises_error(self) -> None:
        cmd = [str(data_dir_path)]
        run_gool_on_file_from_cli_and_check_raise(cmd, error_code=ErrorCode.FILE_NOT_FOUND.value)

    def test_non_existing_baseline_file_error(self) -> None:
        cmd = [str(apache_path_log), "--baseline", "non_existing.log"]
        run_gool_on_file_from_cli_and_check_raise(cmd, error_code=ErrorCode.FILE_NOT_FOUND.value)

    def test_non_file_baseline_raises_error(self) -> None:
        cmd = [str(apache_path_log), "--baseline", str(data_dir_path)]
        run_gool_on_file_from_cli_and_check_raise(cmd, error_code=ErrorCode.FILE_NOT_FOUND.value)

    def test_invalid_tree_depth_exits_with_error(self) -> None:
        cmd = ["--tree-depth", "1", str(zookeeper_path_log)]
        run_gool_on_file_from_cli_and_check_raise(cmd, error_code=ErrorCode.INVALID_TREE_DEPTH.value)

    def test_invalid_option_exits_with_error(self) -> None:
        cmd = ["--invalid-option", "--size_order", str(zookeeper_path_log)]
        run_gool_on_file_from_cli_and_check_raise(cmd, error_code=2)

    def test_bug_regexp_filter_arg(self) -> None:
        cmd = [str(zookeeper_path_log), "--filter", "*invalid_regex["]
        run_gool_on_file_from_cli_and_check_raise(cmd, error_code=ErrorCode.INVALID_REGEX.value)

    def test_bug_regexp_time_pattern(self) -> None:
        cmd = [str(zookeeper_path_log), "--time_pattern", "*invalid_regex[", "--time_format", "%Y-%m-%d %H:%M:%S"]
        run_gool_on_file_from_cli_and_check_raise(cmd, error_code=ErrorCode.TIME_PATTERN_ERROR.value)

    def test_time_pattern_without_format(self) -> None:
        cmd = [
            str(zookeeper_path_log),
            "--time_pattern",
            "(\\d{4}-\\d{2}-\\d{2} \\d{2}:\\d{2}:\\d{2})",
        ]
        run_gool_on_file_from_cli_and_check_raise(cmd, error_code=ErrorCode.TIME_PATTERN_ERROR.value)

    def test_cant_guess_time_pattern(self) -> None:
        cmd = [
            str(zookeeper_path_log),
            "--time_min",
            "07|00|00",
        ]
        run_gool_on_file_from_cli_and_check_raise(cmd, error_code=ErrorCode.TIME_PATTERN_ERROR.value)

    def test_time_min_sup_time_max(self) -> None:
        cmd = [
            str(zookeeper_path_log),
            "--time_min",
            "07:00:00.000001",
            "--time_max",
            "07:00:00.0",
        ]
        run_gool_on_file_from_cli_and_check_raise(cmd, error_code=ErrorCode.TIME_PATTERN_ERROR.value)

    def test_time_format_dont_match_time_min(self) -> None:
        cmd = [
            str(zookeeper_path_log),
            "--time_min",
            "07:00:00.000001",
            "--time_format",
            "%Y-%m-%d %H:%M:%S",
            "--time_pattern",
            "(\\d{2}:\\d{2}:\\d{2}.\\d{6})",
        ]
        run_gool_on_file_from_cli_and_check_raise(cmd, error_code=ErrorCode.TIME_PATTERN_ERROR.value)

    def test_time_format_dont_match_time_max(self) -> None:
        cmd = [
            str(zookeeper_path_log),
            "--time_max",
            "07:00:00.000001",
            "--time_format",
            "%Y-%m-%d %H:%M:%S",
            "--time_pattern",
            "(\\d{2}:\\d{2}:\\d{2}.\\d{6})",
        ]
        run_gool_on_file_from_cli_and_check_raise(cmd, error_code=ErrorCode.TIME_PATTERN_ERROR.value)

    def test_time_format_without_pattern(self) -> None:
        cmd = [str(zookeeper_path_log), "--time_format", "%Y-%m-%d %H:%M:%S"]
        run_gool_on_file_from_cli_and_check_raise(cmd, error_code=ErrorCode.TIME_PATTERN_ERROR.value)

    def test_empty_no_row(self) -> None:
        """Test that gool called with an empty file without raw produce an output without throw."""
        args = Arguments(
            logfile_paths=(input_dir_path / "empty.log",),
            cfg_file=cfg_path,
        )
        result = main(args)
        assert result == 0
