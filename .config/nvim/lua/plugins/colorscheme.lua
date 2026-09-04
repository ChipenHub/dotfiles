-- Colorscheme: provides coloring for treesitter highlight groups.
-- Without a colorscheme, Neovim falls back to the built-in default theme, whose
-- treesitter group colors are too subtle to notice -- highlighting appears "missing".
return {
    "folke/tokyonight.nvim",
    lazy = false,
    priority = 1000,
    opts = {
        style = "night",
        on_colors = function(colors)
            colors.bg = "#000000"
            colors.bg_dark = "#000000"
            colors.bg_float = "#000000"
            colors.bg_popup = "#000000"
            colors.bg_sidebar = "#000000"
            colors.bg_statusline = "#000000"
        end,
    },
    config = function(_, opts)
        require("tokyonight").setup(opts)
        vim.cmd.colorscheme("tokyonight-night")
    end,
}
