"""Tests for lazyjira.config module."""

import os
import tempfile
from unittest.mock import patch

from lazyjira.config import _parse_toml_simple, get_token


class TestParseToml:
    def test_basic_config(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=False) as f:
            f.write('[jira]\nurl = "https://test.atlassian.net"\nemail = "test@example.com"\n')
            f.flush()
            result = _parse_toml_simple(f.name)
        os.unlink(f.name)
        assert result["jira"]["url"] == "https://test.atlassian.net"
        assert result["jira"]["email"] == "test@example.com"

    def test_missing_file(self):
        result = _parse_toml_simple("/nonexistent/path.toml")
        assert result == {}

    def test_comments_ignored(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=False) as f:
            f.write('# comment\n[section]\nkey = "value"\n')
            f.flush()
            result = _parse_toml_simple(f.name)
        os.unlink(f.name)
        assert result["section"]["key"] == "value"


class TestGetToken:
    @patch.dict(os.environ, {"JIRA_API_TOKEN": "env-token"})
    def test_env_var(self):
        assert get_token() == "env-token"

    def test_token_file(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".token", delete=False) as f:
            f.write("file-token\n")
            f.flush()
            with patch("lazyjira.config.TOKEN_FILE", f.name), \
                 patch.dict(os.environ, {}, clear=True):
                # Clear JIRA_API_TOKEN if it exists in env
                os.environ.pop("JIRA_API_TOKEN", None)
                assert get_token() == "file-token"
        os.unlink(f.name)
