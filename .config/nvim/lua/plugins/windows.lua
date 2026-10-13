return {
    "smart-splits-nvim/smart-splits.nvim",
    version = "^3.0.0",
    -- The backend must claim the pane before tmux can forward Alt keys to us.
    lazy = false,
    dependencies = {
        {
            "smart-splits-nvim/backend-tmux",
            main = "smart-splits-backend-tmux",
            opts = { resize_amount = 1 },
        },
        {
            "s1n7ax/nvim-window-picker",
            version = "2.*",
            opts = {
                hint = "floating-letter",
                show_prompt = false,
            },
        },
    },
    opts = {
        move = { at_edge = "stop" },
        resize = { amount = 1 },
        mux = { backend = vim.env.TMUX and "smart-splits-backend-tmux" or nil },
    },
    config = function(_, opts)
        local splits = require("smart-splits")
        local windows = require("config.windows")
        for _, motion in ipairs({ { "h", "left" }, { "j", "down" }, { "k", "up" }, { "l", "right" } }) do
            local key, direction = unpack(motion)
            vim.keymap.set({ "n", "i", "t" }, "<M-" .. key .. ">", splits["move_cursor_" .. direction], {
                desc = "Focus window " .. direction .. " (Neovim first, then tmux)",
            })
            vim.keymap.set({ "n", "i", "t" }, "<M-" .. key:upper() .. ">", splits["resize_" .. direction], {
                desc = "Resize window " .. direction .. " (Neovim first, then tmux)",
            })
        end
        for _, split in ipairs({ { "v", "right" }, { "s", "below" } }) do
            local key, direction = unpack(split)
            vim.keymap.set({ "n", "i", "t" }, "<M-" .. key .. ">", function()
                vim.cmd.stopinsert()
                vim.schedule(function()
                    windows.split_buffer(direction)
                end)
            end, { desc = "Choose buffer for " .. direction .. " split" })
        end
        vim.keymap.set({ "n", "i", "t" }, "<M-Space>", windows.cycle_layout, {
            desc = "Cycle Neovim layout, or tmux layout with one window",
        })
        vim.keymap.set("n", "<leader>m", windows.move_window, { desc = "Move window beside a chosen window" })
        splits.setup(opts)
    end,
}
