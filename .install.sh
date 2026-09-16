#!/usr/bin/env bash
set -euo pipefail

dotfiles_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"

# 直接安装到 $HOME 下的目标。
home_links=(
  .gitconfig.shared
  .codex
  .claude
  .pi
  .hammerspoon
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
  ov
  tmux
)

install_git_include() {
  # Keep automatic global writes local, never through a dotfiles symlink.
  if [ -L "$HOME/.gitconfig" ]; then
    printf 'Refusing to write through symlink: %s\n' "$HOME/.gitconfig" >&2
    return 1
  fi
  if ! git config --file "$HOME/.gitconfig" --get-all include.path | grep -Fxq '~/.gitconfig.shared'; then
    local config_tmp
    config_tmp="$(mktemp "$HOME/.gitconfig.XXXXXX")"
    printf '[include]\n\tpath = ~/.gitconfig.shared\n' > "$config_tmp"
    if [ -f "$HOME/.gitconfig" ]; then
      cat "$HOME/.gitconfig" >> "$config_tmp"
    fi
    mv "$config_tmp" "$HOME/.gitconfig"
  fi
}

# Named targets install only their own links; no arguments only lists targets.
if [ "$#" -eq 0 ]; then
  printf 'Usage: %s <target ... | all>\n' "$0"
  for name in "${home_links[@]}"; do
    target="${name#.}"
    [ "$name" != .gitconfig.shared ] || target=git
    printf '  %s -> ~/%s\n' "$target" "$name"
  done
  for name in "${config_links[@]}"; do
    printf '  %s -> ~/.config/%s\n' "$name" "$name"
  done
  exit 0
fi

if [ "$#" -ne 1 ] || [ "$1" != all ]; then
  selected_paths=()
  for target in "$@"; do
    matched=false
    for name in "${home_links[@]}" "${config_links[@]/#/.config/}"; do
      key="${name#.}"
      key="${key#config/}"
      [ "$name" != .gitconfig.shared ] || key=git
      if [ "$target" = "$key" ]; then
        if [ -e "$HOME/$name" ] || [ -L "$HOME/$name" ]; then
          if [ ! -L "$HOME/$name" ] || [ "$(readlink "$HOME/$name")" != "$dotfiles_dir/$name" ]; then
            printf 'Refusing to overwrite: %s\n' "$HOME/$name" >&2
            exit 1
          fi
        fi
        selected_paths+=("$name")
        matched=true
        break
      fi
    done
    if [ "$matched" = false ]; then
      printf 'Unknown target: %s\n' "$target" >&2
      exit 1
    fi
  done
  for name in "${selected_paths[@]}"; do
    mkdir -p "$(dirname "$HOME/$name")"
    if [ ! -L "$HOME/$name" ]; then
      ln -s "$dotfiles_dir/$name" "$HOME/$name"
    fi
    printf 'Linked: %s -> %s\n' "$HOME/$name" "$dotfiles_dir/$name"
    if [ "$name" = .gitconfig.shared ]; then
      install_git_include
    fi
  done
  exit 0
fi

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

# 不带参数时只列出目标；all 保留原来的全量安装行为。
if [ "$#" -eq 0 ]; then
  echo "Usage: $0 <target> [target ...] | all"
  for name in "${home_links[@]}"; do
    printf '  %-18s %s\n' "${name#.}" "\$HOME/$name"
  done
  for name in "${config_links[@]}"; do
    printf '  %-18s %s\n' "$name" "\$HOME/.config/$name"
  done
  exit 0
fi

if [ "$#" -ne 1 ] || [ "$1" != all ]; then
  selected_home=()
  selected_config=()
  for target in "$@"; do
    if contains ".$target" "${home_links[@]}"; then
      selected_home+=(".$target")
    elif contains "$target" "${config_links[@]}"; then
      selected_config+=("$target")
    else
      echo "unknown target: $target (run $0 to list targets)" >&2
      exit 1
    fi
  done
  # Bash 3.2 treats empty arrays as unset under nounset.
  home_links=(${selected_home[@]+"${selected_home[@]}"})
  config_links=(${selected_config[@]+"${selected_config[@]}"})
fi

regex_escape() {
  printf '%s' "$1" | perl -pe 's/([\\.\[\]{}()+*?^$|])/\\$1/g'
}


ignore_args=()
if [ "${#config_links[@]}" -eq 0 ]; then
  ignore_args+=(--ignore='^\.config($|/)')
fi

# 顶层只允许 home_links 和 .config；其他仓库文件都不 stow。
shopt -s nullglob dotglob
for path in "$dotfiles_dir"/*; do
  name="$(basename "$path")"
  if [ "$name" = ".config" ] || contains "$name" ${home_links[@]+"${home_links[@]}"}; then
    continue
  fi
  ignore_args+=(--ignore="^$(regex_escape "$name")($|/)")
done

# .config 下面只允许 config_links。
for path in "$dotfiles_dir/.config"/*; do
  name="$(basename "$path")"
  if contains "$name" ${config_links[@]+"${config_links[@]}"}; then
    continue
  fi
  ignore_args+=(--ignore="^\.config/$(regex_escape "$name")($|/)")
done
shopt -u nullglob dotglob

# Stow refuses absolute symlinks in a package. These are runtime-managed links,
# so leave their installation to their owner.
managed_roots=()
for name in ${home_links[@]+"${home_links[@]}"}; do
  managed_roots+=("$dotfiles_dir/$name")
done
for name in ${config_links[@]+"${config_links[@]}"}; do
  managed_roots+=("$dotfiles_dir/.config/$name")
done

while IFS= read -r -d '' path; do
  case "$(readlink "$path")" in
    /*)
      relative_path="${path#"$dotfiles_dir"/}"
      ignore_args+=(--ignore="^$(regex_escape "$relative_path")$")
      ;;
  esac
done < <(find -H "${managed_roots[@]}" -type l -print0)

mkdir -p "$HOME/.config"

# 禁止目录折叠，避免把包含未选中配置的整个目录链接回去。
stow \
  --dir="$dotfiles_dir" \
  --target="$HOME" \
  --restow \
  --no-folding \
  --verbose=1 \
  "${ignore_args[@]}" \
  .

install_git_include
