local pane_id = vim.env.TMUX_PANE

if not pane_id then
    return
end

local registered_server

local function tmux(args)
    vim.fn.system(vim.list_extend({ "tmux" }, args))
    return vim.v.shell_error == 0
end

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
        end
    end,
})
