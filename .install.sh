#!/usr/bin/env bash
set -euo pipefail

dotfiles_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"

stow -Rv \
  --dir="$dotfiles_dir" \
  --target="$HOME" \
  --ignore='(^|/)\.install\.sh$' \
  .
