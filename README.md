<div align="center">

```
 _                     _  _
| |  __ _  ____ _   _ (_)(_) _ __  __ _
| | / _` ||_  /| | | || || || '__|/ _` |
| || (_| | / / | |_| || || || |  | (_| |
|_| \__,_|/___| \__, ||_||_||_|   \__,_|
                 |___/
```

**Like lazygit, but for Jira. Zero-dependency CLI that makes Jira bearable.**

[![PyPI](https://img.shields.io/pypi/v/lazyjira)](https://pypi.org/project/lazyjira/)
[![Python](https://img.shields.io/pypi/pyversions/lazyjira)](https://pypi.org/project/lazyjira/)
[![License](https://img.shields.io/github/license/gotexis/lazyjira)](LICENSE)
[![CI](https://img.shields.io/github/actions/workflow/status/gotexis/lazyjira/ci.yml)](https://github.com/gotexis/lazyjira/actions)

[Installation](#installation) · [Quick Start](#quick-start) · [Commands](#commands) · [Configuration](#configuration) · [Contributing](CONTRIBUTING.md)

</div>

---

## Why lazyjira?

Jira's web UI is slow. Existing CLIs are either abandoned, heavy, or missing features you need.

| | lazyjira | [jira-cli](https://github.com/ankitpokhrel/jira-cli) | [go-jira](https://github.com/go-jira/jira) |
|---|---|---|---|
| **Language** | Python | Go | Go |
| **Dependencies** | **0** (pure stdlib) | Multiple | Multiple |
| **Install** | `pip install lazyjira` | `brew` / `go install` | `go install` |
| **Status** | 🟢 Active | 🟢 Active | 🔴 Abandoned |
| **Jira Cloud** | ✅ | ✅ | ✅ |
| **JPD Support** | ✅ | ❌ | ❌ |
| **Markdown → ADF** | ✅ Built-in | ❌ | ❌ |
| **Config** | env / TOML / token file | YAML | YAML |

**Zero dependencies** means no `requests`, no `click`, no `rich` — just Python's standard library. Install it anywhere Python runs. No compiling, no cgo, no nonsense.

## Installation

```bash
# PyPI (recommended)
pip install lazyjira

# pipx (isolated install)
pipx install lazyjira

# One-liner
curl -fsSL https://raw.githubusercontent.com/gotexis/lazyjira/main/install.sh | bash

# From source
git clone https://github.com/gotexis/lazyjira.git
cd lazyjira
pip install .
```

<!--
# Homebrew (coming soon)
brew install gotexis/tap/lazyjira

# Chocolatey (coming soon)
choco install lazyjira
-->

## Quick Start

**1. Configure your credentials:**

```bash
export JIRA_URL="https://your-instance.atlassian.net"
export JIRA_EMAIL="you@example.com"
export JIRA_API_TOKEN="your-api-token"
```

Or use a config file (see [Configuration](#configuration)).

**2. List your projects:**

```bash
lazyjira projects
```

**3. Start working:**

```bash
# Search issues
lazyjira issues list -p MYPROJ

# Create an issue
lazyjira issues create "Fix login timeout" -p MYPROJ -d "Users report 30s delays"

# Move to In Progress
lazyjira move MYPROJ-42 "In Progress"

# Add a comment
lazyjira comments create MYPROJ-42 --body "Root cause found: connection pool exhaustion"
```

## Commands

### Issues

```bash
lazyjira issues list -p PROJECT          # List issues (table format)
lazyjira issues list -p PROJECT --plain  # List issues (JSON)
lazyjira issues search "login bug" -p P  # Full-text search
lazyjira issues read PROJ-123           # Read full issue details
lazyjira issues create TITLE -p PROJECT  # Create issue
lazyjira issues update KEY --summary X   # Update fields
lazyjira issues status KEY "Done"        # Transition status
lazyjira issues comment KEY --body "..."  # Quick comment
```

**Filtering:**

```bash
lazyjira issues list -p PROJ --status "In Progress"
lazyjira issues list -p PROJ --status-in "To Do,In Progress"
lazyjira issues list -p PROJ --status-ne "Done"
lazyjira issues list -p PROJ --label bug --assignee me
lazyjira issues list -p PROJ --priority 1     # Highest only
lazyjira issues list -p PROJ --order "created DESC"
lazyjira issues list -p PROJ --limit 10
```

### Comments

```bash
lazyjira comments create KEY --body "text"   # Add comment
lazyjira comments list KEY                   # List comments
```

### Transitions

```bash
lazyjira move KEY "In Progress"    # Transition issue
lazyjira move KEY "Done"           # Close issue
```

### Other

```bash
lazyjira projects                  # List all projects
lazyjira labels -p PROJECT         # List labels in project
lazyjira link PROJ-1 PROJ-2       # Link two issues
lazyjira link PROJ-1 PROJ-2 -t "is blocked by"
lazyjira open PROJ-123            # Open in browser
lazyjira query "project=X AND status='To Do' ORDER BY priority"  # Raw JQL
```

### Issue Creation — Full Options

```bash
lazyjira issues create "Title" \
  -p PROJECT \
  -d "Description in **markdown** — auto-converted to ADF" \
  --type Story \
  --priority 2 \
  --labels bug urgent \
  --parent PROJ-100 \
  --status "In Progress" \
  --duedate 2025-12-31
```

## Configuration

lazyjira resolves configuration in this order:

### 1. Environment Variables (highest priority)

```bash
export JIRA_URL="https://your-instance.atlassian.net"
export JIRA_EMAIL="you@example.com"
export JIRA_API_TOKEN="your-api-token"
export JIRA_PROJECT="MYPROJ"   # optional default project
```

### 2. Config File

```bash
mkdir -p ~/.config/lazyjira
cat > ~/.config/lazyjira/config.toml << 'EOF'
[jira]
url = "https://your-instance.atlassian.net"
email = "you@example.com"

[defaults]
project = "MYPROJ"
EOF
```

### 3. Token File

```bash
echo "your-api-token" > ~/.config/lazyjira/token
chmod 600 ~/.config/lazyjira/token
```

> 💡 **Tip:** Generate your API token at [id.atlassian.com/manage-profile/security/api-tokens](https://id.atlassian.com/manage-profile/security/api-tokens)

## Markdown → ADF

lazyjira automatically converts Markdown to [Atlassian Document Format](https://developer.atlassian.com/cloud/jira/platform/apis/document/structure/) when creating or updating descriptions and comments.

Write this:

```bash
lazyjira issues create "Fix bug" -p PROJ -d "## Steps\n1. Open the app\n2. Click **login**\n3. See error"
```

Jira sees properly formatted headings, lists, and bold text — not raw markdown.

## JPD Support

lazyjira auto-detects [Jira Product Discovery](https://www.atlassian.com/software/jira/product-discovery) projects and handles their unique issue types and workflows. No extra configuration needed.

## Shell Completion

```bash
# Bash
eval "$(register-python-argcomplete lazyjira 2>/dev/null)" || true

# Or add to ~/.bashrc for persistence
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup, code style, and PR guidelines.

## License

[MIT](LICENSE) © [Exis Z](https://github.com/gotexis)
