-- Colorscheme: provides coloring for treesitter highlight groups.
-- Without a colorscheme, Neovim falls back to the built-in default theme, whose
-- treesitter group colors are too subtle to notice -- highlighting appears "missing".
return {
    "EdenEast/nightfox.nvim",
    lazy = false,
    priority = 1000,
    opts = {
        palettes = {
            carbonfox = {
                bg0 = "#080808",
                bg1 = "#181818",
                bg2 = "#101010",
                bg3 = "#181818",
                bg4 = "#202020",
            },
        },
        groups = {
            carbonfox = {
                GitSignsCurrentLineBlame = { fg = "#404040" },
            },
        },
    },
    config = function(_, opts)
        require("nightfox").setup(opts)
        vim.cmd.colorscheme("carbonfox")
    end,
}
