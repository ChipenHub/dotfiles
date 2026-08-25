#!/usr/bin/env bash
set -euo pipefail

dotfiles_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
state_file="${XDG_STATE_HOME:-$HOME/.local/state}/dotfiles/installed-paths"
available_targets=(
  fish
  karabiner
  nvim
  tmux
  emacs
)

target_paths() {
  case "$1" in
    fish) printf '%s\n' ".config/fish/config.fish" ;;
    karabiner) printf '%s\n' ".config/karabiner/karabiner.json" ;;
    nvim) printf '%s\n' ".config/nvim" ;;
    tmux) printf '%s\n' ".tmux.conf" ".config/tmux" ;;
    emacs) printf '%s\n' ".emacs" ".emacs.custom.el" ;;
    *) return 1 ;;
  esac
}

is_target() {
  local known
  for known in "${available_targets[@]}"; do
    if [ "$known" = "$1" ]; then
      return 0
    fi
  done
  return 1
}

show_targets() {
  echo "Usage: ./.install.sh <target...>"
  echo "       ./.install.sh all"
  echo
  echo "Available targets:"

  local target path
  for target in "${available_targets[@]}"; do
    printf '  %-10s' "$target"
    while IFS= read -r path; do
      printf ' %s' "$path"
    done < <(target_paths "$target")
    echo
  done
}

contains_path() {
  local wanted="$1" path
  shift
  for path in "$@"; do
    if [ "$path" = "$wanted" ]; then
      return 0
    fi
  done
  return 1
}

link_path() {
  local path="$1"
  local source="$dotfiles_dir/$path"
  local destination="$HOME/$path"

  if [ ! -e "$source" ]; then
    echo "Missing source: $source" >&2
    return 1
  fi

  mkdir -p "$(dirname "$destination")"

  if [ -L "$destination" ]; then
    rm "$destination"
  elif [ -e "$destination" ]; then
    echo "Refusing to replace existing path: $destination" >&2
    return 1
  fi

  ln -s "$source" "$destination"
  echo "LINK: $path"
}

unlink_path() {
  local path="$1"
  local destination="$HOME/$path"

  if [ -L "$destination" ] && [ "$(readlink "$destination")" = "$dotfiles_dir/$path" ]; then
    rm "$destination"
    echo "UNLINK: $path"
  fi
}

write_state() {
  mkdir -p "$(dirname "$state_file")"
  printf '%s\n' "$@" >"$state_file"
}

if [ "$#" -eq 0 ]; then
  show_targets
  exit 0
fi

if [ "$1" = "all" ]; then
  if [ "$#" -ne 1 ]; then
    echo "'all' cannot be combined with other targets" >&2
    exit 1
  fi
  selected_targets=("${available_targets[@]}")
else
  selected_targets=("$@")
fi

for target in "${selected_targets[@]}"; do
  if ! is_target "$target"; then
    echo "Unknown target: $target" >&2
    show_targets >&2
    exit 1
  fi
done

installed_paths=()
if [ -f "$state_file" ]; then
  while IFS= read -r path; do
    [ -n "$path" ] && installed_paths+=("$path")
  done <"$state_file"
fi

desired_paths=()
for target in "${selected_targets[@]}"; do
  while IFS= read -r path; do
    desired_paths+=("$path")
  done < <(target_paths "$target")
done

if [ "$1" = "all" ]; then
  for path in "${installed_paths[@]}"; do
    if ! contains_path "$path" "${desired_paths[@]}"; then
      unlink_path "$path"
    fi
  done
  next_state=("${desired_paths[@]}")
else
  next_state=("${installed_paths[@]}")
  for path in "${desired_paths[@]}"; do
    if ! contains_path "$path" "${next_state[@]}"; then
      next_state+=("$path")
    fi
  done
fi

for path in "${desired_paths[@]}"; do
  link_path "$path"
done
write_state "${next_state[@]}"
