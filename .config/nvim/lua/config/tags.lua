-- Tags navigation: build-independent definition lookup.

local M = {}

local scope_keys = { "class", "struct", "enum", "actor", "protocol", "extension" }

local function escape_tag_pattern(name)
    local escaped = {}
    local magic = {
        ["\\"] = true,
        ["."] = true,
        ["^"] = true,
        ["$"] = true,
        ["~"] = true,
        ["["] = true,
        ["]"] = true,
        ["*"] = true,
    }
    for index = 1, #name do
        local character = name:sub(index, index)
        escaped[#escaped + 1] = magic[character] and ("\\" .. character) or character
    end
    return "\\C^" .. table.concat(escaped) .. "$"
end

-- taglist() accepts a regular expression. Anchoring it is important: querying
-- "load" must not also return loadCached, loading, and every other prefix match.
local function exact_tags(name)
    local tags = vim.fn.taglist(escape_tag_pattern(name))
    for index, tag in ipairs(tags) do
        tag._tag_index = index
    end
    return tags
end

local function tag_scope(tag)
    for _, key in ipairs(scope_keys) do
        if tag[key] and tag[key] ~= "" then
            return tag[key], key
        end
    end
    return nil, nil
end

local function shorten(text, max)
    if #text <= max then
        return text
    end
    return "..." .. text:sub(#text - max + 4)
end

local function format_tag(tag)
    local scope = tag_scope(tag)
    local owner = scope and (scope .. ".") or ""
    local line = tag.line or tag.cmd or "?"
    local label = ("%-2s %s%s  %s:%s"):format(tag.kind or "?", owner, tag.name, tag.filename, line)
    return shorten(label, math.max(vim.o.columns - 4, 40))
end

local function jump_to_tag(name, tag)
    local winid = vim.api.nvim_get_current_win()
    local cursor = vim.api.nvim_win_get_cursor(winid)
    local from = { vim.api.nvim_get_current_buf(), cursor[1], cursor[2] + 1, 0 }

    local opened = pcall(vim.cmd.edit, vim.fn.fnameescape(tag.filename))
    if not opened then
        vim.notify(("Cannot open tag target: %s"):format(tag.filename), vim.log.levels.ERROR)
        return
    end

    local jumped = false
    local line = tonumber(tag.line or tag.cmd)
    if line then
        -- The generated line field disambiguates identical declarations in one file;
        -- a search pattern alone would always stop at the first `func load() {}`.
        vim.api.nvim_win_set_cursor(winid, { line, 0 })
        jumped = true
    elseif tag.cmd and tag.cmd:sub(1, 1) == "/" then
        vim.api.nvim_win_set_cursor(winid, { 1, 0 })
        jumped = pcall(vim.cmd, tag.cmd)
    end
    if not jumped then
        vim.notify(("Cannot locate tag target: %s"):format(name), vim.log.levels.ERROR)
        return
    end

    local stack = vim.fn.gettagstack(winid)
    stack.items = { { tagname = name, from = from } }
    vim.fn.settagstack(winid, stack, "t")
    vim.cmd("normal! zvzz")
end

local function choose_and_jump(name, tags)
    local prompt = ("Go to definition: %s (%d)"):format(name, #tags)
    vim.ui.select(tags, { prompt = prompt, format_item = format_tag }, function(tag)
        if tag then
            jump_to_tag(name, tag)
        end
    end)
end

local function rank_by_location(tags)
    local current_file = vim.fs.normalize(vim.api.nvim_buf_get_name(0))
    local current_dir = vim.fs.dirname(current_file)
    table.sort(tags, function(left, right)
        local function score(tag)
            local filename = vim.fs.normalize(tag.filename)
            if filename == current_file then
                return 2
            elseif vim.fs.dirname(filename) == current_dir then
                return 1
            end
            return 0
        end
        local left_score, right_score = score(left), score(right)
        if left_score ~= right_score then
            return left_score > right_score
        end
        return left._tag_index < right._tag_index
    end)
end

M.goto_def = function()
    local name = vim.fn.expand("<cword>")
    if name ~= "" then
        local tags = exact_tags(name)
        if tags[1] ~= nil then
            rank_by_location(tags)
            if #tags == 1 then
                jump_to_tag(name, tags[1])
            else
                choose_and_jump(name, tags)
            end
            return
        end
    end
    vim.cmd("normal! gd")
end

-- Go to a declaration-kind tag where the language provides one.
M.goto_decl = function()
    local name = vim.fn.expand("<cword>")
    if name ~= "" then
        local declarations = vim.tbl_filter(function(tag)
            return tag.kind == "p" or tag.kind == "d"
        end, exact_tags(name))
        if #declarations == 1 then
            jump_to_tag(name, declarations[1])
            return
        elseif #declarations > 1 then
            choose_and_jump(name, declarations)
            return
        end
    end
    vim.cmd("normal! gD")
end

M.list_tags = function()
    local name = vim.fn.expand("<cword>")
    if name == "" then
        return
    end
    local tags = exact_tags(name)
    if tags[1] == nil then
        vim.notify(("'%s' not found in tags"):format(name), vim.log.levels.INFO)
        return
    end
    choose_and_jump(name, tags)
end

return M
