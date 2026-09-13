# Disable the startup greeting and direnv status messages.
set -g fish_greeting
set -gx DIRENV_LOG_FORMAT ""

# Added by trae-cli installer
fish_add_path /Users/bytedance/.local/bin

# Default terminal editor
set -gx EDITOR nvim
set -gx VISUAL nvim

# especiallly for emacs's compile-mode
function rt
    readtags $argv | awk -F '\t' '{
        line = $3
        sub(/;".*/, "", line)
        print $2 ":" line ":" $1
    }'
end

# codex default yolo
abbr -a codex 'codex --yolo'

# export proxy
abbr -a proxy 'export http{,s}_proxy=http://127.0.0.1:7897'
export http{,s}_proxy=http://127.0.0.1:7897

# command replacements
abbr -a cd 'z'
abbr -a find 'fd'
abbr -a du 'dust'
abbr -a df 'duf'

# project
abbr -a ii 'cd /Volumes/disk1/CapCut/iOS/CapCut/'
abbr -a i2 'cd /Volumes/disk1/CapCut/iOS2/CapCut/'
abbr -a aa 'cd /Volumes/disk1/CapCut/Android/'

# uv
abbr -a ur 'uv run' 

# list
abbr -a s 'eza -l'
abbr -a ss 'eza -al'
abbr -a l 'eza'

# nvim
abbr -a b 'nvim'

# clear
abbr -a c 'clear'

# remove
abbr -a rmf 'rm -rf'

# cp
abbr -a cp 'cp -r'

# cp
abbr -a r 'rg'

# git
abbr -a g 'git'
abbr -a gs 'git status'
abbr -a gl 'git log'
abbr -a gd 'git diff'
abbr -a gc 'git commit -m'
abbr -a ga 'git commit -am'
abbr --add --position anywhere -- --force --force-with-lease

# find
abbr -a f 'find'

fish_add_path /opt/homebrew/bin

# pnpm
set -gx PNPM_HOME "/Users/bytedance/Library/pnpm"
if not string match -q -- $PNPM_HOME $PATH
  set -gx PATH "$PNPM_HOME" $PATH
end
# pnpm end

# add home path
fish_add_path $HOME/.local/bin

# ctags
abbr -a ct 'bash ~/scripts/gen_tags.sh'

# z
zoxide init fish | source

# nnn
export NNN_TRASH="trash"
set -gx NNN_OPENER "$HOME/.config/nnn/opener"
abbr -a n "nnn -ecA"

# nvm: align Node/npm with zsh (use nvm default)
set -gx NVM_DIR "$HOME/.nvm"
if test -s "$NVM_DIR/nvm.sh"
  set -l nvm_default (bash -lc 'source "$HOME/.nvm/nvm.sh" >/dev/null 2>&1; nvm version default 2>/dev/null' 2>/dev/null)
  if test -n "$nvm_default"; and test "$nvm_default" != "N/A"
    set -l nvm_bin "$NVM_DIR/versions/node/$nvm_default/bin"
    if test -d "$nvm_bin"
      fish_add_path --prepend "$nvm_bin"
    end
  end
end

function fish_prompt
    echo -n (prompt_pwd) "> "
end
