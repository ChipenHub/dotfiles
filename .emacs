;; set auto file place
(setq custom-file "~/.emacs.custom")
(load-file "~/.emacs.custom")

;; close the bell noise
(setq ring-bell-function 'ignore)
(set-face-attribute 'default nil
                    :font "JetBrainsMono Nerd Font"
                    :height 140)

;; close welcome page
(setq inhibit-startup-screen t)

;; ace-window
(global-set-key (kbd "M-o") #'ace-window)

;; kill buffer shortcut
(global-set-key (kbd "C-x C-k") #'kill-current-buffer)

;; melpa settings
(require 'package)
(setq package-archives
      '(("gnu"   . "https://elpa.gnu.org/packages/")
        ("nongnu" . "https://elpa.nongnu.org/nongnu/")
        ("melpa" . "https://melpa.org/packages/")))
(package-initialize)

;; initial fragment config
(add-to-list 'default-frame-alist '(width . 200))
(add-to-list 'default-frame-alist '(height . 50))

;; save option off
(setq make-backup-files nil)
(setq auto-save-default nil)

;; fragment size
(setq-default indent-tabs-mode nil)
(setq-default tab-width 4)
(setq-default standard-indent 4)
(setq-default c-basic-offset 4)

;; display settings
(column-number-mode 1)
(global-display-line-numbers-mode 1)
(tool-bar-mode 0)
(column-number-mode 1)

;; marginalia note of cordination
(use-package marginalia
  :ensure t
  :init
  (marginalia-mode))

;; srolling~
(pixel-scroll-precision-mode 1)
(use-package ultra-scroll
  :ensure t
  :init
  (ultra-scroll-mode 1))

;; divider
(setq window-divider-default-right-width 2)
(setq window-divider-default-bottom-width 2)
(window-divider-mode 1)

;; ido everywhere
(require 'ido)

(setq ido-enable-flex-matching t
      ido-everywhere t
      ido-case-fold t
      ido-use-virtual-buffers t
      ido-create-new-buffer 'always)
(ido-mode 1)
(recentf-mode 1)
(global-set-key (kbd "C-x b") #'ido-switch-buffer)
(global-set-key (kbd "C-x 4 b") #'ido-switch-buffer-other-window)
(global-set-key (kbd "C-x 5 b") #'ido-switch-buffer-other-frame)

;; enhance find: consult
;; Consult
(use-package consult
  :ensure t
  :bind
  (("C-s"     . consult-line)
   ("M-g g"   . consult-goto-line)
   ("M-g i"   . consult-imenu)
   ("M-y"     . consult-yank-pop)
   ("C-c r"   . consult-ripgrep)
   ("C-c f"   . consult-find)))
