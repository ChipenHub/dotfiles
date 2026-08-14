-- Set up XDG directories via LAZY_STDPATH (set by wrapper script)
-- The lazy.nvim bootstrap will handle this

-- Load core config
require("config.options")
require("config.keymaps")

-- Bootstrap lazy.nvim and load plugin specs
require("config.lazy-setup")
