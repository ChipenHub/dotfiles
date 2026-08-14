-- Basic editor options
vim.opt.backup = false
vim.opt.clipboard = "unnamedplus"
vim.opt.cmdheight = 1
vim.opt.completeopt = { "menuone", "noselect" }
vim.opt.conceallevel = 0
vim.opt.fileencoding = "utf-8"
vim.opt.hlsearch = true
vim.opt.ignorecase = true
vim.opt.mouse = "a"
vim.opt.pumheight = 10
vim.opt.showmode = false
vim.opt.showtabline = 2
vim.opt.smartcase = true
vim.opt.smartindent = true
vim.opt.splitbelow = true
vim.opt.splitright = true
vim.opt.swapfile = false
vim.opt.termguicolors = true
vim.opt.timeout = false
vim.opt.timeoutlen = 300
vim.opt.ttimeout = true
vim.opt.timeoutlen = 100
vim.opt.undofile = true
vim.opt.updatetime = 300
vim.opt.writebackup = false
vim.opt.expandtab = true
vim.opt.shiftwidth = 4
vim.opt.tabstop = 4
vim.opt.cursorline = true
vim.opt.number = true
vim.opt.relativenumber = true
vim.opt.numberwidth = 4
vim.opt.signcolumn = "yes"
vim.opt.wrap = true
vim.opt.scrolloff = 8
vim.opt.sidescrolloff = 8
vim.opt.guifont = "monospace:h17"

-- Disable some built-in plugins
local disabled_built_ins = {
    "netrw",
    "netrwPlugin",
    "netrwSettings",
    "netrwFileHandlers",
    "gzip",
    "zip",
    "zipPlugin",
    "tar",
    "tarPlugin",
    "getscript",
    "getscriptPlugin",
    "vimball",
    "vimballPlugin",
    "2html_plugin",
    "logipat",
    "rrhelper",
    "spellfile_plugin",
    "matchit",
}

for _, plugin in pairs(disabled_built_ins) do
    vim.g["loaded_" .. plugin] = 1
end

-- Set mapleader
vim.g.mapleader = " "
vim.g.maplocalleader = " "

-- Set global LSP log level to off
vim.lsp.log.set_level("off")

vim.api.nvim_create_augroup("mygroup", { clear = true })
vim.api.nvim_create_autocmd("FileType", {
    pattern = { "*" },
    callback = function()
        vim.opt.formatoptions = vim.opt.formatoptions + {
            o = false, -- Don't continue comments with o and O
        }
    end,
    group = "mygroup",
    desc = "Don't continue comments with o and O",
})

-- vim.api.nvim_create_autocmd("BufLeave", {
--     callback = function()
--         if vim.bo.buftype == 'acwrite' and vim.bo.filetype == 'oil' then
--             local oil_buf = vim.api.nvim_win_get_buf(0)
--             local bufs = vim.fn.filter(vim.fn.range(1, vim.fn.bufnr('$')), function(buf)
--                 return buf ~= oil_buf and vim.fn.bufloaded(buf) and vim.fn.bufname(buf) ~= "" and vim.fn.buflisted(buf) == 1
--             end)
--             if #bufs == 0 then
--                 vim.cmd("quit")
--             end
--         end
--     end,
--     group = "mygroup",
--     desc = "Quit Neovim when the the only Oil buffer is closed",
-- })

vim.g.clipboard = {
    name = "OSC 52",
    copy = {
        ["+"] = require("vim.ui.clipboard.osc52").copy("+"),
        ["*"] = require("vim.ui.clipboard.osc52").copy("*"),
    },
    paste = {
        ["+"] = require("vim.ui.clipboard.osc52").paste("+"),
        ["*"] = require("vim.ui.clipboard.osc52").paste("*"),
    },
}
