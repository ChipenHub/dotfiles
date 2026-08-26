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
                require("gitsigns").diffthis()
            end,
            desc = "Diff current file against index",
        },
    },
}
