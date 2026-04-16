#! /usr/bin/env python3
"""
This script computes clusters of similar log lines from the provided log files.
It uses the drain3 library to extract templates from log lines.
It can filter log lines based on a regex pattern and display the clusters.
"""

import contextlib
import dataclasses
import itertools
import logging
import pathlib
import re
import sys
from collections import Counter, namedtuple
from collections.abc import Generator
from datetime import datetime
from enum import Enum
from math import ceil, log10
from typing import Annotated, Any, Union

import tyro
from drain3.masking import MaskingInstruction  # type: ignore
from drain3.template_miner_config import TemplateMinerConfig  # type: ignore
from rich.console import Console
from rich.logging import RichHandler
from rich.progress import BarColumn, Progress, TaskID, TaskProgressColumn, TextColumn
from rich.table import Table

from gool.logs_miner import LogsMiner

try:
    from gool._version import __version__
except ImportError:
    __version__ = "unknown"


class ErrorCode(Enum):
    """Error codes for the log clustering script."""

    NO_ERROR = 0
    NO_LOG_FILES = -1
    INVALID_TREE_DEPTH = -2
    INVALID_REGEX = -3
    FILE_NOT_FOUND = -4
    IO_ERROR = -5
    TIME_PATTERN_ERROR = -6


error_console = Console(file=sys.stderr, stderr=True)
console = Console()

logging.basicConfig(
    format="%(module)s : %(message)s",
    datefmt="%H:%M:%S.%f",
    level=logging.INFO,
    handlers=[RichHandler(console=error_console)],
)
logging.getLogger("drain3").setLevel(logging.WARNING)

HOME_CFG_FILE = pathlib.Path.home() / ".drain3.ini"
KB_FACTOR = 1000


@dataclasses.dataclass
class Arguments:
    """
    Use drain algorithm to cluster similar log lines
    from the provided log files.

    Arguments for the log clustering script :
    """

    # logs files paths to process
    logfile_paths: tyro.conf.Positional[tuple[pathlib.Path, ...]]
    # configuration file for the drain3 template miner.
    cfg_file: Annotated[pathlib.Path, tyro.conf.arg(aliases=["-c"])] = HOME_CFG_FILE
    # If set, filter input log lines which does not match the regex (re python module syntax).
    # Example: '.*(\| Warning |\| Error ).*'
    filter: Annotated[str, tyro.conf.arg(aliases=["-f"])] = ""
    # Format code (for strptime) of the time extracted of each line to convert string into datetime.
    # If empty, the program will try with these patterns "%H:%M:%S.%f" and "%H:%M:%S" to extract time.
    # User must provide both time_format and time_pattern.
    time_format: Annotated[str, tyro.conf.arg(aliases=["-T"])] = ""
    # regexp pattern to extract time of each line. Default pattern is r'(\d{2}:\d{2}:\d{2}(?:\.\d{1,9})?)'
    # to extract time like "15:04:05.000" or "15:04:05".
    time_pattern: Annotated[str, tyro.conf.arg(aliases=["-t"])] = ""
    # time_min used to filter log lines based on the time extracted with time_pattern.
    # Required to be used with time_pattern. Example : "(\\w{3} \\w{3} \\d{2} \\d{2}:\\d{2}:\\d{2} \\d{4})"
    time_min: Annotated[str, tyro.conf.arg(aliases=["-m"])] = ""
    # tim_max used to filter log lines based on the time extracted with time_pattern.
    # Required to be used with time_pattern. Python datetime strptime format is expected
    # for example: "15:04:05.000" or "15:04:05".
    time_max: Annotated[str, tyro.conf.arg(aliases=["-M"])] = ""
    # assume log lines are not ordered by time, and do not stop processing
    # after reaching a line with time after time_max.
    unordered_time: Annotated[tyro.conf.FlagCreatePairsOff[bool], tyro.conf.arg(aliases=["-u"])] = False
    # baseline log files to compare with. If set, the clusters will compared to baseline clusters.
    baseline: Annotated[tuple[pathlib.Path, ...], tyro.conf.arg(aliases=["-b"])] = ()
    # If set, all baseline clusters will also be displayed.
    display_common: Annotated[tyro.conf.FlagCreatePairsOff[bool], tyro.conf.arg(aliases=["-C"])] = False
    # If set, the clusters will be ordered lexicographically.
    lex_order: Annotated[tyro.conf.FlagCreatePairsOff[bool], tyro.conf.arg(aliases=["-l"])] = False
    # The clusters will be ordered by this total length. Where total length is the sum of all
    # log lines lengths belonging to the cluster.
    size_order: Annotated[tyro.conf.FlagCreatePairsOff[bool], tyro.conf.arg(aliases=["-z"])] = False
    # Similarity threshold for the template miner to group lines together.
    # A higher value will lead to create more clusters. Drain default value is 0.4.
    similarity_threshold: Annotated[Union[float, None], tyro.conf.arg(aliases=["-s"])] = None
    # depth of the tree to build the templates miner,
    # a higher value will lead to create more clusters.
    # The higher the value, the more tokens of the log lines
    # will be considered to build the clusters. Increase this value
    # to make clustering rely on distant tokens. Drain default value is 4.
    tree_depth: Annotated[Union[int, None], tyro.conf.arg(aliases=["-d"], default=4)] = None
    # If set, output clusters in plain text format without colors or table formatting,
    # making it easy to process with bash tools like grep, awk, or cut.
    raw: Annotated[tyro.conf.FlagCreatePairsOff[bool], tyro.conf.arg(aliases=["-r"])] = False
    # return the version and exit
    version: Annotated[tyro.conf.FlagCreatePairsOff[bool], tyro.conf.arg(aliases=["-v"])] = False

    def __post_init__(self) -> None:  # noqa: C901
        if self.version:
            return

        if self.logfile_paths is None or len(self.logfile_paths) == 0:
            error_message = "No log files provided. Please specify at least one log file."
            logging.critical(error_message)
            sys.exit(ErrorCode.NO_LOG_FILES.value)
        else:
            for logfile_path in self.logfile_paths:
                if not logfile_path.exists():
                    logging.critical("Log file not found: %s", logfile_path)
                    sys.exit(ErrorCode.FILE_NOT_FOUND.value)
                if not logfile_path.is_file():
                    logging.critical("Not a file: %s", logfile_path)
                    sys.exit(ErrorCode.FILE_NOT_FOUND.value)

        if self.baseline:
            for baseline_path in self.baseline:
                if not baseline_path.exists():
                    logging.critical("Baseline file not found: %s", baseline_path)
                    sys.exit(ErrorCode.FILE_NOT_FOUND.value)
                if not baseline_path.is_file():
                    logging.critical("Not a file: %s", baseline_path)
                    sys.exit(ErrorCode.FILE_NOT_FOUND.value)

        if self.tree_depth and self.tree_depth < 3:
            error_message = f"The tree depth is set to {self.tree_depth}. Minimum value is 3."
            logging.critical(error_message)
            sys.exit(ErrorCode.INVALID_TREE_DEPTH.value)

        if self.filter:
            try:
                re.compile(self.filter)
            except re.error as e:
                logging.critical("Invalid regex pattern: %s. Error: %s", self.filter, e)
                sys.exit(ErrorCode.INVALID_REGEX.value)

        if self.time_pattern:
            try:
                re.compile(self.time_pattern)
            except re.error as e:
                logging.critical("Invalid time regex pattern: %s. Error: %s", self.time_pattern, e)
                sys.exit(ErrorCode.TIME_PATTERN_ERROR.value)
            if not self.time_format:
                error_message = "Time format is required when time pattern is provided."
                logging.critical(error_message)
                sys.exit(ErrorCode.TIME_PATTERN_ERROR.value)
        if self.time_format and not self.time_pattern:
            error_message = "Time pattern is required when time format is provided."
            logging.critical(error_message)
            sys.exit(ErrorCode.TIME_PATTERN_ERROR.value)
        if self.time_min or self.time_max:
            time_value = self.time_min if self.time_min else self.time_max
            if not self.time_format and not self.time_pattern:
                logging.info(
                    "No time pattern or format provided. Trying to guess them from time value '%s'.",
                    time_value,
                )
                guessed_regexp_format = guess_time_regexp_and_format_code(time_value)
                if not guessed_regexp_format:
                    logging.critical(
                        "Failed to guess time pattern and format from time value '%s'. Please provide a valid time pattern and format.",
                        time_value,
                    )
                    sys.exit(ErrorCode.TIME_PATTERN_ERROR.value)
                self.time_pattern, self.time_format = guessed_regexp_format
                logging.info(
                    "Guessed time pattern: '%s' and time format: '%s' from time value '%s'.",
                    self.time_pattern,
                    self.time_format,
                    time_value,
                )

        if self.time_min:
            try:
                convert_time_str_to_datetime(self.time_min, self.time_format)
            except ValueError as e:
                logging.critical("Invalid time_min format: %s. Error: %s", self.time_min, e)
                sys.exit(ErrorCode.TIME_PATTERN_ERROR.value)
        if self.time_max:
            try:
                convert_time_str_to_datetime(self.time_max, self.time_format)
            except ValueError as e:
                logging.critical("Invalid time_max format: %s. Error: %s", self.time_max, e)
                sys.exit(ErrorCode.TIME_PATTERN_ERROR.value)
        if self.time_max and self.time_min and self.time_format:
            time_min_dt = convert_time_str_to_datetime(self.time_min, self.time_format)
            time_max_dt = convert_time_str_to_datetime(self.time_max, self.time_format)
            if time_max_dt < time_min_dt:
                logging.critical("time_max (%s) is before time_min (%s).", self.time_max, self.time_min)
                sys.exit(ErrorCode.TIME_PATTERN_ERROR.value)


def guess_time_regexp_and_format_code(time_str: str) -> tuple[str, str] | None:
    """
    Guess the time regex pattern and format code from a log line.

    Args:
        time_str (str): time string to guess the pattern and format code from.

    Returns:
        A tuple containing the guessed regex pattern and format code.
    """
    time_regex = r"(\d{2}:\d{2}:\d{2}(?:\.\d{1,9})?)"
    regex = re.compile(time_regex)
    match = regex.search(time_str)
    if not match:
        return None
    matched_time = match.group(1)
    with contextlib.suppress(ValueError):
        time_format = "%H:%M:%S.%f"
        datetime.strptime(matched_time, time_format)
        return time_regex, time_format
    with contextlib.suppress(ValueError):
        time_format = "%H:%M:%S"
        datetime.strptime(matched_time, time_format)
        return time_regex, time_format
    return None


def convert_time_str_to_datetime(time_str: str, format_code: str) -> datetime:
    """
    Convert a time string to a datetime object using the provided format code or by guessing common formats.

    Args:
        time_str (str): The time string to convert.
        format_code (str): The format code to use for conversion.

    Returns:
        datetime: The converted datetime object.
    """
    return datetime.strptime(time_str, format_code)


def create_drain3_cfg(args: Arguments) -> Any:
    """
    Create a default configuration for the drain3 template miner.

    Returns:
        TemplateMinerConfig: A configuration object for the drain3 template miner.
    """
    drain3_cfg = TemplateMinerConfig()
    if args.cfg_file.exists():
        logging.info("Loading configuration from %s", args.cfg_file)
        drain3_cfg.load(args.cfg_file)
    else:
        logging.info(
            "Configuration file %s not found. Using default configuration to mask IP, time, and hex values.",
            args.cfg_file,
        )
        mask_time = MaskingInstruction(r"(\d{2}:\d{2}:\d{2}(.\d+|))", "TIME")
        mask_ip = MaskingInstruction(
            r"((?<=[^A-Za-z0-9])|^)(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})((?=[^A-Za-z0-9])|$)",
            "IP",
        )
        mask_hex = MaskingInstruction(
            r"((?<=[^A-Za-z0-9])|^)(0[xX][0-9a-fA-F]+)((?=[^A-Za-z0-9])|$)",
            "HEX",
        )
        # Add masking instructions to the configuration
        drain3_cfg.masking_instructions += [mask_time, mask_ip, mask_hex]

    if args.similarity_threshold:
        drain3_cfg.drain_sim_th = args.similarity_threshold
    if args.tree_depth:
        drain3_cfg.drain_depth = args.tree_depth
    return drain3_cfg


def estimate_lines(path: pathlib.Path, nb_sample_lines: int = 1000) -> int:
    """
    Estimate total lines based on file size and sample average.
    Args:
        path (pathlib.Path): Path to the log file.
        nb_sample_lines (int): Number of lines to sample for average calculation.
    """
    file_size = path.stat().st_size
    if file_size == 0:
        return 0
    # Sample first 'sample_lines' to get avg bytes per line
    avg_bytes_per_line = 0
    with open(path, "rb") as f:  # Use binary for accurate byte counting
        for i, line in enumerate(f):
            if i >= nb_sample_lines:
                break
            avg_bytes_per_line += len(line)
    if nb_sample_lines > 0:
        avg_bytes_per_line //= nb_sample_lines
    # Estimate total lines
    estimated = int(file_size / avg_bytes_per_line) if avg_bytes_per_line > 0 else 0
    return max(estimated, 1)


def create_file_line_generators(
    logfile_paths: tuple[pathlib.Path, ...],
    progress: Progress,
) -> itertools.chain:
    """
    Create progress tasks for all files and return a chained generator yielding lines from all files.

    Args:
        logfile_paths (tuple[pathlib.Path, ...]): Paths to the log files.
        progress (Progress): The progress instance to track file processing.

    Returns:
        Generator: A single generator yielding lines from all files.
    """
    generators = []
    for logfile_path in logfile_paths:
        sample_nb_lines = 20000
        number_of_lines = estimate_lines(logfile_path, sample_nb_lines)
        task_id = progress.add_task(f"{pathlib.Path(logfile_path).name}", total=number_of_lines)

        def line_generator(path: pathlib.Path, tid: TaskID, nb_lines: int) -> Generator[str, None, None]:
            """Generator that yields lines from a file and updates progress."""
            with open(path, encoding="utf-8", errors="surrogateescape") as f:
                for line in f:
                    progress.update(tid, advance=1)
                    yield line
            progress.update(tid, completed=nb_lines)
            progress.stop_task(tid)

        generators.append(line_generator(logfile_path, task_id, number_of_lines))

    # Chain all generators into one
    return itertools.chain(*generators)


def surrogate_non_printable(s: str) -> str:
    """
    Surrogate non-printable characters from a string.

    Args:
        s (str): The input string.
    Returns:
        str: The cleaned string.
    """
    return s.encode("utf-8", errors="surrogateescape").decode("utf-8")


def compute_margin_for_display(max_number: int) -> int:
    """
    Compute the margin for displaying numbers.

    Args:
        max_number (int): The maximum number to display.
    Returns:
        int: The computed margin.
    """
    if max_number <= 0:
        return 1
    b10 = log10(max_number)
    margin = ceil(log10(max_number)) if b10 != int(b10) else int(b10 + 1)
    return margin


def display_diff_baseline(
    missing: list[str], added: list[str], common: list[str], raw: bool = False, display_common: bool = False
) -> None:
    """
    Display the difference between baseline clusters and current clusters.

    Args:
        missing (list[str]): Clusters present in baseline but missing in current.
        added (list[str]): Clusters present in current but missing in baseline.
        common (list[str]): Clusters present in both baseline and current.
        raw (bool): If True, display in plain text format for bash processing. Defaults to False.
        display_common (bool): If True, also display common clusters. Defaults to False.
    """

    def display_data_raw(list_data: list[str], header: str) -> None:
        console.print(f"{header}:")
        for item in list_data:
            console.print(f"{item}", soft_wrap=True, markup=False)

    def display_data(list_data: list[str], header: str) -> None:
        table = Table(title=header, highlight=True)
        table.add_column("Template", justify="left")
        for item in list_data:
            pattern = surrogate_non_printable(item)
            table.add_row(pattern)
        console.print(table, markup=False)

    if raw:
        display_data_raw(missing, "Missing from baseline")
        display_data_raw(added, "Added from baseline")
        if display_common:
            display_data_raw(common, "Common with baseline")
    else:
        display_data(missing, "Missing from baseline")
        display_data(added, "Added from baseline")
        if display_common:
            display_data(common, "Common with baseline")


def display_clusters(
    template_miner: Any,
    cluster_char_sizes: Counter,
    order_by: str = "count",
    raw: bool = False,
    table_title: str = "Log Clusters",
) -> None:
    """
    Display all clusters in a table with 3 columns: Count - Char Size (KB) - Template.

    Args:
        template_miner (TemplateMiner): the template miner which has been filled with log lines.
        cluster_char_sizes (Counter): a counter of the total sizes of each cluster.
        order_by (str): How to order clusters: "count", "size", or "template". Defaults to "count".
    """
    ClusterResult = namedtuple("ClusterResult", ["count", "char_size", "template"])
    clusters_data = [
        ClusterResult(
            count=cluster.size,
            char_size=cluster_char_sizes[cluster.cluster_id],
            template=cluster.get_template(),
        )
        for cluster in template_miner.drain.clusters
    ]

    if not clusters_data:
        return

    # Sort based on order_by parameter
    if order_by == "size":
        clusters_data.sort(key=lambda x: x.char_size, reverse=True)
    elif order_by == "template":
        clusters_data.sort(key=lambda x: x.template)
    else:  # default to "count"
        clusters_data.sort(key=lambda x: x.count, reverse=True)

    # Add rows to the table or print plain text
    if raw:
        # Plain text output for bash processing
        console.print(table_title)
        count_margin = compute_margin_for_display(max(cluster.count for cluster in clusters_data))
        size_margin = compute_margin_for_display(max(cluster.char_size for cluster in clusters_data) // KB_FACTOR)
        for cluster in clusters_data:
            pattern = surrogate_non_printable(cluster.template)
            count_str = f"{cluster.count}"
            size_kb = cluster.char_size // KB_FACTOR
            size_str = f"{size_kb}"
            console.print(
                f"{count_str:>{count_margin}} - {size_str:>{size_margin}} - {pattern}",
                soft_wrap=True,
                markup=False,
            )
    else:
        # Create a Rich table
        table = Table(title=table_title, highlight=True)
        table.add_column("Count", justify="right", style="cyan", no_wrap=True)
        table.add_column("Char Size (KB)", justify="right", style="magenta", no_wrap=True)
        table.add_column("Template", justify="left")

        for cluster in clusters_data:
            pattern = surrogate_non_printable(cluster.template)
            count_str = f"{cluster.count:,}".replace(",", " ")
            size_kb = cluster.char_size // KB_FACTOR
            size_str = f"{size_kb:,}".replace(",", " ")
            table.add_row(count_str, size_str, pattern)

        # Print the table
        console.print(table, markup=False)


def create_and_run_miner(
    drain3_config: Any,
    logfile_paths: tuple[pathlib.Path, ...],
    *,
    filter_regexp: re.Pattern[str] | None = None,
    time_pattern_regexp: re.Pattern[str] | None = None,
    time_format: str | None = None,
    time_min: datetime | None = None,
    time_max: datetime | None = None,
    unordered_time: bool = False,
) -> tuple[LogsMiner, int, Counter | None]:

    template_miner = LogsMiner(
        drain3_config,
        filter_regexp=filter_regexp,
        time_format=time_format,
        time_pattern_regexp=time_pattern_regexp,
        time_min=time_min,
        time_max=time_max,
        unordered_time=unordered_time,
    )

    total_nb_lines, cluster_char_sizes = 0, None
    try:
        with Progress(
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=error_console,
        ) as progress:
            line_generator = create_file_line_generators(logfile_paths, progress)
            total_nb_lines, cluster_char_sizes = template_miner.add_log_lines_to_miner(line_generator)
    except FileNotFoundError as e:
        logging.critical("File not found: %s", e.filename)
        sys.exit(ErrorCode.FILE_NOT_FOUND.value)
    except OSError as e:
        logging.critical("I/O error(%s): %s", e.errno, e.strerror)
        sys.exit(ErrorCode.IO_ERROR.value)

    return template_miner, total_nb_lines, cluster_char_sizes


def display_results(
    drain3_runner: Any, cluster_char_sizes: Counter | None, raw: bool, lex_order: bool, size_order: bool, title: str
) -> None:
    if cluster_char_sizes is None:
        cluster_char_sizes = Counter()
    order = "count"
    if lex_order:
        order = "template"
    elif size_order:
        order = "size"
    display_clusters(drain3_runner.template_miner, cluster_char_sizes, order_by=order, raw=raw, table_title=title)


def sanity_check(total_nb_lines_clusters: int, total_nb_lines: int) -> int:
    """Check if the total number of lines in clusters matches the processed lines."""
    result = 0
    if total_nb_lines_clusters != total_nb_lines:
        logging.error(
            "The number of lines in the clusters (%d) does "
            "not match the total number of lines processed (%d)."
            "Maybe you should increase [DRAIN]/max_clusters parameter.",
            total_nb_lines_clusters,
            total_nb_lines,
        )
        result = 1
    return result


def main(args: Arguments) -> int:
    """
    Extract the cluster templates from the provided log files.

    Args:
        args (Arguments): paths and options for the log extractor

    Returns:
        int: 0 if everything went well
    """
    drain3_cfg = create_drain3_cfg(args)
    time_pattern = re.compile(args.time_pattern) if args.time_pattern else None
    filter_regexp = re.compile(args.filter) if args.filter else None
    time_format = args.time_format
    time_min = convert_time_str_to_datetime(args.time_min, time_format) if args.time_min else None
    time_max = convert_time_str_to_datetime(args.time_max, time_format) if args.time_max else None

    logging.info("Running clustering.")
    runner, total_nb_lines, cluster_char_sizes = create_and_run_miner(
        drain3_cfg,
        args.logfile_paths,
        filter_regexp=filter_regexp,
        time_pattern_regexp=time_pattern,
        time_format=time_format,
        time_min=time_min,
        time_max=time_max,
        unordered_time=args.unordered_time,
    )

    if args.baseline:
        logging.info("Running baseline clustering.")
        bl_runner, bl_total_nb_lines, bl_cluster_char_sizes = create_and_run_miner(
            drain3_cfg,
            args.baseline,
            filter_regexp=filter_regexp,
            time_pattern_regexp=time_pattern,
            time_format=time_format,
            time_min=time_min,
            time_max=time_max,
            unordered_time=args.unordered_time,
        )
        sanity_check(bl_runner.get_total_nb_lines_clusters(), bl_total_nb_lines)
        missing, added, common = LogsMiner.diff_baseline(bl_runner, runner)
        display_diff_baseline(
            missing,
            added,
            common,
            raw=args.raw,
            display_common=args.display_common,
        )
        print()
        if args.display_common:
            display_results(
                bl_runner, bl_cluster_char_sizes, args.raw, args.lex_order, args.size_order, "Baseline Log Clusters"
            )
            print()

    display_results(runner, cluster_char_sizes, args.raw, args.lex_order, args.size_order, "Log Clusters")
    total_nb_lines_clusters = runner.get_total_nb_lines_clusters()
    return sanity_check(total_nb_lines_clusters, total_nb_lines)


def main_cli() -> int:
    """
    Main entry point for the CLI.

    Returns:
        int: Exit code.
    """
    try:
        cfg = tyro.cli(Arguments)
        if cfg.version:
            print(__version__)
            return ErrorCode.NO_ERROR.value
        return main(cfg)
    except KeyboardInterrupt:
        error_console.print("\n[red]Process interrupted by user[/red]")
        return ErrorCode.IO_ERROR.value


if __name__ == "__main__":
    main_cli()
