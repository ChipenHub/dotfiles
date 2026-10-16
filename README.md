# Dotfiles

## Window controls: Neovim first

Neovim is the primary workspace. Alt window controls belong to Neovim; tmux offers the same gestures as convenience shortcuts in other programs. `Prefix` (`Ctrl+s`, then the next key within 500ms) always operates tmux directly.

| Keys | In Neovim | In a terminal without Neovim |
| --- | --- | --- |
| `Alt+h/j/k/l` | Focus an editor window; at its edge, continue into the neighboring tmux pane | Focus tmux pane |
| `Alt+H/J/K/L` | Resize by one cell; use tmux when the editor window spans that entire axis | Resize tmux pane by one cell |
| `Alt+v` | Choose an open buffer for a new right-hand split | Split tmux left/right |
| `Alt+s` | Choose an open buffer for a new bottom split | Split tmux top/bottom, with 20% below |
| `Alt+Space` | Equalize two windows, then cycle left/right ↔ top/bottom | Focus tmux pane on the right (80% width) |
| `Prefix Space` | Focus tmux pane on the right (80% width), bypassing editor windows | Same |
| `Prefix v/s` | Create a tmux split outside Neovim | Same |
| `Prefix h/j/k/l` | Focus tmux pane directly, bypassing editor windows | Same |

Editor navigation, resizing, and layout cycling work in Normal, Insert, and Terminal modes. Buffer selection leaves input mode and operates on ordinary file windows. Movement stops at the outer edge rather than wrapping or creating another pane.

`Alt+Space` acts only with two nonfloating windows in the current tab. Uneven windows are first equalized in their current direction; already equal windows switch between left/right and top/bottom. It preserves window order, focus, and buffers. Other window counts and input from floating windows leave the layout unchanged.

`Alt+v/s` lists ordinary listed buffers, most recently used first, with paths and `[+]` for unsaved changes. Choose a number and press Enter; `q` or an empty Enter cancels without splitting. The current file is available as another view. Existing buffers and their unsaved changes are reused; existing windows are not moved. New editor splits divide the available space in half. In Oil, `Alt+v/s` opens the selected entry directly in a right/bottom split.

`Space m` moves the current editor window: choose a target window by its displayed letter, then `h/j/k/l` to place the source left/below/above/right of it. With only one eligible target, selection is automatic. Only ordinary file windows in the current Neovim tab participate; floating windows, terminals, and separate Neovim processes are excluded.

This uses `smart-splits.nvim` v3 and its tmux backend, plus `nvim-window-picker`. The backend's `@pane-is-vim` marker controls Alt forwarding and follows suspend/resume/exit. tmux copy mode handles its own keys instead of forwarding them. Native `Ctrl+w` commands remain available; the old custom Normal-mode `Ctrl+h/j/k/l`, Shift-arrow resizing, and Oil `Ctrl+s/Ctrl+h` split mappings are removed. Insert-mode Emacs editing is unchanged.

Closing is deliberately separate: Neovim `q` closes a view/buffer as described below, while tmux `Prefix x` and `Alt+x` terminate the entire terminal pane, including Neovim if it is running there.

## tmux shortcut cheat sheet

Based on `.tmux.conf`. `Prefix` = `Ctrl+s`, followed by the next key within **500ms**. `Alt+…` shortcuts need no prefix; uppercase letters mean **Shift** is held. Alt navigation, resizing, splitting, and layout controls defer to Neovim as described above; prefix commands always stay in tmux.

### Panes, windows, and sessions

| Action | Prefix, then | Without prefix |
| --- | --- | --- |
| Focus pane left / down / up / right | `h` / `j` / `k` / `l` | `Alt+h` / `Alt+j` / `Alt+k` / `Alt+l` |
| Resize pane left / down / up / right by one cell | — | `Alt+H` / `Alt+J` / `Alt+K` / `Alt+L` |
| Swap pane left / down / up / right | `H` / `J` / `K` / `L` | — |
| Toggle pane zoom | `Ctrl+s` (i.e. press `Ctrl+s` twice) | — |
| Current pane on the right (80% width), others equally stacked on the left | `Space` | `Alt+Space` |
| Move the 1st / 2nd / 3rd left pane below the main pane (20% height) | `1` / `2` / `3` | — |
| Equalize heights in the current column / widths in the current row | `4` / `5` | — |
| Open the selected/cursor path in a pane chosen by number | — | `Shift+Enter` |
| Split top/bottom; new bottom pane gets 20% | `s` | `Alt+s` |
| Split left/right | `v` | `Alt+v` |
| Close current pane | `x` | `Alt+x` |
| Close all other panes in this window | `0` | `Alt+0` |
| Move pane to its own window | `b` | — |
| Move pane into another window (prompt) | `m` | — |
| New window | `t` | `Alt+t` |
| Respawn current pane (clear history) | `c` | `Alt+c` |
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

`Space` works with any pane count that fits the window and no longer cycles layouts. `1–3` computes the same sidebar first unless the current pane already occupies the rightmost 80% width; in that case it uses the visible left-side order from top to bottom. The preview is not displayed. The selected pane gets the bottom 20% of the right column; an existing lower-right pane returns to the sidebar. With just two panes, the resulting top/bottom pair uses the full width. A missing selection or insufficient space leaves the layout unchanged. Focus stays on the original pane.

`4` affects only adjacent panes with the same left edge and width; `5` requires the same top edge and height. Other panes are unchanged. For two top panes over one full-width bottom pane, `4` does nothing anywhere; `5` equalizes only the top pair. Prefix `6–9` is unbound; `0` still closes all other panes.

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
| `Alt+x` | Close the current tmux pane and its process, not just copy mode |

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
| `Shift+Enter` | Open the same path as `Enter`, but in a pane chosen by number |
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
| `Alt+f` / `Alt+b` | Move forward / backward one word without leaving Insert mode; these mappings do not apply in other modes |
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
| `Space m` | Choose a target editor window, then `h/j/k/l` to move beside it |
| `gv` | Restore the previous Visual selection in this buffer, including its selection type |
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
| `gd` / `gD` | Go to definition / declaration via tags, falling back to native motions |
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

## Open paths in a chosen tmux pane

`Shift+Enter` uses the same selection, cursor-path detection, source working directory, path search, and line/column handling as `Enter`. After resolving the path (and choosing among duplicate matches if needed), it displays pane numbers. Press a number to open the real file or directory in that pane; `Esc` cancels. It creates no window or pane and leaves the layout unchanged.

An existing foreground Neovim in the chosen pane is reused. Otherwise, an interactive fish shell launches Neovim with your normal configuration, plugins, and keybindings. A busy foreground job receives `Ctrl+Z` so terminal applications can prepare their suspend/resume handlers, then resumes with `fg <PID>` when Neovim exits, including a startup failure. The destination leaves copy mode and any unfinished shell input is cancelled before launching the editor. Unsupported destinations produce an English `open-path: Cannot open in this pane: ...` message in the tmux status line.

Path handling lives in `.config/tmux/open-path`; `.config/tmux/copy-mode-enter` handles opening inside the destination pane. The ordinary `Enter` behavior is unchanged.

## tmux path jump

Relevant files:

- `.tmux.conf`
- `.config/tmux/open-path`
- `.config/tmux/copy-mode-git-show`
- `.config/tmux/copy_mode_word.py`
- `.config/nvim/lua/config/tmux.lua`

### Usage

1. Enter tmux copy mode with `Esc`, `Enter`, or mouse wheel scroll.
2. Move the copy cursor onto a path, or select a path with `v` / mouse drag.
3. Press `vip` to select the path without opening it, or `Enter` to open it in a full-window Neovim, reusing one in the current session when possible.
4. Press `s` on a Git revision to run `git show` in a new window; leaving the command closes the window.
5. Press `Esc` to cancel an active search or selection; press `q` to exit copy mode.

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
- `Enter` without a selection selects the same path object and opens it.
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
- Pane resize: `Alt+H/J/K/L`; Alt navigation, resizing, and splitting defer to Neovim when it owns the pane.
- Split with cwd inherited: prefix `s` top/bottom, prefix `v` left/right.
- New window with cwd inherited: prefix `t`; prefix `c` restarts the current pane.
- Pane layouts: prefix `Space` focuses a wide right pane for any pane count; `1–3` chooses a lower-right companion; `4/5` equalizes only the current column/row.
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
- Registers `@nvim_server` in tmux so path jump can reuse live Neovim panes; this is separate from the smart-splits foreground marker.
- Clipboard uses OSC52.
- Oil is the default file explorer; open parent directory with `-`.
- Toggle floating terminal with `C-\`.

Useful keymaps:

- Insert- and command-line-mode Emacs motions: `C-p/C-n/C-f/C-b/C-a/C-e`, `Alt+f/Alt+b` for forward/backward word movement, plus `C-k`, `C-j`, `C-h`, `C-d`. `C-Space` starts visual selection in Insert mode only.
- Window controls: `Alt+h/j/k/l` focus, `Alt+H/J/K/L` resize, `Alt+v/s` choose a buffer for a split, `Alt+Space` cycle two-window layouts, `Space m` reposition a window. See the Neovim-first window controls above.
- Save all: `<leader>w`.
- Smart close: `q` saves when needed, then closes the window, buffer, or Neovim depending on context.
- Macro recording moved to `gq`.
- Buffer navigation: `[b`, `]b`, `[B`, `]B`, `gb` / `gB`, `<leader>bd`.
- Tags navigation: `gd`, `gD`, `g]`, `g[`, native `C-t`.
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
