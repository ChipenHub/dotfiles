# AGENTS.md: AI Agent Instructions for this Repository

This document provides guidelines for AI agents interacting with this Neovim configuration repository.

## 1. Project Overview

This repository contains a personal Neovim configuration written in Lua. The structure is built around the `lazy.nvim` plugin manager.

- **Configuration Root**: `init.lua` is the main entry point.
- **Core Config**: Resides in `lua/config/`.
- **Plugin Specs**: Located in `lua/plugins/`. Each file in this directory typically returns a table defining a plugin specification for `lazy.nvim`.
- **LSP & Tooling**: The configuration uses `lua-language-server` for Lua language features, with configuration in `.luarc.json`. Code formatting is enforced by `stylua`, configured in `.stylua.toml`.

## 2. Build, Lint, and Test

### Linting

The primary linting tool is `lua-language-server`, which should be integrated into your development environment. There is no separate linting command to run from the command line.

- **Tool**: `lua-language-server`
- **Configuration**: `.luarc.json`
- **Action**: When editing Lua files, adhere to the diagnostics provided by the language server. Pay special attention to undefined globals, with the exception of `vim`, which is a recognized global for Neovim configuration.

### Formatting

Code formatting is handled by `stylua`.

- **Tool**: `stylua`
- **Configuration**: `.stylua.toml`
- **Command**: To format a file, you can run:
  ```bash
  stylua lua/path/to/your/file.lua
  ```
- **Command (Whole Project)**: To format the entire project:
  ```bash
  stylua lua/
  ```
- **Action**: Always run `stylua` on any Lua files you create or modify.

### Testing

This repository does not have an automated test suite. "Testing" is performed by starting Neovim and manually verifying that the functionality works as expected.

- **Action**: After making any changes, start a new Neovim instance to ensure the configuration loads without errors and that the modified features behave correctly.

### Syncing Plugins

Plugin management is handled by `lazy.nvim`.

- **Action**: If you add a new plugin spec, you may need to sync it. You can do this by starting Neovim and running the `:Lazy sync` command.

## 3. Code Style Guidelines

Adherence to the existing code style is crucial for maintaining consistency.

### Formatting

- **Indent**: Use 4 spaces for indentation. Do not use tabs. This is enforced by `.stylua.toml`.
- **Line Endings**: Use Unix-style line endings (LF).
- **Line Length**: While not strictly enforced, aim for a line length of around 80-100 characters for better readability.

### Naming Conventions

- **Files**: Use lowercase `kebab-case` (e.g., `lazy-setup.lua`) or simple lowercase names.
- **Variables**: Use `snake_case` for local variables (e.g., `local win_count = 0`).
- **Modules**: Lua modules should be named logically based on their functionality. For example, a module handling keymaps is named `keymaps.lua`.

### Lua Conventions

- **Scope**: Always declare variables with `local` to limit their scope unless you are intentionally modifying a global variable.
- **Modules**: Code should be modular. Create logical modules under `lua/`.
  - Plugin configurations should be in their own files under `lua/plugins/`.
  - Each plugin file should return a table that `lazy.nvim` can process.
- **`require` statements**: Use `require()` to load modules. The path should be relative to the `lua/` directory.
  ```lua
  -- Good
  local utils = require("config.utils")

  -- Bad
  local utils = require("lua.config.utils")
  ```

### API Usage

- **Neovim API**: Use the `vim` global object to interact with the Neovim API (e.g., `vim.keymap.set`, `vim.api`, `vim.fn`). The `.luarc.json` is configured to recognize `vim` as a global.
- **Keymaps**: When setting keymaps with `vim.keymap.set`, always include a `desc` field to describe the keymap's function. This is used by plugins like `which-key.nvim`.
  ```lua
  vim.keymap.set("n", "<leader>w", "<cmd>wa<CR>", {
      noremap = true,
      silent = true,
      desc = "Save all files"
  })
  ```

### Comments

- Use comments (`--`) to explain the *why* behind complex or non-obvious code. Do not comment on the *what*.
- Add section headers to organize long files, especially for keymaps or options.

### Error Handling

- For a personal configuration, explicit error handling with `pcall` is not strictly necessary for every API call, but it can be useful when dealing with potentially faulty external commands or optional features. Use your judgment.

By following these guidelines, you will help maintain the quality and consistency of this codebase.
