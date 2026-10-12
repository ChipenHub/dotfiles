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
    config = function(_, opts)
        local oil = require("oil")
        oil.setup(opts)

        -- Inspect the full action list so mixed edits still require confirmation.
        local confirmation = require("oil.mutator.confirmation")
        local show = confirmation.show
        confirmation.show = function(actions, _, callback)
            local only_creates = true
            for _, action in ipairs(actions) do
                if action.type ~= "create" then
                    only_creates = false
                    break
                end
            end
            return show(actions, not only_creates, callback)
        end
    end,
    opts = {
        default_file_explorer = true,
        keymaps = {
            ["q"] = {
                function()
                    local oil = require("oil")
                    if vim.bo.modified then
                        vim.notify("Save Oil changes with :w before closing", vim.log.levels.WARN)
                        return
                    end
                    oil.close({ exit_if_last_buf = true })
                end,
                mode = "n",
                desc = "Close Oil only when changes are saved",
            },
            ["<C-h>"] = false,
            ["<C-s>"] = false,
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
