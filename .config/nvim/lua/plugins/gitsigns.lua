return {
    "lewis6991/gitsigns.nvim",
    event = { "BufReadPre", "BufNewFile" },
    opts = {
        current_line_blame = true,
        current_line_blame_opts = {
            delay = 300,
        },
    },
    keys = {
        {
            "<leader>gp",
            function()
                require("gitsigns").preview_hunk()
            end,
            desc = "Preview Git hunk",
        },
        {
            "<leader>gb",
            function()
                require("gitsigns").blame_line({ full = true })
            end,
            desc = "Show Git blame for current line",
        },
        {
            "<leader>gd",
            function()
                require("gitsigns").diffthis("HEAD", nil, function(err)
                    if err then
                        vim.notify(err, vim.log.levels.ERROR)
                        return
                    end

                    for _, win in ipairs(vim.api.nvim_tabpage_list_wins(0)) do
                        if vim.wo[win].diff then
                            vim.wo[win].foldenable = false
                        end
                    end
                end)
            end,
            desc = "Diff current file against HEAD",
        },
    },
}
