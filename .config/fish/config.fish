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
abbr -a unproxy 'set -e http_proxy https_proxy'

# Use the local proxy only for Pi and its child processes.
function pi
    set -lx HTTP_PROXY http://127.0.0.1:7897
    set -lx HTTPS_PROXY http://127.0.0.1:7897
    set -lx http_proxy http://127.0.0.1:7897
    set -lx https_proxy http://127.0.0.1:7897
    command pi $argv
end

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
abbr -a up 'uv pip'
abbr -a urp 'uv run python3'

# list
abbr -a s 'eza -l'
abbr -a ss 'eza -al'
abbr -a l 'eza'

# nvim
abbr -a b 'nvim'

function __execute_with_nvim_default
    commandline -f expand-abbr
    if string match -qr '^\s*nvim\s*$' -- (commandline)
        commandline --replace 'nvim .'
    end
    commandline -f execute
end
bind \r __execute_with_nvim_default

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
begin
    set -l i
    for i in (seq 1 9)
        abbr -a gd$i "git diff HEAD~$i"
        abbr -a gl$i "git log -$i -p"
    end
end
abbr -a gr 'git reset HEAD~1'
abbr -a gc 'git commit -m'
abbr -a ga 'git commit -am'
abbr --add --position anywhere -- --force --force-with-lease

function commit --description 'Commit staged changes with a Luna-generated message'
    set -l repo_check (git rev-parse --is-inside-work-tree 2>&1)
    if test $status -ne 0
        printf '%s\n' $repo_check >&2
        return 1
    end

    git diff --cached --quiet --
    set -l diff_status $status
    if test $diff_status -eq 0
        echo 'Nothing staged; no commit created.'
        return 0
    else if test $diff_status -ne 1
        echo 'Failed to inspect staged changes.' >&2
        return $diff_status
    end

    set -l message (begin
        printf '%s\n' \
            'Generate a Git commit message for the staged diff below. Output exactly one line and nothing else. Use the format <type>: <lowercase English description>, with the narrowest conventional commit type. Do not use Markdown, quotes, a scope, or a trailing period.' \
            '<staged_diff>'
        git diff --cached --
        printf '%s\n' '</staged_diff>'
    end | pi \
        --model openai-codex/gpt-5.6-luna \
        --thinking off \
        --no-session \
        --no-tools \
        --no-extensions \
        --no-skills \
        --no-prompt-templates \
        --no-context-files \
        -p)
    set -l pi_status $status
    if test $pi_status -ne 0
        echo 'Failed to generate a commit message.' >&2
        return $pi_status
    end

    if test (count $message) -ne 1
        echo 'Luna returned an invalid multiline commit message; no commit created.' >&2
        return 1
    end

    set message (string trim -- "$message")
    if not string match -rq '^(build|chore|ci|docs|feat|fix|perf|refactor|revert|style|test): [a-z0-9]' -- "$message"
        printf 'Luna returned an invalid commit message: %s\n' "$message" >&2
        return 1
    end

    printf 'Commit message: %s\n' "$message"
    git commit -m "$message"
end

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

# Use the concrete NVM default without loading NVM during shell startup.
set -gx NVM_DIR "$HOME/.nvm"
if test -s "$NVM_DIR/alias/default"
  set -l nvm_default (string trim < "$NVM_DIR/alias/default")
  set -l nvm_bin "$NVM_DIR/versions/node/v$nvm_default/bin"
  if test -d "$nvm_bin"
    fish_add_path --prepend "$nvm_bin"
  end
end

function fish_prompt
    echo -n (prompt_pwd) "> "
end
