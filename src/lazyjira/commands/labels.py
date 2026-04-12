"""Label commands."""

from __future__ import annotations

import json
import sys
from typing import Any

from lazyjira.api import jira_api


def cmd_labels(args: Any) -> None:
    """List labels used in a project."""
    from lazyjira.commands.issues import _resolve_project

    project = _resolve_project(args)
    result = jira_api(
        "POST",
        "/rest/api/3/search/jql",
        {
            "jql": f"project = {project} AND labels IS NOT EMPTY",
            "maxResults": 100,
            "fields": ["labels"],
        },
    )
    if result.get("error"):
        print(f"Error: {json.dumps(result, indent=2)}", file=sys.stderr)
        sys.exit(1)

    all_labels: set[str] = set()
    for issue in result.get("issues", []):
        for label in issue["fields"].get("labels", []):
            all_labels.add(label)

    for label in sorted(all_labels):
        print(f"  {label}")
