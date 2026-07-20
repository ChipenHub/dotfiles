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

# ios
abbr -a i1 'cd /Volumes/disk1/Worktrees/ios/1/CapCut'
abbr -a i2 'cd /Volumes/disk1/Worktrees/ios/2/CapCut'
abbr -a i3 'cd /Volumes/disk1/Worktrees/ios/3/CapCut'
abbr -a i4 'cd /Volumes/disk1/Worktrees/ios/4/CapCut'

# android
abbr -a a1 'cd /Volumes/disk1/Worktrees/and/1'
abbr -a a2 'cd /Volumes/disk1/Worktrees/and/2'
abbr -a a3 'cd /Volumes/disk1/Worktrees/and/3'
abbr -a a4 'cd /Volumes/disk1/Worktrees/and/4'

# rust
abbr -a rc 'rustc'
abbr -a cg 'cargo'

# uv
abbr -a ur 'uv run' 

# list
abbr -a ll 'ls -al'
abbr -a s 'eza'
abbr -a ss 'eza -al'

# nvim
abbr -a b 'nvim'

# clear
abbr -a c 'clear'

# swift
abbr -a sw 'swift'

# coco
abbr -a co 'coco'

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

function gc
    git add . && git commit -am $argv
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

# Added by coco installer
fish_add_path /Users/bytedance/.local/bin

# ctags
abbr -a ct 'bash ~/Scripts/gen_tags.sh'

# capcut ios build/debug
abbr -a ccbuild 'env -u PYTHONHOME DISABLE_RESET_PYHOME=true cdf build'
abbr -a ccbuildonly 'env -u PYTHONHOME DISABLE_RESET_PYHOME=true JOJO_TAGS_LVCC_LOCAL_BUILD_MODE=debug_package bash .pipeline/build_debug_focus_link.sh'
abbr -a ccinstall 'cdf build reinstall'
abbr -a cclaunch 'cdf launch --relaunch --skip-assert true'
abbr -a ccattach 'cdf debug'

function ccdebug
    cdf launch --relaunch --skip-assert true
    and cdf debug
end

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