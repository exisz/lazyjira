# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 0.x     | ✅ Current          |

## Reporting a Vulnerability

If you discover a security vulnerability, please report it responsibly:

1. **Do NOT** open a public GitHub issue
2. Email: gotexis@users.noreply.github.com
3. Include a description and steps to reproduce

We will respond within 48 hours and work on a fix.

## Security Considerations

- lazyjira stores API tokens locally (`~/.config/lazyjira/token`)
- Tokens are never logged or transmitted except to your configured Jira instance
- Always use HTTPS URLs for your Jira instance
- Restrict file permissions on your token file: `chmod 600 ~/.config/lazyjira/token`
