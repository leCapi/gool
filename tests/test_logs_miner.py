import re
from datetime import datetime
from typing import Any
from unittest.mock import Mock, patch

import pytest

from gool.logs_miner import ExceptionLineAfterMaxTime, LogsMiner


@pytest.fixture
def logs_miner_with_time_config() -> Any:
    """LogsMiner instance with time pattern and format configured."""
    time_pattern = re.compile(r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})")
    time_format = "%Y-%m-%d %H:%M:%S"
    with patch("gool.logs_miner.TemplateMiner"):
        return LogsMiner(
            drain3_config=Mock(),
            time_pattern_regexp=time_pattern,
            time_format=time_format,
        )


@pytest.fixture
def logs_miner_no_time_config() -> Any:
    """LogsMiner instance without time configuration."""
    with patch("gool.logs_miner.TemplateMiner"):
        return LogsMiner(drain3_config=Mock())


class TestExtractTimeFromLine:
    """Tests for _extract_time_from_line method."""

    def test_extract_time_when_no_pattern_regexp(self, logs_miner_no_time_config: Any) -> None:
        """Should return None when time_pattern_regexp is not set."""
        result = logs_miner_no_time_config._extract_time_from_line("2024-01-15 10:30:45 Some log message")
        assert result is None

    def test_extract_time_when_no_format(self) -> None:
        """Should return None when time_format is not set."""
        time_pattern = re.compile(r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})")
        with patch("gool.logs_miner.TemplateMiner"):
            logs_miner = LogsMiner(
                drain3_config=Mock(),
                time_pattern_regexp=time_pattern,
                time_format=None,
            )
        result = logs_miner._extract_time_from_line("2024-01-15 10:30:45 Some log message")
        assert result is None

    def test_extract_time_when_pattern_does_not_match(self, logs_miner_with_time_config: Any) -> None:
        """Should return None when pattern doesn't match in line."""
        with patch("gool.logs_miner.logging") as mock_logging:
            result = logs_miner_with_time_config._extract_time_from_line("No time in this message")
            assert result is None
            mock_logging.warning.assert_called_once()

    def test_extract_time_when_parsing_fails(self, logs_miner_with_time_config: Any) -> None:
        """Should return None when time string cannot be parsed."""
        with patch("gool.logs_miner.logging") as mock_logging:
            result = logs_miner_with_time_config._extract_time_from_line("2024-13-45 25:70:90 Invalid time")
            assert result is None
            mock_logging.warning.assert_called_once()

    def test_extract_time_success(self, logs_miner_with_time_config: Any) -> None:
        """Should return datetime when time extraction succeeds."""
        line = "2024-01-15 10:30:45 Some log message"
        result = logs_miner_with_time_config._extract_time_from_line(line)
        assert result is not None
        assert result == datetime(2024, 1, 15, 10, 30, 45)

    def test_extract_time_from_different_positions(self, logs_miner_with_time_config: Any) -> None:
        """Should extract time regardless of its position in the line."""
        line = "Some prefix 2024-06-20 14:25:33 Some suffix"
        result = logs_miner_with_time_config._extract_time_from_line(line)
        assert result == datetime(2024, 6, 20, 14, 25, 33)


class TestCheckLineOutTimeRange:
    """Tests for _check_line_out_time_range method."""

    def test_returns_false_when_no_time_pattern(self, logs_miner_no_time_config: Any) -> None:
        """Should return False when time_pattern_regexp is not set."""
        result = logs_miner_no_time_config._check_line_out_time_range("2024-01-15 10:30:45 Some log")
        assert result is False

    def test_returns_false_when_no_time_format(self) -> None:
        """Should return False when time_format is not set."""
        time_pattern = re.compile(r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})")
        with patch("gool.logs_miner.TemplateMiner"):
            logs_miner = LogsMiner(
                drain3_config=Mock(),
                time_pattern_regexp=time_pattern,
                time_format=None,
            )
        result = logs_miner._check_line_out_time_range("2024-01-15 10:30:45 Some log")
        assert result is False

    def test_returns_false_when_time_cannot_be_extracted(self, logs_miner_with_time_config: Any) -> None:
        """Should return False and log warning when time cannot be extracted."""
        with patch("gool.logs_miner.logging") as mock_logging:
            result = logs_miner_with_time_config._check_line_out_time_range("No time in this message")
            assert result is False
            mock_logging.warning.assert_called()

    def test_returns_true_when_time_before_min(self) -> None:
        """Should return True when line time is before time_min."""
        time_pattern = re.compile(r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})")
        time_format = "%Y-%m-%d %H:%M:%S"
        time_min = datetime(2024, 1, 15, 12, 0, 0)

        with patch("gool.logs_miner.TemplateMiner"):
            logs_miner = LogsMiner(
                drain3_config=Mock(),
                time_pattern_regexp=time_pattern,
                time_format=time_format,
                time_min=time_min,
            )

        # Line time is before time_min
        result = logs_miner._check_line_out_time_range("2024-01-15 10:30:45 Some log")
        assert result is True

    def test_returns_false_when_time_after_min(self) -> None:
        """Should return False when line time is after time_min."""
        time_pattern = re.compile(r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})")
        time_format = "%Y-%m-%d %H:%M:%S"
        time_min = datetime(2024, 1, 15, 10, 0, 0)

        with patch("gool.logs_miner.TemplateMiner"):
            logs_miner = LogsMiner(
                drain3_config=Mock(),
                time_pattern_regexp=time_pattern,
                time_format=time_format,
                time_min=time_min,
            )

        # Line time is after time_min
        result = logs_miner._check_line_out_time_range("2024-01-15 10:30:45 Some log")
        assert result is False

    def test_raises_exception_when_time_after_max_ordered(self) -> None:
        """Should raise ExceptionLineAfterMaxTime when time > time_max and unordered_time is False."""
        time_pattern = re.compile(r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})")
        time_format = "%Y-%m-%d %H:%M:%S"
        time_max = datetime(2024, 1, 15, 10, 0, 0)

        with patch("gool.logs_miner.TemplateMiner"):
            logs_miner = LogsMiner(
                drain3_config=Mock(),
                time_pattern_regexp=time_pattern,
                time_format=time_format,
                time_max=time_max,
                unordered_time=False,
            )

        # Line time is after time_max
        with pytest.raises(ExceptionLineAfterMaxTime):
            logs_miner._check_line_out_time_range("2024-01-15 10:30:45 Some log")

    def test_returns_true_when_time_after_max_unordered(self) -> None:
        """Should return True when time > time_max and unordered_time is True."""
        time_pattern = re.compile(r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})")
        time_format = "%Y-%m-%d %H:%M:%S"
        time_max = datetime(2024, 1, 15, 10, 0, 0)

        with patch("gool.logs_miner.TemplateMiner"):
            logs_miner = LogsMiner(
                drain3_config=Mock(),
                time_pattern_regexp=time_pattern,
                time_format=time_format,
                time_max=time_max,
                unordered_time=True,
            )

        # Line time is after time_max but unordered_time is True
        result = logs_miner._check_line_out_time_range("2024-01-15 10:30:45 Some log")
        assert result is True

    def test_returns_false_when_time_before_max(self) -> None:
        """Should return False when line time is before time_max."""
        time_pattern = re.compile(r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})")
        time_format = "%Y-%m-%d %H:%M:%S"
        time_max = datetime(2024, 1, 15, 12, 0, 0)

        with patch("gool.logs_miner.TemplateMiner"):
            logs_miner = LogsMiner(
                drain3_config=Mock(),
                time_pattern_regexp=time_pattern,
                time_format=time_format,
                time_max=time_max,
            )

        # Line time is before time_max
        result = logs_miner._check_line_out_time_range("2024-01-15 10:30:45 Some log")
        assert result is False

    def test_returns_false_when_time_within_range(self) -> None:
        """Should return False when line time is within min and max range."""
        time_pattern = re.compile(r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})")
        time_format = "%Y-%m-%d %H:%M:%S"
        time_min = datetime(2024, 1, 15, 10, 0, 0)
        time_max = datetime(2024, 1, 15, 12, 0, 0)

        with patch("gool.logs_miner.TemplateMiner"):
            logs_miner = LogsMiner(
                drain3_config=Mock(),
                time_pattern_regexp=time_pattern,
                time_format=time_format,
                time_min=time_min,
                time_max=time_max,
            )

        # Line time is within range
        result = logs_miner._check_line_out_time_range("2024-01-15 11:00:00 Some log")
        assert result is False

    def test_returns_false_when_time_equal_to_min(self) -> None:
        """Should return False when line time equals time_min."""
        time_pattern = re.compile(r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})")
        time_format = "%Y-%m-%d %H:%M:%S"
        time_min = datetime(2024, 1, 15, 10, 30, 45)

        with patch("gool.logs_miner.TemplateMiner"):
            logs_miner = LogsMiner(
                drain3_config=Mock(),
                time_pattern_regexp=time_pattern,
                time_format=time_format,
                time_min=time_min,
            )

        # Line time equals time_min (not less than)
        result = logs_miner._check_line_out_time_range("2024-01-15 10:30:45 Some log")
        assert result is False

    def test_returns_false_when_time_equal_to_max(self) -> None:
        """Should return False when line time equals time_max."""
        time_pattern = re.compile(r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})")
        time_format = "%Y-%m-%d %H:%M:%S"
        time_max = datetime(2024, 1, 15, 10, 30, 45)

        with patch("gool.logs_miner.TemplateMiner"):
            logs_miner = LogsMiner(
                drain3_config=Mock(),
                time_pattern_regexp=time_pattern,
                time_format=time_format,
                time_max=time_max,
            )

        # Line time equals time_max (not greater than)
        result = logs_miner._check_line_out_time_range("2024-01-15 10:30:45 Some log")
        assert result is False


class TestDiffBaseline:
    """Tests for diff_baseline static method."""

    def _create_logs_miner_with_clusters(self, templates: list[str]) -> Any:
        """Helper to create a LogsMiner with mock clusters."""
        with patch("gool.logs_miner.TemplateMiner"):
            logs_miner = LogsMiner(drain3_config=Mock())

            # Create mock clusters
            mock_clusters = []
            for template in templates:
                mock_cluster = Mock()
                mock_cluster.get_template.return_value = template
                mock_clusters.append(mock_cluster)

            # Set up the drain.clusters attribute
            logs_miner.template_miner.drain.clusters = mock_clusters
            return logs_miner

    def test_diff_baseline_identical_clusters(self) -> None:
        """Should return empty missing and added lists when clusters are identical."""
        baseline = self._create_logs_miner_with_clusters(["template1", "template2", "template3"])
        miner = self._create_logs_miner_with_clusters(["template1", "template2", "template3"])

        missing, added, common = LogsMiner.diff_baseline(baseline, miner)

        assert missing == []
        assert added == []
        assert common == ["template1", "template2", "template3"]

    def test_diff_baseline_missing_clusters(self) -> None:
        """Should return missing clusters when baseline has clusters not in miner."""
        baseline = self._create_logs_miner_with_clusters(["template1", "template2", "template3"])
        miner = self._create_logs_miner_with_clusters(["template1"])

        missing, added, common = LogsMiner.diff_baseline(baseline, miner)

        assert set(missing) == {"template2", "template3"}
        assert added == []
        assert common == ["template1"]

    def test_diff_baseline_added_clusters(self) -> None:
        """Should return added clusters when miner has clusters not in baseline."""
        baseline = self._create_logs_miner_with_clusters(["template1"])
        miner = self._create_logs_miner_with_clusters(["template1", "template2", "template3"])

        missing, added, common = LogsMiner.diff_baseline(baseline, miner)

        assert missing == []
        assert set(added) == {"template2", "template3"}
        assert common == ["template1"]

    def test_diff_baseline_mixed_differences(self) -> None:
        """Should return all three lists when there are different clusters."""
        baseline = self._create_logs_miner_with_clusters(["template1", "template2", "template4"])
        miner = self._create_logs_miner_with_clusters(["template1", "template3", "template5"])

        missing, added, common = LogsMiner.diff_baseline(baseline, miner)

        assert set(missing) == {"template2", "template4"}
        assert set(added) == {"template3", "template5"}
        assert common == ["template1"]

    def test_diff_baseline_empty_baseline(self) -> None:
        """Should return all miner clusters as added when baseline is empty."""
        baseline = self._create_logs_miner_with_clusters([])
        miner = self._create_logs_miner_with_clusters(["template1", "template2"])

        missing, added, common = LogsMiner.diff_baseline(baseline, miner)

        assert missing == []
        assert set(added) == {"template1", "template2"}
        assert common == []

    def test_diff_baseline_empty_miner(self) -> None:
        """Should return all baseline clusters as missing when miner is empty."""
        baseline = self._create_logs_miner_with_clusters(["template1", "template2"])
        miner = self._create_logs_miner_with_clusters([])

        missing, added, common = LogsMiner.diff_baseline(baseline, miner)

        assert set(missing) == {"template1", "template2"}
        assert added == []
        assert common == []

    def test_diff_baseline_both_empty(self) -> None:
        """Should return all empty lists when both miners are empty."""
        baseline = self._create_logs_miner_with_clusters([])
        miner = self._create_logs_miner_with_clusters([])

        missing, added, common = LogsMiner.diff_baseline(baseline, miner)

        assert missing == []
        assert added == []
        assert common == []

    def test_diff_baseline_returns_sorted_lists(self) -> None:
        """Should return sorted lists for all three results."""
        baseline = self._create_logs_miner_with_clusters(["z_template", "a_template", "m_template"])
        miner = self._create_logs_miner_with_clusters(["b_template", "a_template", "z_template"])

        missing, added, common = LogsMiner.diff_baseline(baseline, miner)

        # Check that all results are sorted
        assert missing == sorted(missing)
        assert added == sorted(added)
        assert common == sorted(common)
