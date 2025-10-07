#!/usr/bin/env bash

set -euo pipefail

# Detect repo dir based on this script location
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

# Detect runtime context
RUN_USER="${SUDO_USER:-$(whoami)}"
RUN_GROUP="$(id -gn "$RUN_USER")"

# Capture current terminal's python before escalating to root
detect_shell_python_pre_sudo() {
  # 1) Honor explicit override
  if [[ -n "${PYTHON_BIN:-}" ]] && [[ -x "${PYTHON_BIN}" ]]; then
    echo "$PYTHON_BIN"; return 0;
  fi

  # 2) Current shell executable (best for activated conda)
  local p
  p=$(python -c 'import sys;print(sys.executable)' 2>/dev/null || true)
  if [[ -n "$p" ]] && [[ -x "$p" ]]; then
    echo "$p"; return 0;
  fi

  # 3) PATH fallbacks in current shell
  p=$(command -v python 2>/dev/null || true)
  if [[ -n "$p" ]] && [[ -x "$p" ]]; then
    echo "$p"; return 0;
  fi
  p=$(command -v python3 2>/dev/null || true)
  if [[ -n "$p" ]] && [[ -x "$p" ]]; then
    echo "$p"; return 0;
  fi

  echo ""; return 1;
}

# Prefer the caller's conda/mamba/micromamba env python if available
detect_user_python() {
  # 1) Honor explicit override
  if [[ -n "${PYTHON_BIN:-}" ]] && [[ -x "${PYTHON_BIN}" ]]; then
    echo "$PYTHON_BIN"; return 0;
  fi

  # 2) Prefer current terminal's active python (captures conda/mamba already activated in this shell)
  local p
  p=$(python -c 'import sys;print(sys.executable)' 2>/dev/null || true)
  if [[ -n "$p" ]] && [[ -x "$p" ]]; then
    echo "$p"; return 0;
  fi

  # 3) Try current terminal PATH python
  p=$(command -v python 2>/dev/null || true)
  if [[ -n "$p" ]] && [[ -x "$p" ]]; then
    echo "$p"; return 0;
  fi

  p=$(command -v python3 2>/dev/null || true)
  if [[ -n "$p" ]] && [[ -x "$p" ]]; then
    echo "$p"; return 0;
  fi

  # 4) Try original user's login shell python (in case script is run with sudo without -E)
  local p
  p=$(sudo -u "$RUN_USER" -H bash -lc 'python -c "import sys;print(sys.executable)"' 2>/dev/null || true)
  if [[ -n "$p" ]] && [[ -x "$p" ]]; then
    echo "$p"; return 0;
  fi

  # 5) Try original user's PATH python
  p=$(sudo -u "$RUN_USER" -H bash -lc 'command -v python' 2>/dev/null || true)
  if [[ -n "$p" ]] && [[ -x "$p" ]]; then
    echo "$p"; return 0;
  fi

  p=$(sudo -u "$RUN_USER" -H bash -lc 'command -v python3' 2>/dev/null || true)
  if [[ -n "$p" ]] && [[ -x "$p" ]]; then
    echo "$p"; return 0;
  fi

  # 6) Fallback to system
  if command -v python3 >/dev/null 2>&1; then
    command -v python3; return 0;
  fi
  if command -v python >/dev/null 2>&1; then
    command -v python; return 0;
  fi

  echo ""; return 1;
}

if [[ "${EUID:-$(id -u)}" -ne 0 ]]; then
  # Not root: resolve python in THIS terminal first, then re-exec with sudo preserving it
  PYTHON_FROM_SHELL="$(detect_shell_python_pre_sudo || true)"
  if [[ -z "${PYTHON_FROM_SHELL}" ]]; then
    echo "Failed to detect Python from current shell. Try activating your env or set PYTHON_BIN." >&2
    exit 1
  fi
  echo "Re-executing with sudo using current shell python: ${PYTHON_FROM_SHELL}"
  exec sudo -E PYTHON_BIN="${PYTHON_FROM_SHELL}" bash "$0" "$@"
fi

PYTHON_BIN="$(detect_user_python)"
if [[ -z "$PYTHON_BIN" ]]; then
  echo "Failed to detect a Python interpreter. Set PYTHON_BIN explicitly." >&2
  exit 1
fi

# Service names
QQBOT_SERVICE="qqbot.service"
SDUAPI_SERVICE="sduapi.service"

# Output paths
SYSTEMD_DIR="/etc/systemd/system"
OUT_QQBOT="$SYSTEMD_DIR/$QQBOT_SERVICE"
OUT_SDUAPI="$SYSTEMD_DIR/$SDUAPI_SERVICE"

echo "Using repo: $REPO_DIR"
echo "Using python: $PYTHON_BIN"
echo "Target services: $OUT_QQBOT, $OUT_SDUAPI"

require_root() {
  if [[ "${EUID:-$(id -u)}" -ne 0 ]]; then
    echo "This script needs root to write systemd unit files. Re-run with sudo." >&2
    exit 1;
  fi
}

write_units() {
  # qqbot.service
  cat > "$OUT_QQBOT" <<EOF
[Unit]
Description=QQ Bot Scheduler Service
After=network.target
Wants=network.target

[Service]
Type=simple
User=$RUN_USER
Group=$RUN_GROUP
WorkingDirectory=$REPO_DIR/src/main
ExecStart=$PYTHON_BIN $REPO_DIR/src/main/main.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

# Environment
Environment=PYTHONUNBUFFERED=1
Environment=PYTHONPATH=$REPO_DIR/src/main:$REPO_DIR

# Security
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ReadWritePaths=$REPO_DIR

[Install]
WantedBy=multi-user.target
EOF

  # sduapi.service
  cat > "$OUT_SDUAPI" <<EOF
[Unit]
Description=SDU DeepSeek API Service
After=network.target
Wants=network.target

[Service]
Type=simple
User=$RUN_USER
Group=$RUN_GROUP
WorkingDirectory=$REPO_DIR/src/SDU_DeepSeek
ExecStart=$PYTHON_BIN $REPO_DIR/src/SDU_DeepSeek/main.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

# Environment
Environment=PYTHONUNBUFFERED=1
Environment=PYTHONPATH=$REPO_DIR/src/SDU_DeepSeek:$REPO_DIR

# Security
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ReadWritePaths=$REPO_DIR

[Install]
WantedBy=multi-user.target
EOF
}

reload_systemd() {
  systemctl daemon-reload
}

maybe_enable_start() {
  local unit="$1"
  if [[ "${ENABLE_START:-1}" == "1" ]]; then
    systemctl enable "$unit"
    systemctl restart "$unit"
  fi
}

main() {
  require_root
  write_units
  reload_systemd
  echo "Generated: $OUT_QQBOT"
  echo "Generated: $OUT_SDUAPI"
  if [[ "${AUTO_START:-0}" == "1" ]]; then
    maybe_enable_start "$QQBOT_SERVICE"
    maybe_enable_start "$SDUAPI_SERVICE"
    echo "Services enabled and restarted."
  else
    echo "You can now enable/start services:"
    echo "  sudo systemctl enable $QQBOT_SERVICE && sudo systemctl restart $QQBOT_SERVICE"
    echo "  sudo systemctl enable $SDUAPI_SERVICE && sudo systemctl restart $SDUAPI_SERVICE"
    echo "(Or run with AUTO_START=1 to do this automatically)"
  fi
}

main "$@"


