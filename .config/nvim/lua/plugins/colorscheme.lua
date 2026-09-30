-- Core visual plugins: the colorscheme and a single-line buffer list.
-- Without a colorscheme, Neovim falls back to the built-in default theme, whose
-- treesitter group colors are too subtle to notice -- highlighting appears "missing".
return {
    {
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
                    Visual = { bg = "#383838" },
                },
            },
        },
        config = function(_, opts)
            require("nightfox").setup(opts)
            vim.cmd.colorscheme("carbonfox")
        end,
    },
    {
        "akinsho/bufferline.nvim",
        event = "VeryLazy",
        opts = {
            options = {
                mode = "buffers",
                numbers = "none",
                indicator = {
                    style = "underline",
                },
                modified_icon = "●",
                left_trunc_marker = "‹",
                right_trunc_marker = "›",
                max_name_length = 24,
                max_prefix_length = 12,
                truncate_names = true,
                tab_size = 18,
                diagnostics = false,
                show_buffer_icons = false,
                show_buffer_close_icons = false,
                show_close_icon = false,
                show_tab_indicators = false,
                separator_style = "thin",
                always_show_bufferline = true,
                sort_by = "id",
            },
        },
    },
}
