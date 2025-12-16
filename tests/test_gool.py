import io
import sys
from contextlib import redirect_stdout
from pathlib import Path

import pytest

from gool.log_clustering import Arguments, ErrorCode, main, main_cli, surrogate_non_printable

data_dir_path = Path(__file__).parents[0] / "data"
output_dir_path = data_dir_path / "results"
input_dir_path = data_dir_path / "log"
cfg_path = data_dir_path / "drain3.ini"


def test_surrogate_non_printable() -> None:
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


def test_zookeeper_2k_output() -> None:
    """Test the raw output for Zookeeper_2k.log matches the expected file."""
    input_paths_tuple = (input_dir_path / "Zookeeper_2k.log",)
    expected_path = output_dir_path / "Zookeeper_2k_raw_output.txt"
    assert run_gool_on_file_and_check(input_paths_tuple, expected_path)


def test_apache_2k_output() -> None:
    """Test the raw output for Zookeeper_2k.log matches the expected file."""
    input_paths_tuple = (input_dir_path / "Apache_2k.log",)
    expected_path = output_dir_path / "Apache_2k_raw_output.txt"
    assert run_gool_on_file_and_check(input_paths_tuple, expected_path)


def test_6times_zookeeper_2k_output() -> None:
    """Test several files in input"""
    input_paths_tuple = (input_dir_path / "Zookeeper_2k.log",) * 6
    expected_path = output_dir_path / "6times_Zookeeper_2k_raw_output.txt"
    assert run_gool_on_file_and_check(input_paths_tuple, expected_path)


def test_zookeeper_2k_output_similarity_5() -> None:
    """Test manually setting similarity threshold to 0.5."""
    input_paths_tuple = (input_dir_path / "Zookeeper_2k.log",)
    expected_path = output_dir_path / "Zookeeper_2k_sim_thres_5.txt"
    assert run_gool_on_file_and_check(input_paths_tuple, expected_path, similarity=0.5)


def test_zookeeper_2k_output_depth_10() -> None:
    """Test manually setting depth to 10."""
    input_paths_tuple = (input_dir_path / "Zookeeper_2k.log",)
    expected_path = output_dir_path / "Zookeeper_2k_depth10.txt"
    assert run_gool_on_file_and_check(input_paths_tuple, expected_path, depth=10)


def test_zookeeper_2k_output_filter_warn() -> None:
    """Test manually setting warn filter."""
    input_paths_tuple = (input_dir_path / "Zookeeper_2k.log",)
    expected_path = output_dir_path / "Zookeeper_2k_warn.txt"
    assert run_gool_on_file_and_check(input_paths_tuple, expected_path, line_filter=".*WARN.*")


def test_zookeeper_2k_output_lex_order() -> None:
    """Test manually setting lex order."""
    input_paths_tuple = (input_dir_path / "Zookeeper_2k.log",)
    expected_path = output_dir_path / "Zookeeper_2k_lex_order.txt"
    assert run_gool_on_file_and_check(input_paths_tuple, expected_path, lex_order=True)


def test_zookeeper_2k_output_size_order() -> None:
    """Test manually setting size order."""
    input_paths_tuple = (input_dir_path / "Zookeeper_2k.log",)
    expected_path = output_dir_path / "Zookeeper_2k_size_order.txt"
    assert run_gool_on_file_and_check(input_paths_tuple, expected_path, size_order=True)


def test_no_args_exits_with_error() -> None:
    """Test that gool called without arguments exits with code -2."""
    # Save original argv
    original_argv = sys.argv.copy()
    try:
        # Set argv to simulate no arguments (just the script name)
        sys.argv = ["gool"]
        with pytest.raises(SystemExit) as exec_info:
            main_cli()
        assert exec_info.value.code == ErrorCode.NO_LOG_FILES.value
    finally:
        # Restore original argv
        sys.argv = original_argv


def test_non_existing_file_raises_error() -> None:
    """Test that gool called with a non-existing file raises FileNotFoundError."""
    args = Arguments(
        logfile_paths=(Path("non_existing.log"),),
        cfg_file=cfg_path,
    )
    with pytest.raises(SystemExit) as exec_info:
        main(args)
    assert exec_info.value.code == ErrorCode.FILE_NOT_FOUND.value


def test_invalid_tree_depth_exits_with_error() -> None:
    """Test invalid tree-depth throws."""
    original_argv = sys.argv.copy()
    try:
        sys.argv = ["gool", "--tree-depth", "1", "some.log"]
        with pytest.raises(SystemExit) as exec_info:
            main_cli()
        assert exec_info.value.code == ErrorCode.INVALID_TREE_DEPTH.value
    finally:
        sys.argv = original_argv


def test_invalid_option_exits_with_error() -> None:
    """Test that gool called with an invalid option exits with SystemExit."""
    original_argv = sys.argv.copy()
    try:
        sys.argv = ["gool", "--invalid-option", "--size_order", "some.log"]
        with pytest.raises(SystemExit) as exec_info:
            main_cli()
        assert exec_info.value.code == 2
    finally:
        sys.argv = original_argv


def test_version_cli_outputs_one_line() -> None:
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


def test_zookeeper_2K_no_raw() -> None:
    """Test that gool called with a file without raw produce an output without throw."""
    args = Arguments(
        logfile_paths=((input_dir_path / "Zookeeper_2k.log",)),
        cfg_file=cfg_path,
    )
    result = main(args)
    assert result == 0


def test_zookeeper_2K_no_raw_no_config() -> None:
    """Test that gool called with a file without raw produce an output without throw."""
    cfg_path = data_dir_path / "drain3_no_exist.ini"
    args = Arguments(
        logfile_paths=((input_dir_path / "Zookeeper_2k.log",)),
        cfg_file=cfg_path,
    )
    result = main(args)
    assert result == 0


def test_bug_regexp_filter_arg() -> None:
    """Test that gool called with a file with a wrong regexp filter throw."""
    args = Arguments(
        logfile_paths=((input_dir_path / "Zookeeper_2k.log",)),
        cfg_file=cfg_path,
        filter="*invalid_regex[",
    )
    with pytest.raises(SystemExit) as exec_info:
        main(args)
    assert exec_info.value.code == ErrorCode.INVALID_REGEX.value


def test_empty_no_row() -> None:
    """Test that gool called with an empty file without raw produce an output without throw."""
    args = Arguments(
        logfile_paths=((input_dir_path / "empty.log",)),
        cfg_file=cfg_path,
    )
    result = main(args)
    assert result == 0
