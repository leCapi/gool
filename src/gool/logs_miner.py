import logging
import re
import time
from collections import Counter
from collections.abc import Iterator
from datetime import datetime
from typing import Any

from drain3 import TemplateMiner  # type: ignore  # type: ignore


class ExceptionLineAfterMaxTime(Exception):
    """Raised when a log line has a time after the specified maximum time."""

    pass


class LogsMiner:
    def __init__(
        self,
        drain3_config: Any,
        *,
        filter_regexp: re.Pattern[str] | None = None,
        time_pattern_regexp: re.Pattern[str] | None = None,
        time_format: str | None = None,
        time_min: datetime | None = None,
        time_max: datetime | None = None,
        unordered_time: bool = False,
    ):
        """
        Initialize the LogsMiner.

        Args:
            drain3_config (any): Configuration for the Drain3 template miner.
            filter_regexp (re.Pattern[str] | None): Regex pattern to filter log lines.
            time_pattern_regexp (re.Pattern[str] | None): Regex pattern to extract time from log lines.
            time_format (str | None): The format of the time extracted from log lines.
            time_min (datetime | None): Minimum time for log lines to be processed.
            time_max (datetime | None): Maximum time for log lines to be processed.
            unordered_time (bool): If True, log lines with time after time_max will not raise an exception and will be processed.
        """
        self.template_miner = TemplateMiner(config=drain3_config)
        self.filter_regexp = filter_regexp
        self.time_pattern_regexp = time_pattern_regexp
        self.time_format = time_format
        self.time_min = time_min
        self.time_max = time_max
        self.unordered_time = unordered_time

    @staticmethod
    def diff_baseline(baseline_miner: "LogsMiner", miner: "LogsMiner") -> tuple[list[str], list[str], list[str]]:
        """
        Diff the clusters of the miner with the baseline miner and print the differences.

        Args:
            baseline_miner (TemplateMiner): The baseline template miner.
            miner (TemplateMiner): The template miner to compare with the baseline.
        Returns:
            tuple[set[str], set[str], set[str]]: A tuple containing three sets:
                - missing_from_baseline: Clusters present in the baseline but missing in the miner.
                - added_from_baseline: Clusters present in the miner but missing in the baseline.
                - common: Clusters present in both the baseline and the miner.
        """
        baseline_clusters = {cluster.get_template() for cluster in baseline_miner.template_miner.drain.clusters}
        clusters = {cluster.get_template() for cluster in miner.template_miner.drain.clusters}

        missing_from_baseline = baseline_clusters - clusters
        added_from_baseline = clusters - baseline_clusters
        common = baseline_clusters & clusters

        return sorted(missing_from_baseline), sorted(added_from_baseline), sorted(common)

    def get_total_nb_lines_clusters(self) -> int:
        """
        Get the total number of lines in all clusters.

        Returns:
            int: The total number of lines in all clusters.
        """
        return sum(cluster.size for cluster in self.template_miner.drain.clusters)

    def _extract_time_from_line(self, line: str) -> datetime | None:
        if not self.time_pattern_regexp or not self.time_format:
            return None
        match = self.time_pattern_regexp.search(line)
        if match:
            time_str = match.group(1)
            try:
                return datetime.strptime(time_str, self.time_format)
            except ValueError:
                logging.warning("Failed to parse time '%s' in line: %s", time_str, line)
                return None
        else:
            logging.warning("Time pattern not found in line: %s", line)
            return None

    def _check_line_out_time_range(
        self,
        line: str,
    ) -> bool:
        """
        Check if the time extracted from a log line is within the specified time range.

        Args:
            line (str): The log line to check.

        Returns:
            bool: True if the line should be skipped (time is out of range), False otherwise

        throws:
            ExceptionLineAfterMaxTime: If the line's time is after the specified maximum time
        """
        if self.time_pattern_regexp is None or self.time_format is None:
            return False
        line_time = self._extract_time_from_line(line)
        if line_time is None:
            logging.warning("Could not extract time from line, skipping time check: %s", line)
            return False
        if self.time_min and line_time < self.time_min:
            return True
        if self.time_max and line_time > self.time_max:
            if self.unordered_time:
                return True
            raise ExceptionLineAfterMaxTime()
        return False

    def add_log_lines_to_miner(
        self,
        line_generator: Iterator[str],
    ) -> tuple[int, Counter]:
        """
        Add log lines from a generator to the template miner.

        Args:
            template_miner (TemplateMiner): The template miner instance.
            line_generator (Generator): A generator yielding log lines.
            filter_regexp (re.Pattern | None): Regex pattern to filter log lines.

        Returns:
            tuple[int, Counter]: The number of lines added and cluster sizes counter.
        """
        start_time = time.perf_counter()
        total_nb_lines = 0
        cluster_char_sizes: Counter = Counter()

        for line in line_generator:
            if not line:
                continue
            if self.filter_regexp and not self.filter_regexp.match(line):
                continue
            try:
                if self._check_line_out_time_range(line):
                    continue
            except ExceptionLineAfterMaxTime:
                logging.info(
                    "Reached a log line with time after the specified maximum time. Stopping processing further lines."
                )
                break
            total_nb_lines += 1
            result = self.template_miner.add_log_message(line)
            cluster_char_sizes[result["cluster_id"]] += len(line)
        end_time = time.perf_counter()
        elapsed_time = end_time - start_time
        logging.info(
            "Processed %d lines in %.2f seconds (%.2f lines/second).",
            total_nb_lines,
            elapsed_time,
            total_nb_lines / elapsed_time if elapsed_time > 0 else 0,
        )
        return total_nb_lines, cluster_char_sizes
