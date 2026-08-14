-- tags (ctags) navigation: no LSP dependency, relies only on an existing tags file.
--
-- Prerequisite: the tags file is generated externally (ctags); this config does not
-- generate it. Tag lookup uses Neovim's default 'tags=./tags;,tags', which searches
-- upward from the current file's directory for the nearest tags file -- naturally
-- satisfying the "nearest location" navigation requirement.

local M = {}

-- Shorten an overly long tag entry: when the path exceeds max, keep the tail and
-- replace the front with "...". e.g. /a/very/long/path/to/file.lua:42 -> .../to/file.lua:42
local function shorten(entry, max)
    local shown = entry.filename .. ":" .. (entry.cmd or "")
    if #shown <= max then
        return shown
    end
    return "..." .. shown:sub(#shown - max + 4)
end

-- Render the multi-match list via vim.ui.select (omitting the front of long paths),
-- then jump to the chosen entry and push it onto the tag stack.
local function choose_and_jump(cword, tags)
    local max = vim.o.columns - 24 -- leave room for the symbol name, line number and padding (min 20)
    if max < 20 then
        max = 20
    end
    local items = {}
    for i, e in ipairs(tags) do
        items[i] = shorten(e, max)
    end
    vim.ui.select(items, { prompt = ("Go to definition: %s (%d)"):format(cword, #tags) }, function(_, idx)
        if not idx then
            return
        end
        -- :{N}tag {name} jumps to the Nth match and pushes it onto the stack,
        -- keeping <C-t>/g[ fallback working.
        vim.cmd(("%dtag %s"):format(idx, vim.fn.escape(cword, "/")))
    end)
end

-- Go to definition: try a tag first -- a single match jumps directly and pushes the
-- stack; multiple matches open a selection list (omitting the front of long paths).
-- Falls back to native gd (definition search within the current buffer) when no tag.
M.goto_def = function()
    local cword = vim.fn.expand("<cword>")
    if cword ~= "" then
        local tags = vim.fn.taglist(cword)
        if tags[1] ~= nil then
            if #tags == 1 then
                vim.cmd("tag " .. vim.fn.escape(cword, "/"))
            else
                choose_and_jump(cword, tags)
            end
            return
        end
    end
    vim.cmd("normal! gd")
end

-- Go to declaration (gD): a declaration entry in the tags, or fall back to native gD.
M.goto_decl = function()
    local cword = vim.fn.expand("<cword>")
    if cword ~= "" then
        local tags = vim.fn.taglist(cword)
        local decl = vim.tbl_filter(function(t)
            return t.kind == "p" or t.kind == "d" -- prototype / macro-definition
        end, tags)[1]
        if decl then
            vim.cmd("tag " .. vim.fn.escape(cword, "/"))
            return
        end
    end
    vim.cmd("normal! gD")
end

-- Find references: search the current symbol with ripgrep in the working directory,
-- sending results to the quickfix list. (ctags does not record references, so this is
-- a complementary part of the navigation suite -- imperfect but practical.)
M.find_refs = function()
    local cword = vim.fn.expand("<cword>")
    if cword == "" then
        return
    end
    if vim.fn.executable("rg") ~= 1 then
        vim.notify("Finding references requires ripgrep (rg)", vim.log.levels.WARN)
        return
    end
    -- Word-boundary match, excluding the tags file itself and .git.
    local cmd = { "rg", "--vimgrep", "-w", "--no-heading", "--color=never", "-g", "!tags", "-g", "!.git", cword, vim.fn.getcwd() }
    local out = vim.system(cmd, { text = true }):wait()
    if out.code ~= 0 or not out.stdout or out.stdout == "" then
        vim.notify(("No references found for '%s'"):format(cword), vim.log.levels.INFO)
        return
    end
    local qf = {}
    for line in vim.gsplit(out.stdout, "\n", { trimempty = true }) do
        local file, lnum, col, text = line:match("^(.-):(%d+):(%d+):(.*)$")
        if file then
            qf[#qf + 1] = { filename = file, lnum = tonumber(lnum), col = tonumber(col), text = text }
        end
    end
    if #qf == 0 then
        return
    end
    vim.fn.setqflist(qf)
    vim.cmd("copen")
    vim.notify(("%d reference(s)"):format(#qf), vim.log.levels.INFO)
end

-- List all tag entries for the current symbol (:tselect).
M.list_tags = function()
    local cword = vim.fn.expand("<cword>")
    if cword == "" then
        return
    end
    if vim.fn.taglist(cword)[1] == nil then
        vim.notify(("'%s' not found in tags"):format(cword), vim.log.levels.INFO)
        return
    end
    vim.cmd("tselect " .. vim.fn.escape(cword, "/"))
end

return M
