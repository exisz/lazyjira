"""Tests for lazyjira.api module."""

import json
import os
from unittest.mock import patch, MagicMock

from lazyjira.api import jira_api, transition_issue


class TestJiraApi:
    """Test the low-level API client."""

    @patch("lazyjira.api.get_jira_url", return_value="https://test.atlassian.net")
    @patch("lazyjira.api.get_jira_email", return_value="test@example.com")
    @patch("lazyjira.api.get_token", return_value="test-token")
    @patch("lazyjira.api.urllib.request.urlopen")
    def test_get_request(self, mock_urlopen, mock_token, mock_email, mock_url):
        mock_resp = MagicMock()
        mock_resp.read.return_value = json.dumps({"key": "TEST-1"}).encode()
        mock_resp.status = 200
        mock_resp.__enter__ = lambda s: s
        mock_resp.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_resp

        result = jira_api("GET", "/rest/api/3/issue/TEST-1")
        assert result["key"] == "TEST-1"

    @patch("lazyjira.api.get_jira_url", return_value="https://test.atlassian.net")
    @patch("lazyjira.api.get_jira_email", return_value="test@example.com")
    @patch("lazyjira.api.get_token", return_value="test-token")
    @patch("lazyjira.api.urllib.request.urlopen")
    def test_post_request_with_data(self, mock_urlopen, mock_token, mock_email, mock_url):
        mock_resp = MagicMock()
        mock_resp.read.return_value = json.dumps({"issues": []}).encode()
        mock_resp.status = 200
        mock_resp.__enter__ = lambda s: s
        mock_resp.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_resp

        result = jira_api("POST", "/rest/api/3/search/jql", {"jql": "project = TEST"})
        assert "issues" in result


class TestTransitionIssue:
    """Test the transition helper."""

    @patch("lazyjira.api.jira_api")
    def test_transition_success(self, mock_api):
        mock_api.side_effect = [
            # GET current status (not at target yet)
            {"fields": {"status": {"name": "To Do"}}},
            # GET transitions
            {"transitions": [{"id": "31", "to": {"name": "In Progress"}}]},
            # POST transition
            {},
        ]
        assert transition_issue("TEST-1", "In Progress") is True

    @patch("lazyjira.api.jira_api")
    def test_transition_not_found(self, mock_api):
        mock_api.return_value = {
            "transitions": [{"id": "31", "to": {"name": "In Progress"}}]
        }
        assert transition_issue("TEST-1", "Nonexistent") is False
