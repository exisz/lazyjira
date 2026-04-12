"""Comment commands."""

from __future__ import annotations

import json
import sys
from typing import Any

from lazyjira.api import jira_api
from lazyjira.format import adf_to_text, markdown_to_adf


def cmd_comments(args: Any) -> None:
    sub = args.sub_command
    if sub in ("create", "add"):
        cmd_comment_create(args)
    elif sub == "list":
        cmd_comment_list(args)
    else:
        print(f"Unknown comments subcommand: {sub}", file=sys.stderr)
        sys.exit(1)


def cmd_comment_create(args: Any) -> None:
    """Add a comment to an issue."""
    body_adf = markdown_to_adf(args.body)
    result = jira_api("POST", f"/rest/api/3/issue/{args.key}/comment", {"body": body_adf})
    if result.get("error"):
        print(f"Error: {json.dumps(result, indent=2)}", file=sys.stderr)
        sys.exit(1)
    print(f"✅ Comment added to {args.key}")


def cmd_comment_list(args: Any) -> None:
    """List comments on an issue."""
    result = jira_api("GET", f"/rest/api/3/issue/{args.key}/comment")
    if result.get("error"):
        print(f"Error: {json.dumps(result, indent=2)}", file=sys.stderr)
        sys.exit(1)
    comments = []
    for c in result.get("comments", []):
        body_text = adf_to_text(c.get("body", {})) if isinstance(c.get("body"), dict) else str(c.get("body", ""))
        comments.append(
            {
                "id": c["id"],
                "author": c.get("author", {}).get("displayName", "Unknown"),
                "created": c.get("created"),
                "body": body_text,
            }
        )
    print(json.dumps(comments, indent=2, ensure_ascii=False))
