return {
    "akinsho/toggleterm.nvim",
    version = "*",
    keys = {
        {
            "<C-\\>",
            function()
                local dir
                if vim.bo.filetype == "oil" then
                    dir = require("oil").get_current_dir()
                elseif vim.bo.buftype == "" then
                    local name = vim.api.nvim_buf_get_name(0)
                    if name ~= "" then
                        dir = vim.fs.dirname(name)
                    end
                end
                require("toggleterm").toggle(0, nil, dir, "float")
            end,
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
