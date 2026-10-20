set nocompatible
scriptencoding utf-8

let mapleader = ' '
let maplocalleader = ' '

set background=dark
syntax enable
highlight CursorLine term=NONE cterm=NONE ctermbg=235 gui=NONE guibg=#262626
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
