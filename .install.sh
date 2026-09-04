#!/usr/bin/env bash
set -euo pipefail

dotfiles_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"

# 直接安装到 $HOME 下的目标。
home_links=(
  .codex
  .claude
  .pi
  .tmux.conf
  .emacs
  .emacs.custom.el
)

# 安装到 $HOME/.config 下的目标，对应仓库里的 .config/<name>。
config_links=(
  fish
  karabiner
  kitty
  nnn
  nvim
  tmux
)

if ! command -v stow >/dev/null 2>&1; then
  echo "missing: stow" >&2
  echo "install it with: brew install stow" >&2
  exit 1
fi

contains() {
  local wanted="$1" item
  shift
  for item in "$@"; do
    [ "$item" = "$wanted" ] && return 0
  done
  return 1
}

regex_escape() {
  printf '%s' "$1" | perl -pe 's/([\\.\[\]{}()+*?^$|])/\\$1/g'
}


ignore_args=()

# 顶层只允许 home_links 和 .config；其他仓库文件都不 stow。
shopt -s nullglob dotglob
for path in "$dotfiles_dir"/*; do
  name="$(basename "$path")"
  if [ "$name" = ".config" ] || contains "$name" "${home_links[@]}"; then
    continue
  fi
  ignore_args+=(--ignore="^$(regex_escape "$name")($|/)")
done

# .config 下面只允许 config_links。
for path in "$dotfiles_dir/.config"/*; do
  name="$(basename "$path")"
  if contains "$name" "${config_links[@]}"; then
    continue
  fi
  ignore_args+=(--ignore="^\.config/$(regex_escape "$name")($|/)")
done
shopt -u nullglob dotglob

mkdir -p "$HOME/.config"

stow \
  --dir="$dotfiles_dir" \
  --target="$HOME" \
  --restow \
  --verbose=1 \
  "${ignore_args[@]}" \
  .
