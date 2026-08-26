return {
    "stevearc/oil.nvim",
    lazy = false,
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
