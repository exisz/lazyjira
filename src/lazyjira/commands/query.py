"""Raw JQL query command."""

from __future__ import annotations

import json
from typing import Any

from lazyjira.api import jira_api


def cmd_query(args: Any) -> None:
    """Run a raw JQL query."""
    result = jira_api(
        "POST",
        "/rest/api/3/search/jql",
        {
            "jql": args.jql,
            "maxResults": args.limit or 50,
            "fields": args.fields.split(",") if args.fields else ["summary", "status", "priority"],
        },
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))
