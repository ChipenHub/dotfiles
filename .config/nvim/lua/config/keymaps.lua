-- Basic keymaps
-- Leader is set in options.lua (space)
--
-- This file contains only native Neovim keymaps, with no plugin dependencies.
-- Smart q (smart close) is at the bottom.

local map = function(mode, lhs, rhs, opts)
    opts = opts or {}
    opts.noremap = opts.noremap ~= false
    opts.silent = opts.silent ~= false
    vim.keymap.set(mode, lhs, rhs, opts)
end

-- ───────────────────────────── Emacs editing ──────────────────────────────

-- Keep these mappings out of Normal and Visual modes.
local emacs_motions = {
    { lhs = "<C-f>", rhs = "<Right>", desc = "Move forward" },
    { lhs = "<C-b>", rhs = "<Left>", desc = "Move backward" },
    { lhs = "<M-f>", rhs = "<C-Right>", desc = "Move forward one word" },
    { lhs = "<M-b>", rhs = "<C-Left>", desc = "Move backward one word" },
    { lhs = "<C-a>", rhs = "<Home>", desc = "Move to line start" },
    { lhs = "<C-e>", rhs = "<End>", desc = "Move to line end" },
}

for _, motion in ipairs(emacs_motions) do
    map("i", motion.lhs, motion.rhs, { desc = "Emacs: " .. motion.desc })
    map("c", motion.lhs, motion.rhs, { silent = false, desc = "Emacs: " .. motion.desc })
end

map("i", "<C-k>", "<C-o>D", { desc = "Emacs: Kill to line end" })
map("c", "<C-k>", function()
    local pos = vim.fn.getcmdpos()
    vim.fn.setcmdline(vim.fn.getcmdline():sub(1, pos - 1), pos)
end, { silent = false, desc = "Emacs: Kill to line end" })
map("i", "<C-j>", "<CR>", { desc = "Emacs: Insert newline" })
map("c", "<C-j>", "<CR>", { silent = false, desc = "Emacs: Accept command line" })
map("i", "<C-h>", "<BS>", { desc = "Emacs: Delete backward" })
map("c", "<C-h>", "<BS>", { silent = false, desc = "Emacs: Delete backward" })
map("i", "<C-d>", "<Del>", { desc = "Emacs: Delete forward" })
map("c", "<C-d>", "<Del>", { silent = false, desc = "Emacs: Delete forward" })
map("i", "<C-Space>", "<Esc>v", { desc = "Emacs: Start visual selection" })

-- ───────────────────────────── Indentation ───────────────────────────────────

map("v", "<leader><", "<gv", { desc = "Indent left and keep selection" })
map("v", "<leader>>", ">gv", { desc = "Indent right and keep selection" })

-- ───────────────────────────── Move selection ────────────────────────────────

-- Silence move reports so cmdheight=0 prompts cannot consume the following gv.
map("v", "J", ":silent m '>+1<CR>gv=gv", { desc = "Move selection down" })
map("v", "K", ":silent m '<-2<CR>gv=gv", { desc = "Move selection up" })

-- ───────────────────────────── Search ────────────────────────────────────────

map("n", "<Esc>", "<cmd>nohlsearch<CR>", { desc = "Clear search highlight" })
map("x", "<Esc>", "<Esc><cmd>nohlsearch<CR>", { desc = "Exit visual mode and clear search highlight" })

-- Observe the physical Esc key without replacing its mode-specific behavior.
local save_on_escape_ns = vim.api.nvim_create_namespace("save_on_escape")
vim.on_key(function(_, typed)
    if typed ~= "\27" then
        return
    end

    local bufnr = vim.api.nvim_get_current_buf()
    vim.schedule(function()
        if not vim.api.nvim_buf_is_valid(bufnr) or not vim.bo[bufnr].modified then
            return
        end

        vim.api.nvim_buf_call(bufnr, function()
            if vim.bo.buftype == "" and vim.api.nvim_buf_get_name(0) ~= "" then
                vim.cmd.write()
            end
        end)
    end)
end, save_on_escape_ns)

-- ───────────────────────────── Terminal ──────────────────────────────────────

map("t", "<Esc><Esc>", "<C-\\><C-n>", { desc = "Exit terminal mode" })

-- ───────────────────────────── Navigation (tags, no LSP) ─────────────────────
-- Relies on a tags file generated externally with universal-ctags.
-- Tag lookup uses the default 'tags=./tags;,tags', which searches upward
-- from the current file's directory for the nearest tags file.

local tags = require("config.tags")

map("n", "gd", tags.goto_def, { desc = "Go to definition (tags, fallback native gd)" })
map("n", "gD", tags.goto_decl, { desc = "Go to declaration (tags, fallback native gD)" })
map("n", "g]", tags.list_tags, { desc = "List exact tag matches for symbol" })
map("n", "g[", "<cmd>pop<CR>", { desc = "Pop to previous tag stack position" })
-- <C-t> is Neovim's native tag fallback key; no mapping needed, noted here only.

-- ───────────────────────────── Files ─────────────────────────────────────────

map({ "n", "v" }, "<leader>w", "<cmd>wa<CR>", { desc = "Save all files" })

-- ───────────────────────────── Smart q ───────────────────────────────────────
-- Press q to smart "close":
--   multiple windows / floating  -> hide (close current window only)
--   multiple buffers             -> if modified, save; switch to next and delete the old buffer
--   single buffer                -> if modified, save; quit Neovim
-- The original macro recording function is moved to gq.

local function is_floating(winnr)
    local config = vim.api.nvim_win_get_config(winnr)
    return config.relative ~= "" or config.zindex ~= nil
end

local function visible_windows()
    local wins = {}
    for _, win in ipairs(vim.api.nvim_tabpage_list_wins(0)) do
        if
            vim.api.nvim_win_get_height(win) ~= -1
            and vim.api.nvim_win_get_width(win) ~= -1
            and not is_floating(win)
        then
            wins[#wins + 1] = win
        end
    end
    return wins
end

local function listed_loaded_bufs()
    return vim.tbl_filter(function(b)
        return vim.bo[b].buflisted and vim.api.nvim_buf_is_loaded(b)
    end, vim.api.nvim_list_bufs())
end

local function save_if_needed(bufnr)
    if not vim.bo[bufnr].modified then
        return true
    end

    local buftype = vim.bo[bufnr].buftype
    if buftype ~= "" and buftype ~= "acwrite" then
        return false
    end

    local ok = pcall(vim.cmd.write)
    return ok and not vim.bo[bufnr].modified
end

map("n", "q", function()
    if #visible_windows() > 1 or is_floating(0) then
        vim.cmd("hide")
    elseif #listed_loaded_bufs() > 1 then
        local bufnr = vim.api.nvim_get_current_buf()
        if not save_if_needed(bufnr) then
            return
        end
        vim.cmd("bnext")
        vim.cmd("bdelete #")
    else
        local bufnr = vim.api.nvim_get_current_buf()
        if not save_if_needed(bufnr) then
            return
        end
        vim.cmd("quit")
    end
end, { desc = "Smart close window/buffer/quit with save" })

map("v", "q", "<Esc>", { desc = "Exit visual mode" })
map("n", "gq", "q", { noremap = true, silent = true, desc = "Record macro (original q function)" })

-- ───────────────────────────── Buffer navigation ─────────────────────────────

local function previous_buffer()
    for _ = 1, vim.v.count1 do
        vim.cmd.bprevious()
    end
end

local function next_buffer()
    for _ = 1, vim.v.count1 do
        vim.cmd.bnext()
    end
end

map("n", "[b", previous_buffer, { desc = "Previous buffer" })
map("n", "]b", next_buffer, { desc = "Next buffer" })
for _, motion in ipairs({ { "p", "previous", previous_buffer }, { "n", "next", next_buffer } }) do
    local key, direction, switch_buffer = unpack(motion)
    map({ "n", "i", "t" }, "<M-" .. key .. ">", function()
        if vim.env.TMUX and vim.env.TMUX_PANE and #vim.fn.getbufinfo({ buflisted = 1 }) == 1 then
            -- Execute the tmux action instead of sending the key back into Neovim.
            local output = vim.fn.system({
                "tmux",
                "run-shell",
                "-C",
                "-t",
                vim.env.TMUX_PANE,
                direction .. '-window -t "#{session_id}"',
            })
            if vim.v.shell_error ~= 0 then
                vim.notify(vim.trim(output), vim.log.levels.ERROR)
            end
        else
            switch_buffer()
        end
    end, { desc = "Switch to " .. direction .. " buffer or tmux window" })
end
map("n", "[B", function()
    local bufs = vim.tbl_filter(function(b)
        return vim.bo[b].buflisted
    end, vim.api.nvim_list_bufs())
    local idx = math.min(vim.v.count1, #bufs)
    vim.cmd.buffer(bufs[idx])
end, { desc = "First buffer" })
map("n", "]B", function()
    local bufs = vim.tbl_filter(function(b)
        return vim.bo[b].buflisted
    end, vim.api.nvim_list_bufs())
    local idx = math.max(#bufs - vim.v.count1 + 1, 1)
    vim.cmd.buffer(bufs[idx])
end, { desc = "Last buffer" })
map("n", "gb", "<cmd>buffer #<CR>", { desc = "Switch to alternate buffer" })
map("n", "gB", "<cmd>buffer #<CR>", { desc = "Switch to alternate buffer" })
map("n", "<leader>bd", "<cmd>bdelete<CR>", { desc = "Delete current buffer" })

-- ───────────────────────────── Other ─────────────────────────────────────────

map("n", "<f1>", "", { desc = "Disable F1" })
