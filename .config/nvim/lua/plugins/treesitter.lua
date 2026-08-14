-- Syntax highlighting: highlighting only, no LSP / textobjects / indentation modules.
-- When a parser is missing, :TSInstall is triggered automatically so highlighting is
-- available the next time the file is opened.
return {
    "nvim-treesitter/nvim-treesitter",
    branch = "main",
    lazy = false,
    build = ":TSUpdate",
    config = function()
        require("nvim-treesitter").setup()

        -- Enable treesitter highlighting for each opened file by filetype.
        vim.api.nvim_create_autocmd("FileType", {
            pattern = "*",
            group = vim.api.nvim_create_augroup("treesitter_highlight", { clear = true }),
            callback = function(args)
                local lang = vim.treesitter.language.get_lang(vim.bo[args.buf].filetype)
                if not lang then
                    return
                end
                if pcall(vim.treesitter.language.add, lang) then
                    pcall(vim.treesitter.start, args.buf, lang)
                else
                    -- Parser not installed: install asynchronously and prompt to reopen the file.
                    vim.cmd("TSInstall " .. lang)
                    vim.notify(("treesitter: installing parser '%s', reopen the file after install to enable highlighting"):format(lang), vim.log.levels.INFO)
                end
            end,
        })
    end,
}
