"""Issue linking command."""

from __future__ import annotations

import json
import sys
from typing import Any

from lazyjira.api import jira_api


def cmd_link(args: Any) -> None:
    """Link two issues."""
    result = jira_api(
        "POST",
        "/rest/api/3/issueLink",
        {
            "type": {"name": args.type},
            "inwardIssue": {"key": args.inward},
            "outwardIssue": {"key": args.outward},
        },
    )
    if result.get("error"):
        print(f"Error: {json.dumps(result, indent=2)}", file=sys.stderr)
        sys.exit(1)
    print(f"✅ Linked {args.inward} {args.type} {args.outward}")
