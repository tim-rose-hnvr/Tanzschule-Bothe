#!/usr/bin/env bash
# Startet die Marktanalyse lokal. macOS und Linux.
set -e
cd "$(dirname "$0")"
for p in python3 python py; do
  if command -v "$p" >/dev/null 2>&1; then
    exec "$p" serve.py "$@"
  fi
done
echo "Python wurde nicht gefunden. Bitte Python 3 installieren: https://www.python.org/downloads/" >&2
exit 1
