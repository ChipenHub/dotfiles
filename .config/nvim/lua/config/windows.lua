local M = {}

local function file_window(win)
    return vim.api.nvim_win_is_valid(win)
        and vim.api.nvim_win_get_config(win).relative == ""
        and vim.bo[vim.api.nvim_win_get_buf(win)].buftype == ""
end

function M.split_buffer(direction)
    local source = vim.api.nvim_get_current_win()
    local current = vim.api.nvim_get_current_buf()
    if not file_window(source) then
        vim.notify("Choose a file window before splitting", vim.log.levels.INFO)
        return
    end

    local buffers = vim.tbl_filter(function(buf)
        return vim.bo[buf.bufnr].buftype == ""
    end, vim.fn.getbufinfo({ buflisted = 1 }))
    table.sort(buffers, function(a, b)
        if a.lastused == b.lastused then
            return a.bufnr < b.bufnr
        end
        return a.lastused > b.lastused
    end)

    vim.ui.select(buffers, {
        prompt = "Open buffer in " .. direction .. " split:",
        format_item = function(buf)
            local name = buf.name == "" and "[No Name]" or vim.fn.fnamemodify(buf.name, ":~:.")
            local modified = vim.bo[buf.bufnr].modified and " [+]" or ""
            local same_file = buf.bufnr == current and " (current file: another view)" or ""
            return name .. modified .. same_file
        end,
    }, function(buf)
        -- The picker may be asynchronous; never create a split on cancellation
        -- or substitute another window if its original target has disappeared.
        if not buf or not file_window(source) or not vim.api.nvim_buf_is_valid(buf.bufnr) then
            return
        end
        vim.api.nvim_open_win(buf.bufnr, true, { win = source, split = direction })
    end)
end

function M.cycle_layout()
    local layout = vim.fn.winlayout()
    if
        vim.api.nvim_win_get_config(0).relative ~= ""
        or layout[1] == "leaf"
        or #layout[2] ~= 2
        or layout[2][1][1] ~= "leaf"
        or layout[2][2][1] ~= "leaf"
    then
        return
    end

    local first, second = layout[2][1][2], layout[2][2][2]
    local size = layout[1] == "row" and vim.api.nvim_win_get_width or vim.api.nvim_win_get_height
    -- Normalize an uneven layout first; one cell of rounding still counts as equal.
    if math.abs(size(first) - size(second)) <= 1 then
        vim.fn.win_splitmove(second, first, { vertical = layout[1] == "col", rightbelow = true })
    end
    vim.cmd.wincmd("=")
end

function M.move_window()
    local source = vim.api.nvim_get_current_win()
    if not file_window(source) then
        return
    end

    local target = require("window-picker").pick_window({
        filter_func = function(wins)
            return vim.tbl_filter(function(win)
                return win ~= source and file_window(win)
            end, wins)
        end,
    })
    if not target then
        return
    end

    -- A one-key prompt needs a command line even when cmdheight is normally 0.
    local cmdheight = vim.o.cmdheight
    vim.o.cmdheight = math.max(1, cmdheight)
    vim.api.nvim_echo({ { "Place window: h=left j=below k=above l=right (Esc cancels)" } }, false, {})
    local ok, key = pcall(vim.fn.getcharstr)
    vim.api.nvim_echo({ { "" } }, false, {})
    vim.o.cmdheight = cmdheight
    if not ok or not ({ h = true, j = true, k = true, l = true })[key] then
        return
    end
    if not file_window(source) or not file_window(target) then
        return
    end

    local result = vim.fn.win_splitmove(source, target, {
        vertical = key == "h" or key == "l",
        rightbelow = key == "j" or key == "l",
    })
    if result == 0 then
        vim.api.nvim_set_current_win(source)
    end
end

return M
