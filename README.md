# Dotfiles

## tmux shortcut cheat sheet

Based on `.tmux.conf`. `Prefix` = `Ctrl+s`, followed by the next key within **500ms**. `Alt+…` shortcuts need no prefix; uppercase letters mean **Shift** is held.

### Panes, windows, and sessions

| Action | Prefix, then | Without prefix |
| --- | --- | --- |
| Focus pane left / down / up / right | `h` / `j` / `k` / `l` | `Alt+h` / `Alt+j` / `Alt+k` / `Alt+l` |
| Resize pane left / down / up / right by one cell | — | `Alt+H` / `Alt+J` / `Alt+K` / `Alt+L` |
| Swap pane left / down / up / right | `H` / `J` / `K` / `L` | — |
| Toggle pane zoom | `Ctrl+s` (i.e. press `Ctrl+s` twice) | — |
| Cycle preset layout | `Space` | `Alt+Space` |
| Split top/bottom; new bottom pane gets 20% | `s` | `Alt+s` |
| Split left/right | `v` | `Alt+v` |
| Close current pane | `x` | `Alt+x` |
| Close all other panes in this window | `0` | `Alt+0` |
| Move pane to its own window | `b` | — |
| Move pane into another window (prompt) | `m` | — |
| New window | `c` or `t` | `Alt+c` or `Alt+t` |
| Previous / next window | `p` / `n` | `Alt+p` / `Alt+n` |
| Toggle last window | `a` or `;` | `Alt+;` |
| Window tree | `w` | `Alt+w` |
| Close current window | `X` | — |
| Toggle last session | `A` | — |
| Session tree | `f` | — |
| Rename session | `.` | — |
| Enter copy mode | `Esc` or `Enter` | `Alt+[` |
| Paste tmux buffer | `P` | — |

Splits and new windows inherit the current directory. Pane focus stops at window edges. Closing panes/windows above does not ask for confirmation.

### Copy mode: navigation and search

All keys below are pressed **without the prefix** while in copy mode.

| Keys | Action |
| --- | --- |
| `Alt+u` / `Alt+d` | Scroll up / down half a page; also enter copy mode from normal mode (passed through to Pi instead when Pi is running in the pane) |
| `h` / `j` / `k` / `l` | Move cursor left / down / up / right |
| `Ctrl+a` / `Ctrl+e` | Start / end of line |
| `H` / `M` / `L` | Move to roughly 15% / 50% / 85% of the visible pane |
| `b` / `e` / `w` | Previous word start / word end / next word start; counts such as `3w` work |
| `[` / `]` | Previous / next paragraph |
| `/` / `?` | Search backward (older history) / forward (newer output) |
| `n` / `N` | Repeat search / search in the opposite direction |
| `Esc` | Cancel path search and clear selection; stay in copy mode |
| `q` | Exit copy mode |

Scrolling up with the mouse enters copy mode in normal shell output; alternate-screen or mouse-aware applications may handle scrolling themselves.

### Copy mode: selection, copying, and path jumping

| Keys | Action |
| --- | --- |
| `v` / `V` | Begin character / line selection |
| `Ctrl+v` | Toggle rectangle selection |
| `A` | Append to selection |
| `d` or `Ctrl+c` | Clear selection |
| `viw` / `vaw` | Select word / word with adjacent whitespace |
| `vip` | Select path (not a paragraph) |
| `vi"` / `va"` | Select inside / around quotes; single quotes and backticks also work |
| `vi(` / `va(` | Select inside / around a balanced block; either bracket of `()`, `[]`, `{}`, `<>` works; `b` / `B` alias parentheses / braces |
| `y` | Copy active selection, staying in copy mode |
| `yy` | With no selection, copy current line |
| `yiw` / `yaw` / `yip` | With no selection, copy word / word with whitespace / path |
| `yi"` / `ya"`, `yi(` / `ya(` | With no selection, copy inside / around quotes or blocks; same variants as selection |
| `D` | Copy through end of line |
| `Ctrl+j` | Copy selection without clearing it |
| `p` | Paste tmux buffer |
| `Shift+Enter` | Select or extend path without opening it |
| `Enter` | Open selected path, or path under cursor, in full-window Neovim |
| `s` | Open `git show` for the hexadecimal commit hash under cursor in a temporary window |
| Mouse drag / double-click / triple-click | Copy selection / word / line; clear highlight and stay in copy mode |
| Single click | Clear selection and move cursor to clicked cell |

Word objects split on punctuation (including `_`) and individual Han characters; path objects retain ASCII punctuation such as `/._:`. Operator yanks (`yy`, `yi…`, `ya…`) stay in copy mode and return the cursor to the first copied character.

## Neovim shortcut cheat sheet

Based on `.config/nvim/lua/config/keymaps.lua` and `.config/nvim/lua/plugins/`. `Leader` = `Space`; press leader sequences in Normal mode unless noted. `Meta` / `Alt` = Option in this Kitty setup. Unlike tmux shortcuts, these depend on the current Neovim mode.

### Insert mode

| Keys | Action |
| --- | --- |
| `Ctrl+p` / `Ctrl+n` | Move up / down |
| `Ctrl+f` / `Ctrl+b` | Move right / left one character |
| `Alt+b` | Move backward one word without leaving Insert mode |
| `Ctrl+a` / `Ctrl+e` | Move to line start / end |
| `Ctrl+k` | Delete through end of line |
| `Ctrl+j` | Insert newline |
| `Ctrl+h` / `Ctrl+d` | Delete backward / forward |
| `Ctrl+Space` | Leave Insert mode and begin Visual selection |
| `Esc` | Return to Normal mode |

### Normal mode: files, windows, and buffers

| Keys | Action |
| --- | --- |
| `Space w` | Save all files (also works in Visual mode) |
| `q` | Close current window if multiple/floating; otherwise save modified file and close buffer or quit |
| `-` | Open parent directory in Oil |
| `Ctrl+h` / `Ctrl+j` / `Ctrl+k` / `Ctrl+l` | Focus window left / down / up / right |
| `Shift+Up` / `Shift+Down` | Increase / decrease window height |
| `Shift+Left` / `Shift+Right` | Increase / decrease window width |
| `[b` / `]b` | Previous / next buffer; accepts a count |
| `[B` / `]B` | First / last listed buffer; count selects Nth from that end |
| `gb` or `gB` | Switch to alternate buffer |
| `Space bd` | Delete current buffer |
| `Esc` | Clear search highlighting |
| `gq` | Record macro (original `q` function) |
| `Ctrl+\` | Toggle floating terminal (also works in Terminal mode) |

### Normal mode: code and Git

| Keys | Action |
| --- | --- |
| `gd` / `gD` | Go to definition / declaration via scope-aware tags, falling back to native motions |
| `gr` | Find references with ripgrep and show quickfix results |
| `g]` | List exact tag matches for symbol |
| `g[` or `Ctrl+t` | Return to previous tag-stack position |
| `[c` / `]c` | Previous / next Git hunk (native motions in diff mode) |
| `Space gs` | Open Fugitive Git status |
| `Space gp` | Preview current Git hunk |
| `Space gb` | Show full blame for current line |
| `Space gd` | Diff current file against HEAD |
| `Ctrl+n` | Select next occurrence with multicursor (also works in Visual mode) |

### Visual and Terminal modes

| Mode | Keys | Action |
| --- | --- | --- |
| Visual | `Space <` / `Space >` | Indent left / right and keep selection |
| Visual | `J` / `K` | Move selected lines down / up and reindent |
| Visual | `q` | Return to Normal mode |
| Terminal | `Esc Esc` | Leave terminal input mode for Normal mode |

Personal terminal/editor setup centered on tmux path jumping and a lean Neovim workflow.

## Install / refresh

Run from the repo root:

```bash
./.install.sh              # List available targets without installing
./.install.sh hammerspoon  # Install only Hammerspoon
./.install.sh omp          # Link OMP keybindings and shared skills/extensions only
./.install.sh tmux fish    # Install selected targets
./.install.sh all          # Install / refresh the full whitelist
```

The installer uses GNU Stow and only installs the selected targets from the explicit whitelist in `.install.sh`. Existing regular files must be backed up before installation; they are not overwritten.

Home links:

- `.codex`
- `.claude`
- `.pi`
- `.omp` (only the three managed entries below, for both `omp` and `all`)
- `.hammerspoon`
- `.tmux.conf`
- `.emacs`
- `.emacs.custom.el`

`.config` links:

- `fish`
- `karabiner`
- `kitty`
- `nnn`
- `nvim`
- `tmux`

## OMP

OMP follows `.pi`'s layout: `.omp/agent/keybindings.yml` contains the compatible
editor/selection bindings, while `skills` and `extensions` link to
`.agents/skills` and `.agents/hooks`. `./.install.sh omp` links these three entries
into an existing `~/.omp/agent` without replacing the directory or local settings.
Existing conflicting files or links are refused.
`./.install.sh all` excludes `.omp` from Stow and runs the same `omp` installer,
so switching between individual and full installs preserves link ownership.

`Ctrl+P/N` navigate the editor and selections instead of cycling models;
`Ctrl+J` inserts a newline. Pi's `tui.altScreen.*`, `app.models.toggleProvider`,
and `app.session.toggleNamedFilter` have no matching actions in OMP 18.4.2 and
are not copied. OMP's temporary model picker (`Alt+P`) remains available.

`config.yml`, credentials, databases, sessions, caches, and logs remain local
and are excluded from Git. Restart OMP after installation to load the bindings
and shared extensions.

## tmux path jump

This is the good part.

Relevant files:

- `.tmux.conf`
- `.config/tmux/open-path`
- `.config/tmux/copy-mode-enter`
- `.config/tmux/copy-mode-git-show`
- `.config/tmux/copy_mode_word.py`
- `.config/nvim/lua/config/tmux.lua`

### Usage

1. Enter tmux copy mode with `Esc`, `Enter`, or mouse wheel scroll.
2. Move the copy cursor onto a path, or select a path with `v` / mouse drag.
3. Press `S-Enter` to select or extend the path without opening it.
4. Press `Enter` to open it in a full-window Neovim, reusing one in the current session when possible.
5. Press `s` on a Git revision to run `git show` in a new window; leaving the command closes the window.
6. Press `Esc` to cancel an active search or selection; press `q` to exit copy mode.

### Behavior

- Accepts `file`, `dir/file`, `file:12`, `file:12:3`, `file(12,3)`, and `file#L12`.
- Resolves existing paths relative to the source pane's current directory.
- If the direct path does not exist, searches from the Git root.
- Ignores `.git`, `.cache`, and `node_modules` during fallback search.
- If multiple matches exist, opens an `fzf` chooser in a tmux popup.
- `Enter` reuses and switches to the only live Neovim pane that occupies an entire window in the current session.
- Otherwise it creates a new tmux window.
- Directories open through Oil when reusing an existing Neovim server.
- Search status appears in tmux status-right.

### Copy-mode helpers

- `Alt+u` / `Alt+d` enter copy mode and scroll up / down half a page. In a pane running Pi, tmux passes these keys through to Pi instead.
- `H` / `M` / `L` move to 15% / 50% / 85% of the visible pane.
- `[` / `]` move by paragraph, matching `{` / `}`.
- `b` / `e` / `w` use Vim-style word boundaries, with `_` as punctuation and each Han character or Chinese punctuation mark as a separate unit. Numeric prefixes such as `3w` work too.
- `viw` selects the current word, punctuation unit, or whitespace run.
- `vaw` includes trailing whitespace, or preceding whitespace when there is no trailing whitespace (excluding indentation).
- `vi"` / `va"` select inside / around quotes, respecting backslash escapes. Single quotes and backticks work too.
- `vi(` / `va)` select inside / around nested, multiline blocks. Either bracket in `()`, `[]`, `{}` or `<>` works; `b` / `B` alias parentheses / braces.
- Text objects select forward and retain rectangle mode. `C-v` toggles rectangle selection with the cursor on the right edge; `j` / `k` keep its columns across short lines and wide Chinese characters.
- `vip` selects a path: ASCII punctuation such as `/._:` stays inside it; whitespace, Han characters and Chinese punctuation split it. This is a custom path object, not Vim's paragraph object.
- `Enter` without a selection selects the same path object and opens it; `S-Enter` selects or extends it without opening.
- `s` selects the current word, stopping at punctuation (including `_`, `-` and `/`), and accepts only 4–64 hexadecimal characters (a commit hash or abbreviation). It opens `git show <revision>` in a new tmux window, which closes when the command exits.
- `y` copies an active visual selection. Without one, Vim-style yanks such as `yy`, `yiw`, `yip`, `yi(`, `ya(`, and their quote/bracket variants copy without leaving copy mode, then return the cursor to the first copied character. `p` pastes and `q` cancels copy mode.
- `:` opens a one-line command prompt and runs the command in a temporary pane occupying the bottom 30%. Commands lasting at least three seconds close with the pane when they exit; quicker results wait for any key so they remain readable.
- Layout changes (prefix `Space`, pane resizing, or terminal resizing) refresh every resized copy-mode pane, focused or not, after **300ms** without another layout change. Tracking uses hidden environment variables to avoid global redraws; stale timers do not start workers.
- `.config/tmux/refresh_copy_mode.py` records the cursor's x/y and the frozen page's absolute history row **at refresh time**, exits and re-enters copy mode, then restores that row without switching focus. With history retained, appended output does not move the page. Positions are clamped when necessary. It does not match text, preserve selections, or restore a pre-resize content anchor. Output arriving after this one-shot refresh remains frozen.

These helpers require Python 3 and tmux with `capture-pane -M` support (tested on 3.6a and 3.6b).
Run their tests with `python3 -m unittest discover -s .config/tmux/tests -v`.

## tmux basics

- Prefix is `C-s` instead of `C-b`; it expires after 500ms. Press `C-s` twice within that window to toggle pane zoom.
- Pane movement: prefix `h/j/k/l`.
- Pane resize: `M-h/M-j/M-k/M-l`.
- Split with cwd inherited: prefix `s` vertical, prefix `v` horizontal.
- New window with cwd inherited: prefix `c` or `t`.
- Preset layout: prefix `Space`; normalizes two/three/four-pane layouts around a wide right pane.
- Window/session navigation: prefix `;` or prefix `a` toggles the last window, prefix `A` last session, prefix `w` window tree, prefix `f` session tree.

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
- Git: `[c` / `]c` previous/next changed hunk; `<leader>gs` Fugitive status; `<leader>gp` preview hunk; `<leader>gb` blame; `<leader>gd` diff current file.
- Multicursor: `C-n` selects next occurrence.

## Hammerspoon

`.hammerspoon/init.lua` clamps movement and drag events to one macOS coordinate point inside each screen's left edge, preserving vertical movement and leaving click events untouched. It uses no polling timer or cursor warping. On Retina displays, a coordinate point can span multiple physical pixels. Direct cursor repositioning by other apps is not intercepted; this is not a system-level confinement guarantee.

Enable Hammerspoon in **System Settings → Privacy & Security → Accessibility**, then restart Hammerspoon or choose **Reload Config**. Hammerspoon must remain running. Downloaded Spoons and runtime files are not tracked.

## Other useful config

- fish sets `EDITOR` and `VISUAL` to `nvim`.
- fish abbreviations include `b -> nvim`; bare `b` or `nvim` opens the current directory. Other abbreviations include `cd -> z`, `find -> fd`, `s/ss/l -> eza`, and common git shortcuts.
- `nnn` uses `.config/nnn/opener` so editable files stay in terminal Neovim, images preview with `chafa`, and videos do not accidentally open externally.
- Karabiner, Emacs, Pi/OMP/Codex/Claude agent configs are tracked too, but they are secondary to the tmux + Neovim workflow.
