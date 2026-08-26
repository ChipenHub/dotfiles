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
