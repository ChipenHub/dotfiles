local pane_id = vim.env.TMUX_PANE

if not pane_id then
    return
end

local published_dir

local function tmux(args)
    vim.fn.system(vim.list_extend({ "tmux" }, args))
    return vim.v.shell_error == 0
end

local function publish_file_dir()
    local name = vim.api.nvim_buf_get_name(0)
    local dir = ""
    if vim.bo.filetype == "oil" then
        dir = require("oil").get_current_dir() or ""
    elseif vim.bo.buftype == "" and name ~= "" then
        dir = vim.fs.dirname(name)
    end
    if dir ~= "" and vim.fn.isdirectory(dir) == 0 then
        dir = ""
    end
    if dir ~= published_dir and tmux({ "set-option", "-p", "-t", pane_id, "@nvim_file_dir", dir }) then
        published_dir = dir
    end
end

vim.api.nvim_create_autocmd({ "BufEnter", "WinEnter", "BufFilePost", "DirChanged", "VimResume", "UIEnter" }, {
    callback = publish_file_dir,
})

vim.api.nvim_create_autocmd("VimLeavePre", {
    callback = function()
        tmux({ "set-option", "-pu", "-t", pane_id, "@nvim_file_dir" })
    end,
})
