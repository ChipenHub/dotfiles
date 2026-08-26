# Dotfiles

Personal terminal/editor setup centered on tmux path jumping and a lean Neovim workflow.

## Install / refresh

Run from the repo root:

```bash
./.install.sh
```

The installer uses GNU Stow and only installs the explicit whitelist in `.install.sh`.

Home links:

- `.codex`
- `.claude`
- `.pi`
- `.tmux.conf`
- `.emacs`
- `.emacs.custom.el`

`.config` links:

- `fish`
- `karabiner`
- `nnn`
- `nvim`
- `tmux`

## tmux path jump

This is the good part.

Relevant files:

- `.tmux.conf`
- `.config/tmux/open-path`
- `.config/tmux/copy-mode-enter`
- `.config/nvim/lua/config/tmux.lua`

### Usage

1. Enter tmux copy mode with `Esc`, `Enter`, or mouse wheel scroll.
2. Move the copy cursor onto a path, or select a path with `v` / mouse drag.
3. Press `Enter` to open it in Neovim.
4. Press `O` to open it in a new tmux window instead of a split.
5. Press `Esc` to cancel copy mode and cancel any active path search.

### Behavior

- Accepts `file`, `dir/file`, `file:12`, `file:12:3`, and `file(12,3)`.
- Resolves existing paths relative to the source pane's current directory.
- If the direct path does not exist, searches from the Git root.
- Ignores `.git`, `.cache`, and `node_modules` during fallback search.
- If multiple matches exist, opens an `fzf` chooser in a tmux popup.
- If exactly one reusable Neovim server exists in the current tmux window, opens the file there.
- When `Enter` reuses Neovim in the same pane, it exits copy mode so the jump is visible immediately.
- Otherwise creates a 60% right split running `nvim`.
- Directories open through Oil when reusing an existing Neovim server.
- Search status appears in tmux status-right.

### Copy-mode helpers

- `Enter` without a selection selects a space-delimited word and opens it.
- `S-Enter` selects or extends a space-delimited word without opening it.
- `viw` uses symbol-aware word boundaries.
- `vip` uses space-delimited selection, better for paths.
- `y` copies, `p` pastes, `q` cancels copy mode.

## tmux basics

- Prefix is `C-s` instead of `C-b`.
- Pane movement: prefix `h/j/k/l`.
- Pane resize: `M-h/M-j/M-k/M-l`.
- Split with cwd inherited: prefix `s` vertical, prefix `v` horizontal.
- New window with cwd inherited: prefix `c` or `t`.
- Preset layout: prefix `Space`; normalizes two/three-pane layouts around a wide right pane.
- Window/session navigation: prefix `a` last window, prefix `A` last session, prefix `w` window tree, prefix `f` session tree.

## Neovim basics

Relevant files:

- `.config/nvim/init.lua`
- `.config/nvim/lua/config/options.lua`
- `.config/nvim/lua/config/keymaps.lua`
- `.config/nvim/lua/config/tmux.lua`
- `.config/nvim/lua/plugins/*.lua`

Core behavior:

- Leader is Space.
- Uses `lazy.nvim`.
- Uses tags and ripgrep for navigation rather than an LSP-heavy workflow.
- Registers `@nvim_server` in tmux so path jump can reuse live Neovim panes.
- Clipboard uses OSC52.
- Oil is the default file explorer; open parent directory with `-`.
- Toggle floating terminal with `C-\`.

Useful keymaps:

- Insert-mode Emacs motions: `C-p/C-n/C-f/C-b/C-a/C-e`, plus `C-k`, `C-j`, `C-h`, `C-d`.
- Window movement: `C-h/C-j/C-k/C-l`.
- Save all: `<leader>w`.
- Smart close: `q` saves when needed, then closes the window, buffer, or Neovim depending on context.
- Macro recording moved to `gq`.
- Buffer navigation: `[b`, `]b`, `[B`, `]B`, `gb` / `gB`, `<leader>bd`.
- Tags navigation: `gd`, `gD`, `gr`, `g]`, `g[`, native `C-t`.
- Git: `<leader>gs` Fugitive status; `<leader>gp` preview hunk; `<leader>gb` blame; `<leader>gd` diff current file.
- Multicursor: `C-n` selects next occurrence.

## Other useful config

- fish sets `EDITOR` and `VISUAL` to `nvim`.
- fish abbreviations include `b -> nvim`, `cd -> z`, `find -> fd`, `s/ss/l -> eza`, and common git shortcuts.
- `nnn` uses `.config/nnn/opener` so editable files stay in terminal Neovim, images preview with `chafa`, and videos do not accidentally open externally.
- Karabiner, Emacs, Pi/Codex/Claude agent configs are tracked too, but they are secondary to the tmux + Neovim workflow.
