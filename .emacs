;;; package bootstrap ----------------------------------------------------------

(require 'package)

(setq package-archives
      '(("gnu"    . "https://elpa.gnu.org/packages/")
        ("nongnu" . "https://elpa.nongnu.org/nongnu/")
        ("melpa"  . "https://melpa.org/packages/")))

;; 启动时让 Emacs 的包管理和 URL 请求走本地代理。
(setq url-proxy-services
      '(("http"     . "127.0.0.1:7897")
        ("https"    . "127.0.0.1:7897")
        ("no_proxy" . "localhost,127.0.0.1")))

(package-initialize)

;; 第一次启动或者本地没有软件包索引时，自动刷新索引。
(unless package-archive-contents
  (package-refresh-contents))

;; use-package 自己也需要先安装。
(unless (package-installed-p 'use-package)
  (package-install 'use-package))

(require 'use-package)

;; 此后所有 use-package 声明都会自动安装缺失的软件包。
(setq use-package-always-ensure t)


;;; custom file ---------------------------------------------------------------

(setq custom-file (expand-file-name "~/.emacs.custom.el"))

;; 文件不存在时不要报错。
(load custom-file 'noerror 'nomessage)


;;; basic UI ------------------------------------------------------------------

;; 关闭提示音。
(setq ring-bell-function #'ignore)

(set-face-attribute
 'default nil
 :font "JetBrainsMono Nerd Font"
 :height 140)

;; 关闭欢迎页。
(setq inhibit-startup-screen t)

;; 初始窗口大小。
(add-to-list 'default-frame-alist '(width . 200))
(add-to-list 'default-frame-alist '(height . 50))

;; 不生成备份文件和自动保存文件。
(setq make-backup-files nil)
(setq auto-save-default nil)

;; 缩进设置。
(setq-default indent-tabs-mode nil)
(setq-default tab-width 4)
(setq-default standard-indent 4)
(setq-default c-basic-offset 4)

;; 显示设置。
(column-number-mode 1)
(global-display-line-numbers-mode 1)
(tool-bar-mode 0)


;;; window management ---------------------------------------------------------

(use-package ace-window
  :bind
  ("M-o" . ace-window))

(global-set-key (kbd "C-x C-k") #'kill-current-buffer)

(setq window-divider-default-right-width 2)
(setq window-divider-default-bottom-width 2)
(window-divider-mode 1)


;;; completion annotations ----------------------------------------------------

(use-package marginalia
  :init
  (marginalia-mode 1))


;;; scrolling -----------------------------------------------------------------

;; Emacs 内置功能，不需要安装。
(when (fboundp 'pixel-scroll-precision-mode)
  (pixel-scroll-precision-mode 1))

(use-package ultra-scroll
  :init
  (ultra-scroll-mode 1))


;;; ido -----------------------------------------------------------------------

;; ido 是 Emacs 内置包，不需要安装。
(use-package ido
  :ensure nil
  :init
  (setq ido-enable-flex-matching t
        ido-everywhere t
        ido-case-fold t
        ido-use-virtual-buffers t
        ido-create-new-buffer 'always)

  (ido-mode 1)
  (ido-everywhere 1)

  :bind
  (("C-x b"   . ido-switch-buffer)
   ("C-x 4 b" . ido-switch-buffer-other-window)
   ("C-x 5 b" . ido-switch-buffer-other-frame)))

;; recentf 也是内置包。
(use-package recentf
  :ensure nil
  :init
  (recentf-mode 1))


;;; consult -------------------------------------------------------------------

(use-package consult
  :bind
  (("C-s"   . consult-line)
   ("M-g g" . consult-goto-line)
   ("M-g i" . consult-imenu)
   ("M-y"   . consult-yank-pop)
   ("C-c r" . consult-ripgrep)
   ("C-c f" . consult-find)))


;;; project -------------------------------------------------------------------

(use-package projectile
  :init
  (projectile-mode 1)
  :bind-keymap
  ("C-c p" . projectile-command-map))


;;; file refresh / autosave ---------------------------------------------------

;; 自动保存到原文件。
(auto-save-visited-mode 1)
(setq auto-save-visited-interval 3)

;; 文件被外部修改时自动刷新。
(global-auto-revert-mode 1)
