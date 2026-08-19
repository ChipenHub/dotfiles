# Added by trae-cli installer
fish_add_path /Users/bytedance/.local/bin

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

# command replacements
abbr -a cd 'z'
abbr -a find 'fd'
abbr -a du 'dust'
abbr -a df 'duf'
abbr -a tree 'broot'
abbr -a main 'tldr'

# project
abbr -a ii 'cd /Volumes/disk1/CapCut/iOS/CapCut/'
abbr -a aa 'cd /Volumes/disk1/CapCut/Android/'

# rust
abbr -a rc 'rustc'
abbr -a cg 'cargo'

# uv
abbr -a ur 'uv run' 

# list
abbr -a s 'eza -l'
abbr -a ss 'eza -al'

# nvim
abbr -a b 'nvim'

# clear
abbr -a c 'clear'

# swift
abbr -a sw 'swift'

# remove
abbr -a rmf 'rm -rf'

# cp
abbr -a cp 'cp -r'

# git
abbr -a g 'git'
abbr -a gs 'git status'
abbr -a gp 'git pull'
abbr -a gl 'git log'
abbr -a gd 'git diff HEAD'
abbr -a gd1 'git diff HEAD~1'
abbr -a gdc 'git diff --cached'
abbr -a gg 'git status && git diff HEAD'
abbr -a gc 'git commit -m'

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

set -g CX_MODEL_DEFAULT gpt-5.3-spark

function cx --description 'Run a quick Codex task with full access'
    if test (count $argv) -eq 0
        echo 'Usage: cx "task"'
        return 1
    end

    set -l prompt (string join ' ' -- $argv)
    if string match -qr '^\[.*\]$' -- "$prompt"
        set prompt (string replace -r '^\[(.*)\]$' '$1' -- "$prompt")
    end

    set -l cx_last (mktemp -t cx-last.XXXXXX)
    set -l cx_log (mktemp -t cx-log.XXXXXX)
    set -l cx_prompt "Execute this task directly in the current directory. Use tools and make the requested changes instead of only explaining commands. Keep the final response to at most three short lines. Task: $prompt"

    codex exec \
        --model gpt-5.6-luna \
        --config 'model_reasoning_effort="low"' \
        --dangerously-bypass-approvals-and-sandbox \
        --ignore-user-config \
        --ignore-rules \
        --ephemeral \
        --skip-git-repo-check \
        --color never \
        --cd "$PWD" \
        --output-last-message $cx_last \
        -- "$cx_prompt" >$cx_log 2>&1
    set -l rc $status

    if test $rc -eq 0
        cat $cx_last
    else if test -s $cx_last
        cat $cx_last
    else
        set -l errors (string match -r -i '.*(error|fatal|failed|not supported|permission denied|operation not permitted).*' <$cx_log)
        if test (count $errors) -gt 0
            printf '%s\n' $errors
        else
            echo "cx: Codex failed with exit status $rc"
        end
    end

    command rm -f $cx_last $cx_log
    return $rc
end
