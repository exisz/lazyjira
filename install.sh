#!/usr/bin/env bash
set -euo pipefail

# ─────────────────────────────────────────────
#  lazyjira installer
#  https://github.com/gotexis/lazyjira
# ─────────────────────────────────────────────

VERSION="lazyjira"  # latest from PyPI

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m'

info()    { echo -e "${BLUE}==>${NC} ${BOLD}$1${NC}"; }
success() { echo -e "${GREEN}==>${NC} ${BOLD}$1${NC}"; }
warn()    { echo -e "${YELLOW}==>${NC} ${BOLD}$1${NC}"; }
error()   { echo -e "${RED}==>${NC} ${BOLD}$1${NC}" >&2; }

# ── Banner ──

echo -e "${BOLD}"
cat << 'BANNER'
 _                     _  _
| |  __ _  ____ _   _ (_)(_) _ __  __ _
| | / _` ||_  /| | | || || || '__|/ _` |
| || (_| | / / | |_| || || || |  | (_| |
|_| \__,_|/___| \__, ||_||_||_|   \__,_|
                 |___/
BANNER
echo -e "${NC}"
echo "  Zero-dependency CLI for Jira Cloud"
echo ""

# ── Detect OS ──

OS="$(uname -s)"
case "$OS" in
    Linux*)  PLATFORM="linux";;
    Darwin*) PLATFORM="macos";;
    MINGW*|MSYS*|CYGWIN*) PLATFORM="windows";;
    *)       PLATFORM="unknown";;
esac

info "Detected platform: $PLATFORM"

# ── Check Python ──

PYTHON=""
for cmd in python3 python; do
    if command -v "$cmd" &>/dev/null; then
        PY_VERSION=$("$cmd" -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')" 2>/dev/null || true)
        if [ -n "$PY_VERSION" ]; then
            PY_MAJOR=$(echo "$PY_VERSION" | cut -d. -f1)
            PY_MINOR=$(echo "$PY_VERSION" | cut -d. -f2)
            if [ "$PY_MAJOR" -ge 3 ] && [ "$PY_MINOR" -ge 9 ]; then
                PYTHON="$cmd"
                break
            fi
        fi
    fi
done

if [ -z "$PYTHON" ]; then
    error "Python 3.9+ is required but not found."
    echo ""
    echo "  Install Python:"
    case "$PLATFORM" in
        macos)   echo "    brew install python3";;
        linux)   echo "    sudo apt install python3  # or your distro's package manager";;
        windows) echo "    Download from https://python.org";;
    esac
    exit 1
fi

success "Found $PYTHON ($PY_VERSION)"

# ── Install ──

install_with_pip() {
    local pip_cmd="$1"
    # Try --user first, fall back to --break-system-packages for PEP 668 environments
    if $pip_cmd install --user "$VERSION" 2>/dev/null; then
        return 0
    fi
    warn "--user install failed, trying with --break-system-packages..."
    $pip_cmd install --user --break-system-packages "$VERSION"
}

if command -v pipx &>/dev/null; then
    info "Installing with pipx (isolated environment)..."
    pipx install "$VERSION"
elif command -v pip3 &>/dev/null; then
    info "Installing with pip3..."
    install_with_pip pip3
elif command -v pip &>/dev/null; then
    info "Installing with pip..."
    install_with_pip pip
else
    info "Installing with $PYTHON -m pip..."
    install_with_pip "$PYTHON -m pip"
fi

# ── Verify ──

echo ""
if command -v lazyjira &>/dev/null; then
    INSTALLED_VERSION=$(lazyjira --version 2>/dev/null || echo "unknown")
    success "lazyjira installed successfully! ($INSTALLED_VERSION)"
else
    # Check if it's in a path not yet sourced
    USER_BIN=""
    case "$PLATFORM" in
        macos|linux)
            USER_BIN="$HOME/.local/bin"
            ;;
    esac

    if [ -n "$USER_BIN" ] && [ -f "$USER_BIN/lazyjira" ]; then
        INSTALLED_VERSION=$("$USER_BIN/lazyjira" --version 2>/dev/null || echo "unknown")
        success "lazyjira installed successfully! ($INSTALLED_VERSION)"
        warn "Add $USER_BIN to your PATH:"
        echo ""
        echo "    export PATH=\"$USER_BIN:\$PATH\""
        echo ""
        echo "  Add that line to your ~/.bashrc, ~/.zshrc, or equivalent."
    else
        success "lazyjira package installed."
        warn "Binary not found in PATH. You may need to restart your shell."
    fi
fi

# ── Next Steps ──

echo ""
echo -e "${BOLD}Next steps:${NC}"
echo ""
echo "  1. Configure credentials:"
echo ""
echo "     export JIRA_URL=\"https://your-instance.atlassian.net\""
echo "     export JIRA_EMAIL=\"you@example.com\""
echo "     export JIRA_API_TOKEN=\"your-api-token\""
echo ""
echo "  2. Test it:"
echo ""
echo "     lazyjira projects"
echo ""
echo -e "  📖 Docs: ${BLUE}https://github.com/gotexis/lazyjira${NC}"
echo ""
