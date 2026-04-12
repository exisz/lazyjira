# lazyjira

> Zero-dependency CLI for Jira Cloud REST API.

**Work in progress — full README coming soon.**

## Quick Start

```bash
pip install lazyjira

# Configure
export JIRA_URL="https://your-instance.atlassian.net"
export JIRA_EMAIL="you@example.com"
export JIRA_API_TOKEN="your-api-token"

# Or use config file
mkdir -p ~/.config/lazyjira
cat > ~/.config/lazyjira/config.toml << EOF
[jira]
url = "https://your-instance.atlassian.net"
email = "you@example.com"
EOF
echo "your-api-token" > ~/.config/lazyjira/token

# Use it
lazyjira projects
lazyjira issues list -p MYPROJ
lazyjira issues create "Fix the bug" -p MYPROJ
lazyjira move MYPROJ-1 "In Progress"
```

## Features

- **Zero dependencies** — pure Python stdlib, no `requests`, no `click`
- **Full Jira Cloud REST API** — issues, comments, transitions, labels, links, JQL
- **Markdown ↔ ADF** — write descriptions in Markdown, auto-converted to Atlassian Document Format
- **JPD support** — auto-detects Jira Product Discovery projects
- **Config flexibility** — env vars, config file, or token file

## License

MIT
