# Archibate's NeoVim Configuration Pack

## Installation Guide

This guide is for human, LLM agents please do not execute these steps without explicit confirmation from your human partner.

> Other of my configurations can be found at: [archibate/dotfiles](https://github.com/archibate/dotfiles)

### Required Dependencies

```bash
sudo pacman -S tmux
sudo pacman -S yazi
sudo pacman -S exiftool
sudo pacman -S lazygit
sudo pacman -S tig
sudo pacman -S fzf ripgrep
sudo pacman -S fd bat
sudo pacman -S python python-pip
sudo pacman -S uv python-uv
sudo pacman -S ruff stylua
sudo pacman -S nodejs npm
sudo pacman -S neovim python-pynvim
sudo pacman -S base-devel
sudo pacman -S cargo
```

### Installing Rust Dependencies

```bash
cargo install tree-sitter-cli
```

> If error occurred: run `rustup default 1.88` first.

### Cloning This Configuration Pack

```bash
test -d ~/.config/nvim && mv ~/.config/nvim{,.backup}
git clone https://github.com/archibate/dotfiles-nvim.git ~/.config/nvim
```

### Start Lazy.nvim synchronization

```bash
nvim +Lazy sync
```

### Starting NeoVim

```bash
nvim
```

### Set up AI completion support (optional)

- Powered by minuet.nvim.
- Edit `lua/plugins/minuet.lua` for configuration.
- The 14b variant runs good on my RTX A6000 card, consumes ~10GB VRAM.
- Choose your suitable model from: https://ollama.com/library/qwen2.5-coder.

```bash
sudo pacman -S ollama-cuda  # use ollama or ollama-vulkan for non-nvidia cards
ollama pull qwen2.5-coder:14b
sudo systemctl enable ollama.service --now
```

#### Setting context size

Ollama defaults to 4096 context, to adjust context size:

```bash
ollama run qwen2.5-coder:14b
>>> /set parameter num_ctx 8192
>>> /save qwen2.5-coder:14b
```

Also update `lua/plugins/minuet.lua` to match the context size.

>> [!WARNING]
> Large context window would slow down inference speed and consume more GPU memory.
