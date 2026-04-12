"""Jira REST API client — zero external dependencies."""

from __future__ import annotations

import base64
import json
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Optional

from lazyjira.config import get_jira_email, get_jira_url, get_token


# Project type cache (populated on demand)
_project_type_cache: dict[str, str] = {}


def jira_api(
    method: str,
    path: str,
    data: Optional[dict] = None,
    params: Optional[dict] = None,
) -> dict[str, Any]:
    """Call Jira REST API. Returns parsed JSON response.

    On HTTP errors, returns ``{"error": True, "status": <code>, ...}``.
    """
    base_url = get_jira_url()
    url = f"{base_url}{path}"
    if params:
        url += "?" + urllib.parse.urlencode(params)

    body = json.dumps(data).encode() if data else None
    email = get_jira_email()
    token = get_token()
    creds = base64.b64encode(f"{email}:{token}".encode()).decode()

    req = urllib.request.Request(
        url,
        data=body,
        method=method,
        headers={
            "Authorization": f"Basic {creds}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req) as resp:
            resp_body = resp.read()
            if not resp_body:
                return {}
            return json.loads(resp_body)
    except urllib.error.HTTPError as e:
        err_body = e.read().decode()
        try:
            err_json = json.loads(err_body)
            return {"error": True, "status": e.code, "errors": err_json}
        except json.JSONDecodeError:
            return {"error": True, "status": e.code, "body": err_body[:500]}


def is_jpd(project_key: str) -> bool:
    """Detect whether a project is a Jira Product Discovery project."""
    key = project_key.upper()
    if key not in _project_type_cache:
        result = jira_api("GET", f"/rest/api/3/project/{key}")
        if result.get("error"):
            return False
        _project_type_cache[key] = result.get("projectTypeKey", "software")
    return _project_type_cache[key] == "product_discovery"


def transition_issue(key: str, target_status: str) -> bool:
    """Transition an issue to the target status. Returns True on success."""
    transitions = jira_api("GET", f"/rest/api/3/issue/{key}/transitions")
    if transitions.get("error"):
        return False

    for t in transitions.get("transitions", []):
        if t["to"]["name"].lower() == target_status.lower():
            result = jira_api(
                "POST",
                f"/rest/api/3/issue/{key}/transitions",
                {"transition": {"id": t["id"]}},
            )
            return not result.get("error")

    return False
