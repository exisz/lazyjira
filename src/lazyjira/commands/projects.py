"""Project listing command."""

from __future__ import annotations

import json
import sys
from typing import Any

from lazyjira.api import jira_api


def cmd_projects(args: Any) -> None:
    """List all Jira projects."""
    result = jira_api("GET", "/rest/api/3/project/search", params={"maxResults": 50})
    if result.get("error"):
        print(f"Error: {json.dumps(result, indent=2)}", file=sys.stderr)
        sys.exit(1)
    for p in result.get("values", []):
        ptype = p.get("projectTypeKey", "software")
        ptype_label = "JPD" if ptype == "product_discovery" else ptype
        print(f"  {p['key']:<10s} {p['name']:<40s} type={ptype_label}")
