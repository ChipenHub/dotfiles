local pane_id = vim.env.TMUX_PANE

if not pane_id then
    return
end

local registered_server
local published_dir

local function tmux(args)
    vim.fn.system(vim.list_extend({ "tmux" }, args))
    return vim.v.shell_error == 0
end

local function publish_file_dir()
    if not registered_server then
        return
    end

    local name = vim.api.nvim_buf_get_name(0)
    local dir = vim.bo.buftype == "" and name ~= "" and vim.fs.dirname(name) or ""
    if dir ~= "" and vim.fn.isdirectory(dir) == 0 then
        dir = ""
    end
    if dir ~= published_dir and tmux({ "set-option", "-p", "-t", pane_id, "@nvim_file_dir", dir }) then
        published_dir = dir
    end
end

vim.api.nvim_create_autocmd({ "BufEnter", "WinEnter", "BufFilePost", "DirChanged", "VimResume" }, {
    callback = publish_file_dir,
})

vim.api.nvim_create_autocmd("UIEnter", {
    callback = function()
        if registered_server then
            return
        end

        local has_terminal_ui = vim.iter(vim.api.nvim_list_uis()):any(function(ui)
            return ui.stdin_tty
        end)
        if not has_terminal_ui then
            return
        end

        local server = vim.v.servername
        if server == "" then
            server = vim.fn.serverstart()
        end
        if tmux({ "set-option", "-p", "-t", pane_id, "@nvim_server", server }) then
            registered_server = server
            publish_file_dir()
        end
    end,
})

vim.api.nvim_create_autocmd("VimLeavePre", {
    callback = function()
        if not registered_server then
            return
        end

        local current_server = vim.trim(vim.fn.system({
            "tmux",
            "show-options",
            "-pqv",
            "-t",
            pane_id,
            "@nvim_server",
        }))
        if vim.v.shell_error == 0 and current_server == registered_server then
            tmux({ "set-option", "-pu", "-t", pane_id, "@nvim_server" })
            tmux({ "set-option", "-pu", "-t", pane_id, "@nvim_file_dir" })
        end
    end,
})
