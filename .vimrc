set nocompatible
scriptencoding utf-8

let mapleader = ' '
let maplocalleader = ' '

syntax enable
filetype plugin indent on
set encoding=utf-8
set number relativenumber cursorline
set expandtab shiftwidth=4 tabstop=4 smartindent
set ignorecase smartcase hlsearch incsearch
set splitbelow splitright hidden
set tags=./tags;,tags
set wrap scrolloff=8 sidescrolloff=8
set mouse=a
set nobackup nowritebackup noswapfile
set timeout timeoutlen=300 ttimeout ttimeoutlen=100
set updatetime=300
if has('termguicolors')
    set termguicolors
endif
if has('clipboard')
    set clipboard=unnamedplus
endif

augroup dotfiles_vim
    autocmd!
    autocmd FileType * setlocal formatoptions-=o
augroup END

" Emacs editing stays in Insert and command-line modes.
inoremap <C-f> <Right>
cnoremap <C-f> <Right>
inoremap <C-b> <Left>
cnoremap <C-b> <Left>
inoremap <C-p> <Up>
cnoremap <C-p> <Up>
inoremap <C-n> <Down>
cnoremap <C-n> <Down>
inoremap <M-f> <C-Right>
cnoremap <M-f> <C-Right>
inoremap <M-b> <C-Left>
cnoremap <M-b> <C-Left>
inoremap <C-a> <Home>
cnoremap <C-a> <Home>
inoremap <C-e> <End>
cnoremap <C-e> <End>
inoremap <C-k> <C-o>D
cnoremap <C-k> <C-\>estrpart(getcmdline(), 0, getcmdpos() - 1)<CR>
inoremap <C-j> <CR>
cnoremap <C-j> <CR>
inoremap <C-h> <BS>
cnoremap <C-h> <BS>
inoremap <C-d> <Del>
cnoremap <C-d> <Del>
inoremap <C-Space> <Esc>v

xnoremap <silent> <leader>< <gv
xnoremap <silent> <leader>> >gv
xnoremap <silent> J :silent move '>+1<CR>gv=gv
xnoremap <silent> K :silent move '<-2<CR>gv=gv

" Vim has no vim.on_key; save on Escape in Normal, Insert and Visual modes.
function! s:SaveOnEscape() abort
    if &modified && &buftype ==# '' && !empty(expand('%'))
        update
    endif
endfunction
nnoremap <silent> <Esc> :<C-u>call <SID>SaveOnEscape()<CR>:nohlsearch<CR>
inoremap <silent> <Esc> <Esc>:call <SID>SaveOnEscape()<CR>:nohlsearch<CR>
xnoremap <silent> <Esc> <Esc>:call <SID>SaveOnEscape()<CR>:nohlsearch<CR>

nnoremap <silent> <leader>w :wall<CR>
xnoremap <silent> <leader>w :<C-u>wall<CR>

" Use tags when available, otherwise keep Vim's native gd/gD behavior.
function! s:GotoTag(fallback) abort
    let symbol = expand('<cword>')
    if !empty(symbol) && !empty(taglist('^' . escape(symbol, '\.*$^~[]') . '$'))
        execute 'tag ' . escape(symbol, ' \|"')
    else
        execute 'normal! ' . a:fallback
    endif
endfunction
nnoremap <silent> gd :call <SID>GotoTag('gd')<CR>
nnoremap <silent> gD :call <SID>GotoTag('gD')<CR>
nnoremap <silent> g] g<C-]>
nnoremap <silent> g[ :pop<CR>

" Keep modified buffers when closing only a split; never force-discard changes.
function! s:SmartClose() abort
    if winnr('$') > 1
        hide
        return
    endif
    if &modified
        if &buftype !=# '' && &buftype !=# 'acwrite'
            return
        endif
        write
        if &modified
            return
        endif
    endif
    if len(getbufinfo({'buflisted': 1, 'bufloaded': 1})) > 1
        let closing = bufnr('%')
        bnext
        execute 'bdelete ' . closing
    else
        quit
    endif
endfunction
nnoremap <silent> q :call <SID>SmartClose()<CR>
xnoremap q <Esc>
nnoremap gq q

nnoremap <silent> [b :<C-u>execute v:count1 . 'bprevious'<CR>
nnoremap <silent> ]b :<C-u>execute v:count1 . 'bnext'<CR>
function! s:EdgeBuffer(from_end, count) abort
    let buffers = getbufinfo({'buflisted': 1})
    let index = a:from_end ? max([len(buffers) - a:count, 0]) : min([a:count, len(buffers)]) - 1
    execute 'buffer ' . buffers[index].bufnr
endfunction
nnoremap <silent> [B :<C-u>call <SID>EdgeBuffer(0, v:count1)<CR>
nnoremap <silent> ]B :<C-u>call <SID>EdgeBuffer(1, v:count1)<CR>
nnoremap <silent> gb :buffer #<CR>
nnoremap <silent> gB :buffer #<CR>
nnoremap <silent> <leader>bd :bdelete<CR>
nnoremap <silent> <M-p> :<C-u>execute v:count1 . 'bprevious'<CR>
nnoremap <silent> <M-n> :<C-u>execute v:count1 . 'bnext'<CR>
inoremap <silent> <M-p> <C-o>:bprevious<CR>
inoremap <silent> <M-n> <C-o>:bnext<CR>

" Native window controls only: no tmux routing or plugin buffer picker.
nnoremap <silent> <M-h> <C-w>h
nnoremap <silent> <M-j> <C-w>j
nnoremap <silent> <M-k> <C-w>k
nnoremap <silent> <M-l> <C-w>l
nnoremap <silent> <M-H> :vertical resize -3<CR>
nnoremap <silent> <M-J> :resize -3<CR>
nnoremap <silent> <M-K> :resize +3<CR>
nnoremap <silent> <M-L> :vertical resize +3<CR>
nnoremap <silent> <M-v> :vsplit<CR>
nnoremap <silent> <M-s> :split<CR>

" netrw replaces Oil for browsing the current file's parent directory.
nnoremap <silent> - :Explore<CR>
nnoremap <F1> <Nop>
if has('terminal')
    tnoremap <Esc><Esc> <C-\><C-n>
    tnoremap <silent> <M-p> <C-\><C-n>:bprevious<CR>
    tnoremap <silent> <M-n> <C-\><C-n>:bnext<CR>
endif
