#!/bin/zsh
cd "$(dirname "$0")"
if command -v python3 >/dev/null 2>&1; then
  python3 server.py
else
  echo 'Python 3.10 or newer is required. Install it from https://www.python.org/downloads/ then reopen this launcher.'
fi
read '?Press Enter to close…'
