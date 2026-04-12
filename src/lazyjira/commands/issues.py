"""Issue CRUD commands."""

from __future__ import annotations

import json
import re
import sys
from typing import Any

from lazyjira.api import jira_api, transition_issue
from lazyjira.config import get_jira_url
from lazyjira.format import adf_to_text, markdown_to_adf


def _resolve_project(args) -> str:
    """Get project key from args — required."""
    from lazyjira.config import get_default_project

    project = getattr(args, "project", None) or get_default_project()
    if not project:
        print(
            "Error: --project / -p is required. Specify a project key (e.g. -p MYPROJ).",
            file=sys.stderr,
        )
        sys.exit(1)
    return project


def _get_default_issue_type(project_key: str) -> str:
    """Auto-detect default issue type for a project."""
    result = jira_api("GET", f"/rest/api/3/issue/createmeta/{project_key}/issuetypes")
    if not result.get("error"):
        types = result.get("issueTypes", result.get("values", []))
        type_names = [t["name"] for t in types]
        if "Idea" in type_names:
            return "Idea"
        if "Task" in type_names:
            return "Task"
        if type_names:
            return type_names[0]
    return "Task"


def cmd_issues(args: Any) -> None:
    sub = args.sub_command
    dispatch = {
        "read": cmd_issue_read,
        "search": cmd_issue_search,
        "create": cmd_issue_create,
        "update": cmd_issue_update,
        "list": cmd_issue_list,
        "status": cmd_move,
        "comment": cmd_comment_create,
    }
    fn = dispatch.get(sub)
    if fn:
        fn(args)
    else:
        print(f"Unknown issues subcommand: {sub}", file=sys.stderr)
        sys.exit(1)


def cmd_issue_read(args: Any) -> None:
    """Read a single issue with full details."""
    key = args.key
    result = jira_api(
        "GET",
        f"/rest/api/3/issue/{key}",
        params={
            "fields": "summary,description,status,priority,labels,comment,assignee,"
            "reporter,created,updated,resolutiondate,issuetype,parent",
            "expand": "names",
        },
    )
    if result.get("error"):
        print(f"Error: {json.dumps(result, indent=2)}", file=sys.stderr)
        sys.exit(1)

    fields = result.get("fields", {})
    base_url = get_jira_url()
    output: dict[str, Any] = {
        "key": result["key"],
        "id": result["id"],
        "url": f"{base_url}/browse/{result['key']}",
        "summary": fields.get("summary", ""),
        "status": fields.get("status", {}).get("name", ""),
        "priority": fields.get("priority", {}).get("name", ""),
        "type": fields.get("issuetype", {}).get("name", ""),
        "labels": fields.get("labels", []),
        "assignee": (fields.get("assignee") or {}).get("displayName"),
        "reporter": (fields.get("reporter") or {}).get("displayName"),
        "created": fields.get("created"),
        "updated": fields.get("updated"),
        "resolved": fields.get("resolutiondate"),
        "parent": (fields.get("parent") or {}).get("key"),
    }

    desc = fields.get("description")
    if desc and isinstance(desc, dict):
        output["description"] = adf_to_text(desc)
    elif desc:
        output["description"] = str(desc)
    else:
        output["description"] = ""

    comments_data = fields.get("comment", {}).get("comments", [])
    output["comments"] = []
    for c in comments_data:
        body_text = adf_to_text(c.get("body", {})) if isinstance(c.get("body"), dict) else str(c.get("body", ""))
        output["comments"].append(
            {
                "author": c.get("author", {}).get("displayName", "Unknown"),
                "created": c.get("created"),
                "body": body_text,
            }
        )

    print(json.dumps(output, indent=2, ensure_ascii=False))


def cmd_issue_search(args: Any) -> None:
    """Search issues via JQL."""
    project = _resolve_project(args)
    jql_parts = [f"project = {project}"]

    if args.query:
        jql_parts.append(f'text ~ "{args.query}"')
    if args.status:
        jql_parts.append(f'status = "{args.status}"')
    if getattr(args, "status_ne", None):
        jql_parts.append(f'status != "{args.status_ne}"')
    if getattr(args, "status_in", None):
        vals = ", ".join(f'"{v.strip()}"' for v in args.status_in.split(","))
        jql_parts.append(f"status IN ({vals})")
    if getattr(args, "status_nin", None):
        vals = ", ".join(f'"{v.strip()}"' for v in args.status_nin.split(","))
        jql_parts.append(f"status NOT IN ({vals})")
    if args.label:
        jql_parts.append(f'labels = "{args.label}"')
    if args.assignee:
        jql_parts.append(f'assignee = "{args.assignee}"')
    if args.priority:
        pmap = {"1": "Highest", "2": "High", "3": "Medium", "4": "Low"}
        pname = pmap.get(args.priority, args.priority)
        jql_parts.append(f'priority = "{pname}"')

    jql = " AND ".join(jql_parts)
    jql += f" ORDER BY {args.order}" if args.order else " ORDER BY created DESC"

    wanted = args.limit or 50
    all_issues: list[dict] = []
    next_page_token = None
    page_size = min(wanted, 100)

    while len(all_issues) < wanted:
        payload: dict[str, Any] = {
            "jql": jql,
            "maxResults": page_size,
            "fields": ["summary", "status", "priority", "labels", "assignee"],
        }
        if next_page_token:
            payload["nextPageToken"] = next_page_token

        result = jira_api("POST", "/rest/api/3/search/jql", payload)
        if result.get("error"):
            print(f"Error: {json.dumps(result, indent=2)}", file=sys.stderr)
            sys.exit(1)

        batch = result.get("issues", [])
        all_issues.extend(batch)
        next_page_token = result.get("nextPageToken")
        if not next_page_token or len(batch) < page_size:
            break

    issues = []
    for issue in all_issues[:wanted]:
        f = issue["fields"]
        issues.append(
            {
                "key": issue["key"],
                "summary": f.get("summary", ""),
                "status": f.get("status", {}).get("name", ""),
                "priority": f.get("priority", {}).get("name", ""),
                "labels": f.get("labels", []),
                "assignee": (f.get("assignee") or {}).get("displayName"),
            }
        )

    print(json.dumps(issues, indent=2, ensure_ascii=False))

    # Write cache if requested
    if getattr(args, "update_cache", None):
        try:
            from datetime import datetime, timezone

            cache_lines = [
                "# Auto-generated by lazyjira search --update-cache",
                f"# Updated: {datetime.now(timezone.utc).isoformat()}",
                "# Format: KEY | STATUS | SUMMARY",
                "",
            ]
            for issue in issues:
                cache_lines.append(f"{issue['key']} | {issue['status']} | {issue['summary']}")
            with open(args.update_cache, "w") as cf:
                cf.write("\n".join(cache_lines) + "\n")
            print(f"Cache written: {args.update_cache} ({len(issues)} issues)", file=sys.stderr)
        except Exception as e:
            print(f"Warning: failed to write cache: {e}", file=sys.stderr)


def cmd_issue_list(args: Any) -> None:
    """List issues with tabular or JSON output."""
    if not hasattr(args, "query"):
        args.query = ""
    if args.plain:
        cmd_issue_search(args)
        return

    project = _resolve_project(args)
    jql_parts = [f"project = {project}"]

    if args.status:
        jql_parts.append(f'status = "{args.status}"')
    if getattr(args, "status_ne", None):
        jql_parts.append(f'status != "{args.status_ne}"')
    if getattr(args, "status_in", None):
        vals = ", ".join(f'"{v.strip()}"' for v in args.status_in.split(","))
        jql_parts.append(f"status IN ({vals})")
    if getattr(args, "status_nin", None):
        vals = ", ".join(f'"{v.strip()}"' for v in args.status_nin.split(","))
        jql_parts.append(f"status NOT IN ({vals})")
    if args.assignee:
        jql_parts.append(f'assignee = "{args.assignee}"')
    if args.label:
        jql_parts.append(f'labels = "{args.label}"')
    if hasattr(args, "query") and args.query:
        jql_parts.append(args.query)

    jql = " AND ".join(jql_parts) + " ORDER BY created DESC"
    limit = args.limit or 50

    result = jira_api(
        "POST",
        "/rest/api/3/search/jql",
        {"jql": jql, "maxResults": limit, "fields": ["summary", "status", "issuetype"]},
    )
    issues = result.get("issues", [])
    if not issues:
        print("No issues found.")
        return

    print(f"{'TYPE':<12s} {'KEY':<14s} {'SUMMARY':<80s} {'STATUS'}")
    for issue in issues:
        f = issue["fields"]
        itype = f.get("issuetype", {}).get("name", "")
        key = issue["key"]
        summary = f.get("summary", "")
        status = f.get("status", {}).get("name", "")
        print(f"{itype:<12s} {key:<14s} {summary:<80s} {status}")


def cmd_issue_create(args: Any) -> None:
    """Create an issue."""
    project = _resolve_project(args)
    issue_type = args.type or _get_default_issue_type(project)

    desc_adf = None
    if args.description:
        desc_adf = markdown_to_adf(args.description)

    fields: dict[str, Any] = {
        "project": {"key": project},
        "summary": args.title,
        "issuetype": {"name": issue_type},
    }

    if desc_adf:
        fields["description"] = desc_adf
    if args.priority:
        pmap = {"1": "1", "2": "2", "3": "3", "4": "4"}
        fields["priority"] = {"id": pmap.get(str(args.priority), "3")}
    if args.labels:
        expanded = []
        for lbl in args.labels:
            expanded.extend(part.strip() for part in lbl.split(",") if part.strip())
        fields["labels"] = expanded
    if args.assignee:
        fields["assignee"] = {"id": args.assignee}
    if args.parent:
        fields["parent"] = {"key": args.parent}

    # Auto-set dates for Jira Calendar visibility
    from datetime import date

    today = date.today().isoformat()
    fields["customfield_10015"] = today  # Start date
    fields["duedate"] = getattr(args, "duedate", None) or today

    base_url = get_jira_url()
    result = jira_api("POST", "/rest/api/3/issue", {"fields": fields})

    # Retry without start date if field doesn't exist
    if result.get("error") or result.get("errors"):
        err_str = json.dumps(result.get("errors", {}))
        if "customfield_10015" in err_str:
            del fields["customfield_10015"]
            result = jira_api("POST", "/rest/api/3/issue", {"fields": fields})

    if result.get("error"):
        err_str = json.dumps(result.get("errors", {}))
        if "issuetype" in err_str.lower() or "issue type" in err_str.lower():
            types_result = jira_api("GET", f"/rest/api/3/issue/createmeta/{project}/issuetypes")
            if not types_result.get("error"):
                types = types_result.get("issueTypes", types_result.get("values", []))
                type_names = [t["name"] for t in types]
                print(f"Error: issue type '{issue_type}' not valid for {project}.", file=sys.stderr)
                print(f"Available types: {', '.join(type_names)}", file=sys.stderr)
                sys.exit(1)
        print(f"Error creating issue: {json.dumps(result, indent=2)}", file=sys.stderr)
        sys.exit(1)

    issue_key = result["key"]
    print(
        json.dumps(
            {"key": issue_key, "id": result.get("id"), "url": f"{base_url}/browse/{issue_key}"},
            indent=2,
        )
    )

    if args.status and args.status not in ("To Do", "Backlog"):
        transition_issue(issue_key, args.status)


def cmd_issue_update(args: Any) -> None:
    """Update an issue."""
    key = args.key

    if args.status:
        success = transition_issue(key, args.status)
        if success:
            print(f"✅ {key} → {args.status}")
        else:
            print(f"❌ {key}: could not transition to {args.status}", file=sys.stderr)
            sys.exit(1)

    direct_fields: dict[str, Any] = {}
    if getattr(args, "description", None):
        direct_fields["description"] = markdown_to_adf(args.description)

    update_fields: dict[str, Any] = {}
    if args.summary:
        update_fields["summary"] = [{"set": args.summary}]
    if args.labels_add:
        expanded = []
        for lbl in args.labels_add:
            expanded.extend(part.strip() for part in lbl.split(",") if part.strip())
        update_fields["labels"] = [{"add": lbl} for lbl in expanded]
    if args.labels_remove:
        expanded = []
        for lbl in args.labels_remove:
            expanded.extend(part.strip() for part in lbl.split(",") if part.strip())
        if "labels" not in update_fields:
            update_fields["labels"] = []
        update_fields["labels"].extend([{"remove": lbl} for lbl in expanded])
    if args.priority:
        pmap = {"1": "1", "2": "2", "3": "3", "4": "4"}
        update_fields["priority"] = [{"set": {"id": pmap.get(str(args.priority), "3")}}]

    if update_fields or direct_fields:
        payload: dict[str, Any] = {}
        if update_fields:
            payload["update"] = update_fields
        if direct_fields:
            payload["fields"] = direct_fields
        result = jira_api("PUT", f"/rest/api/3/issue/{key}", payload)
        if result.get("error"):
            print(f"Error: {json.dumps(result, indent=2)}", file=sys.stderr)
            sys.exit(1)
        print(f"✅ {key} updated")


# Import for cmd_move and cmd_comment_create used by alias dispatch
from lazyjira.commands.move import cmd_move
from lazyjira.commands.comments import cmd_comment_create
