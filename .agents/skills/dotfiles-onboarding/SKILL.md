---
name: dotfiles-onboarding
version: 1.0.0
description: "管理本仓库 dotfiles：把已有配置迁移进仓库、检查敏感内容，并通过 .install.sh 只安装对应配置。"
---

# dotfiles 配置追踪（新增或变更）

## 使用时机
- 用户要求把某个工具/应用的本地配置加入本仓库管理。

## 执行原则
1. **先判断来源位置**：一定先确认家目录下真实配置文件是否存在，再决定是否追踪。
2. **先审查隐私**：如果配置文件里有密钥、token、个人敏感路径、或你不想同步的机器特有内容，先停止并请用户确认，不要直接迁移。
3. **路径映射**：将配置按家目录相对路径放到仓库。
   - `$HOME/.config/broot/conf.hjson` -> `.config/broot/conf.hjson`
   - `$HOME/.cache/...` -> `.cache/...`
4. **不追踪自动生成的状态文件**：诸如安装标记、运行时缓存、会变化的临时文件不要直接追踪（例如 `broot/launcher/installed-v4`）。
5. **只安装对应内容**：
   - `.install.sh` 使用显式白名单；不要根据仓库目录自动推断安装项。
   - `./.install.sh`：只显示可安装目标及其路径，不执行安装。
   - `./.install.sh fish`：只安装 fish。
   - `./.install.sh tmux fish`：安装多个指定目标。
   - `./.install.sh all`：同步白名单中的全部目标，并移除上次安装但已从白名单删除的链接。
   - 安装记录保存在 `${XDG_STATE_HOME:-$HOME/.local/state}/dotfiles/installed-paths`。
   - 目标位置已有非符号链接的文件或目录时拒绝覆盖，由用户先处理。
6. **安装后校验**：检查目标是否已链接到仓库，并确认程序生成的运行时文件仍被 Git 忽略。

## 常见命令
```bash
# 查看 .install.sh 支持的目标及路径
./.install.sh

# 只安装 fish 配置
./.install.sh fish

# 安装多个目标
./.install.sh tmux fish

# 安装白名单中的全部目标
./.install.sh all
```

## broot 示例

### 追踪内容
- `.config/broot/conf.hjson`
- `.config/broot/verbs.hjson`
- `.config/broot/skins/*.hjson`

### 处理说明
- 不追踪 `~/.config/broot/launcher/installed-v4`（为运行时状态文件）。