"""Move / transition command."""

from __future__ import annotations

import json
import sys
from typing import Any

from lazyjira.api import jira_api, transition_issue


def cmd_move(args: Any) -> None:
    """Transition an issue to a new status."""
    success = transition_issue(args.key, args.status)
    if success:
        print(f"✅ {args.key} → {args.status}")
    else:
        print(f"❌ Could not transition {args.key} to '{args.status}'", file=sys.stderr)
        transitions = jira_api("GET", f"/rest/api/3/issue/{args.key}/transitions")
        if not transitions.get("error"):
            avail = [t["to"]["name"] for t in transitions.get("transitions", [])]
            print(f"Available transitions: {', '.join(avail)}", file=sys.stderr)
        sys.exit(1)
