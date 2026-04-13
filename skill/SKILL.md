---
name: lazyjira
description: "Jira Cloud CLI via lazyjira — issue CRUD, transitions, JQL queries, comments, links. Zero dependencies."
---

# lazyjira — Jira Cloud CLI Skill

Use `lazyjira` CLI for all Jira operations. Zero-dependency Python CLI wrapping the Jira Cloud REST API.

## Setup

```bash
pip install lazyjira
```

## Configuration

Three ways to configure (resolution order):

### 1. Environment Variables (recommended for agents)
```bash
export JIRA_URL="https://your-instance.atlassian.net"
export JIRA_EMAIL="you@example.com"
export JIRA_API_TOKEN="your-api-token"
```

### 2. Config File
```toml
# ~/.config/lazyjira/config.toml
[jira]
url = "https://your-instance.atlassian.net"
email = "you@example.com"

[defaults]
project = "MYPROJ"  # optional default project
```

### 3. Token File
```bash
echo "your-api-token" > ~/.config/lazyjira/token
```

## Common Patterns

### Reading Issues
```bash
lazyjira issues read PROJ-123                              # Full issue + comments
lazyjira issues search "query" -p PROJ                     # Text search
lazyjira issues search "" -p PROJ --status-ne Done         # Exclude status
lazyjira issues search "" -p PROJ --status-in "To Do,QA"   # Include statuses
lazyjira issues list -p PROJ --plain                       # JSON output
```

### Creating & Updating
```bash
lazyjira issues create "Title" -d "Description" -p PROJ --priority 1
lazyjira issues create "Title" -p PROJ -t Bug              # Bug type
lazyjira issues create "Title" -p PROJ --parent PROJ-1     # Child issue
lazyjira issues update PROJ-123 --status "Engineering"
lazyjira issues update PROJ-123 --labels-add bug
```

### Status Transitions
```bash
lazyjira move PROJ-123 "In Progress"
lazyjira move PROJ-123 "Done"
```

### Comments
```bash
lazyjira comments create PROJ-123 --body "Fixed in commit abc123"
lazyjira comments list PROJ-123
```

### JQL Queries
```bash
lazyjira query 'project=PROJ AND status="To Do" ORDER BY priority ASC'
lazyjira query 'assignee=currentUser() AND status!="Done"' --limit 20
```

### Other
```bash
lazyjira projects                              # List all projects
lazyjira labels -p PROJ                        # List labels
lazyjira link PROJ-1 PROJ-2 --type Blocks      # Link issues
lazyjira open PROJ-123                         # Open in browser
```

## Key Features

- **Zero dependencies** — pure Python stdlib
- **Markdown → ADF** — write descriptions in Markdown, auto-converted
- **JPD support** — auto-detects Jira Product Discovery projects
- **Flexible config** — env vars, TOML file, or token file
- `-p`/`--project` is **required** for most commands (no hidden defaults)

## Issue Types

| Flag | Type | Use Case |
|------|------|----------|
| `-t Story` | Story | New feature |
| `-t Bug` | Bug | Something broken |
| `-t Task` | Task | Internal work (default) |
| `-t Epic` | Epic | Large initiative |

## Priority Levels

| Flag | Priority |
|------|----------|
| `--priority 1` | Highest |
| `--priority 2` | High |
| `--priority 3` | Medium |
| `--priority 4` | Low |

## Notes

- `lazyjira` uses Jira Cloud REST API v3
- API token: generate at https://id.atlassian.com/manage-profile/security/api-tokens
- Descriptions support full Markdown including tables, code blocks, and lists
