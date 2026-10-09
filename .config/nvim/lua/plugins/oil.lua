return {
    "stevearc/oil.nvim",
    lazy = false,
    dependencies = {
        {
            "malewicz1337/oil-git.nvim",
            opts = {
                show_file_highlights = true,
                show_directory_highlights = true,
                show_file_symbols = true,
                show_directory_symbols = true,
                symbol_position = "eol",
            },
        },
    },
    keys = {
        { "-", "<cmd>Oil<CR>", desc = "Open parent directory" },
    },
    opts = {
        default_file_explorer = true,
        keymaps = {
            ["<C-s>"] = false,
            ["<C-h>"] = false,
            ["<M-v>"] = { "actions.select", opts = { vertical = true, split = "belowright" } },
            ["<M-s>"] = { "actions.select", opts = { horizontal = true, split = "belowright" } },
        },
        columns = {
            "permissions",
            "size",
            "mtime",
        },
        constrain_cursor = "name",
        view_options = {
            show_hidden = true,
            natural_order = "fast",
        },
    },
}
