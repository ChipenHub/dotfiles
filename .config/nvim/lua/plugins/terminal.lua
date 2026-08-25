return {
    "akinsho/toggleterm.nvim",
    version = "*",
    keys = {
        {
            "<C-\\>",
            "<cmd>ToggleTerm direction=float<CR>",
            mode = { "n", "t" },
            desc = "Toggle floating terminal",
        },
    },
    opts = {
        direction = "float",
        float_opts = {
            border = "curved",
        },
    },
}
