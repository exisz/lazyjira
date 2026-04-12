"""Tests for lazyjira CLI."""

import subprocess
import sys


def test_version():
    """lazyjira --version should print version string."""
    result = subprocess.run(
        [sys.executable, "-m", "lazyjira", "--version"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "0.1.0" in result.stdout


def test_help():
    """lazyjira --help should show help text."""
    result = subprocess.run(
        [sys.executable, "-m", "lazyjira", "--help"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "lazyjira" in result.stdout
    assert "issues" in result.stdout


def test_issues_help():
    """lazyjira issues --help should show issue subcommands."""
    result = subprocess.run(
        [sys.executable, "-m", "lazyjira", "issues", "--help"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "read" in result.stdout
    assert "create" in result.stdout
