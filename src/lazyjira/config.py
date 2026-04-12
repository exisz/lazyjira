"""Configuration management for lazyjira.

Resolution order:
  1. Environment variables: JIRA_URL, JIRA_EMAIL, JIRA_API_TOKEN
  2. Config file: ~/.config/lazyjira/config.toml
  3. Token file: ~/.config/lazyjira/token (API token only)
"""

from __future__ import annotations

import os
import sys
from typing import Optional

CONFIG_DIR = os.path.expanduser("~/.config/lazyjira")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.toml")
TOKEN_FILE = os.path.join(CONFIG_DIR, "token")


def _parse_toml_simple(path: str) -> dict:
    """Minimal TOML parser — handles [section] and key = "value" only.

    We avoid external deps. This covers the config file format we define.
    """
    config: dict = {}
    current_section: Optional[str] = None
    try:
        with open(path) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if line.startswith("[") and line.endswith("]"):
                    current_section = line[1:-1].strip()
                    config.setdefault(current_section, {})
                elif "=" in line:
                    key, _, value = line.partition("=")
                    key = key.strip()
                    value = value.strip().strip('"').strip("'")
                    if current_section:
                        config[current_section][key] = value
                    else:
                        config[key] = value
    except FileNotFoundError:
        pass
    return config


def get_jira_url() -> str:
    """Return the Jira instance URL."""
    url = os.environ.get("JIRA_URL")
    if url:
        return url.rstrip("/")

    cfg = _parse_toml_simple(CONFIG_FILE)
    url = cfg.get("jira", {}).get("url") if isinstance(cfg.get("jira"), dict) else None
    if url:
        return url.rstrip("/")

    print(
        "Error: Jira URL not configured.\n"
        "Set JIRA_URL env var or add to ~/.config/lazyjira/config.toml:\n\n"
        "  [jira]\n"
        '  url = "https://your-instance.atlassian.net"\n',
        file=sys.stderr,
    )
    sys.exit(1)


def get_jira_email() -> str:
    """Return the Jira account email."""
    email = os.environ.get("JIRA_EMAIL")
    if email:
        return email

    cfg = _parse_toml_simple(CONFIG_FILE)
    email = cfg.get("jira", {}).get("email") if isinstance(cfg.get("jira"), dict) else None
    if email:
        return email

    print(
        "Error: Jira email not configured.\n"
        "Set JIRA_EMAIL env var or add to ~/.config/lazyjira/config.toml:\n\n"
        "  [jira]\n"
        '  email = "you@example.com"\n',
        file=sys.stderr,
    )
    sys.exit(1)


def get_token() -> str:
    """Return the Jira API token."""
    token = os.environ.get("JIRA_API_TOKEN")
    if token:
        return token

    # Check token file
    if os.path.isfile(TOKEN_FILE):
        with open(TOKEN_FILE) as f:
            token = f.read().strip()
        if token:
            return token

    # Legacy token file location
    legacy = os.path.expanduser("~/.jira_api_token")
    if os.path.isfile(legacy):
        with open(legacy) as f:
            token = f.read().strip()
        if token:
            return token

    print(
        "Error: Jira API token not found.\n"
        "Set JIRA_API_TOKEN env var, or save token to:\n"
        f"  {TOKEN_FILE}\n",
        file=sys.stderr,
    )
    sys.exit(1)


def get_default_project() -> Optional[str]:
    """Return the default project key, if configured."""
    project = os.environ.get("JIRA_PROJECT")
    if project:
        return project

    cfg = _parse_toml_simple(CONFIG_FILE)
    defaults = cfg.get("defaults", {})
    if isinstance(defaults, dict):
        return defaults.get("project")

    return None
