-- Colorscheme: provides coloring for treesitter highlight groups.
-- Without a colorscheme, Neovim falls back to the built-in default theme, whose
-- treesitter group colors are too subtle to notice -- highlighting appears "missing".
return {
    "folke/tokyonight.nvim",
    lazy = false,
    priority = 1000,
    opts = {},
    config = function(_, opts)
        require("tokyonight").setup(opts)
        vim.cmd.colorscheme("tokyonight")
    end,
}
