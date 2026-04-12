"""lazyjira CLI — zero-dependency Jira Cloud CLI.

Usage:
    lazyjira issues read KEY
    lazyjira issues search [QUERY] -p PROJECT
    lazyjira issues create TITLE -p PROJECT
    lazyjira move KEY STATUS
    lazyjira comments create KEY --body TEXT
    ...

Full docs: https://github.com/gotexis/lazyjira
"""

from __future__ import annotations

import argparse
import sys
import webbrowser

from lazyjira import __version__
from lazyjira.config import get_jira_url


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="lazyjira",
        description="Zero-dependency CLI for Jira Cloud REST API",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    sub = parser.add_subparsers(dest="command", help="Available commands")

    # ── issues ──
    p_issues = sub.add_parser("issues", help="Issue operations")
    issues_sub = p_issues.add_subparsers(dest="sub_command")

    # issues read
    p_read = issues_sub.add_parser("read", help="Read full issue details")
    p_read.add_argument("key", help="Issue key (e.g. PROJ-123)")

    # issues search
    p_search = issues_sub.add_parser("search", help="Search issues via JQL")
    p_search.add_argument("query", nargs="?", default="", help="Text search query")
    p_search.add_argument("--project", "-p", help="Project key")
    p_search.add_argument("--status", "-s", help="Filter by status")
    p_search.add_argument("--status-ne", help="Exclude status (not equal)")
    p_search.add_argument("--status-in", help="Filter by statuses (comma-separated)")
    p_search.add_argument("--status-nin", help="Exclude statuses (comma-separated)")
    p_search.add_argument("--label", "-l", help="Filter by label")
    p_search.add_argument("--assignee", "-a", help="Filter by assignee")
    p_search.add_argument("--priority", help="Filter by priority (1-4)")
    p_search.add_argument("--order", help="JQL ORDER BY clause")
    p_search.add_argument("--limit", type=int, default=50, help="Max results (default: 50)")
    p_search.add_argument(
        "--update-cache", metavar="FILE", help="Write results to cache file"
    )

    # issues list
    p_list = issues_sub.add_parser("list", help="List issues (table or JSON)")
    p_list.add_argument("--project", "-p", help="Project key")
    p_list.add_argument("--status", "-s", help="Filter by status")
    p_list.add_argument("--status-ne", help="Exclude status (not equal)")
    p_list.add_argument("--status-in", help="Filter by statuses (comma-separated)")
    p_list.add_argument("--status-nin", help="Exclude statuses (comma-separated)")
    p_list.add_argument("--label", "-l", help="Filter by label")
    p_list.add_argument("--assignee", "-a", help="Filter by assignee")
    p_list.add_argument("--priority", help="Filter by priority")
    p_list.add_argument("--limit", type=int, help="Max results")
    p_list.add_argument("--plain", action="store_true", help="Plain JSON output")
    p_list.add_argument("--order", help="JQL ORDER BY clause")

    # issues create
    p_create = issues_sub.add_parser("create", help="Create a new issue")
    p_create.add_argument("title", help="Issue summary/title")
    p_create.add_argument("-d", "--description", help="Issue description (markdown)")
    p_create.add_argument("--project", "-p", help="Project key")
    p_create.add_argument("--status", "-s", help="Initial status (transitions after creation)")
    p_create.add_argument("--priority", type=int, help="Priority (1=Highest, 4=Low)")
    p_create.add_argument("--labels", "-l", nargs="+", help="Labels")
    p_create.add_argument(
        "--type", "-t", default=None, help="Issue type (auto-detected if omitted)"
    )
    p_create.add_argument("--assignee", help="Assignee account ID")
    p_create.add_argument("--parent", help="Parent issue key")
    p_create.add_argument("--duedate", help="Due date (YYYY-MM-DD)")

    # issues update
    p_update = issues_sub.add_parser("update", help="Update an issue")
    p_update.add_argument("key", help="Issue key")
    p_update.add_argument("--status", "-s", help="Transition to status")
    p_update.add_argument("--summary", help="Update summary")
    p_update.add_argument("--priority", type=int, help="Priority (1=Highest, 4=Low)")
    p_update.add_argument("--description", "-d", help="Update description (markdown)")
    p_update.add_argument("--labels-add", nargs="+", help="Add labels")
    p_update.add_argument("--labels-remove", nargs="+", help="Remove labels")

    # issues status
    p_status = issues_sub.add_parser("status", help="Transition issue status")
    p_status.add_argument("key", help="Issue key")
    p_status.add_argument("status", help="Target status name")

    # issues comment
    p_icomment = issues_sub.add_parser("comment", help="Add a comment")
    p_icomment.add_argument("key", help="Issue key")
    p_icomment.add_argument("--body", "-b", required=True, help="Comment text")

    from lazyjira.commands.issues import cmd_issues

    p_issues.set_defaults(func=cmd_issues)

    # ── comments ──
    p_comments = sub.add_parser("comments", help="Comment operations")
    comments_sub = p_comments.add_subparsers(dest="sub_command")

    p_cc = comments_sub.add_parser("create", help="Add a comment")
    p_cc.add_argument("key", help="Issue key")
    p_cc.add_argument("--body", "-b", required=True, help="Comment text")

    p_ca = comments_sub.add_parser("add", help="Add a comment (alias)")
    p_ca.add_argument("key", help="Issue key")
    p_ca.add_argument("--body", "-b", required=True, help="Comment text")

    p_cl = comments_sub.add_parser("list", help="List comments")
    p_cl.add_argument("key", help="Issue key")

    from lazyjira.commands.comments import cmd_comments

    p_comments.set_defaults(func=cmd_comments)

    # ── move ──
    p_move = sub.add_parser("move", help="Transition issue to a status")
    p_move.add_argument("key", help="Issue key")
    p_move.add_argument("status", help="Target status name")

    from lazyjira.commands.move import cmd_move

    p_move.set_defaults(func=cmd_move)

    # ── labels ──
    p_labels = sub.add_parser("labels", help="List labels used in a project")
    p_labels.add_argument("--project", "-p", help="Project key")

    from lazyjira.commands.labels import cmd_labels

    p_labels.set_defaults(func=cmd_labels)

    # ── projects ──
    p_proj = sub.add_parser("projects", help="List all Jira projects")

    from lazyjira.commands.projects import cmd_projects

    p_proj.set_defaults(func=cmd_projects)

    # ── open ──
    p_open = sub.add_parser("open", help="Open issue in browser")
    p_open.add_argument("key", help="Issue key")

    def _cmd_open(args):
        base_url = get_jira_url()
        url = f"{base_url}/browse/{args.key}"
        webbrowser.open(url)
        print(f"Opened {url}")

    p_open.set_defaults(func=_cmd_open)

    # ── link ──
    p_link = sub.add_parser("link", help="Link two issues")
    p_link.add_argument("inward", help="Inward issue key")
    p_link.add_argument("outward", help="Outward issue key")
    p_link.add_argument("--type", "-t", default="Blocks", help="Link type (default: Blocks)")

    from lazyjira.commands.links import cmd_link

    p_link.set_defaults(func=cmd_link)

    # ── query ──
    p_query = sub.add_parser("query", help="Run raw JQL query")
    p_query.add_argument("jql", help="JQL query string")
    p_query.add_argument("--fields", "-f", help="Comma-separated field names")
    p_query.add_argument("--limit", type=int, default=50, help="Max results")

    from lazyjira.commands.query import cmd_query

    p_query.set_defaults(func=cmd_query)

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)
    args.func(args)


if __name__ == "__main__":
    main()
