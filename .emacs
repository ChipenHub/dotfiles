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

;; magit config
(with-eval-after-load 'magit
  (setq magit-diff-refine-hunk 'all)
  (setq magit-diff-fontify-hunk 'all)
  (set-face-attribute 'magit-diff-file-heading nil
                      :weight 'bold
                      :height 1.1)
  (set-face-attribute 'magit-diff-hunk-heading nil
                      :weight 'bold)
  (set-face-attribute 'magit-diff-hunk-heading-highlight nil
                      :weight 'bold))

(with-eval-after-load 'magit
  (set-face-attribute 'magit-section-heading nil
                      :weight 'bold
                      :height 1.15)

  (set-face-attribute 'magit-diff-file-heading nil
                      :weight 'bold
                      :height 1.15)

  (set-face-attribute 'magit-branch-local nil
                      :weight 'bold)

  (set-face-attribute 'magit-branch-remote nil
                      :weight 'bold))

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

;; close lines number;
(dolist (hook '(magit-mode-hook
                dired-mode-hook
                vterm-mode-hook
                shell-mode-hook
                compilation-mode-hook))
  (add-hook hook
            (lambda ()
              (display-line-numbers-mode -1))))

;; vertico
(use-package vertico
  :ensure t
  :init
  (vertico-mode 1))

;; marginalia
(use-package marginalia
  :ensure t
  :init
  (marginalia-mode 1))

;; Consult search
(use-package consult
  :ensure t
  :bind
  (("C-x b"   . consult-buffer)
   ("C-s"     . consult-line)
   ("M-g i"   . consult-imenu)
   ("M-y"     . consult-yank-pop)
   ("C-c r"   . consult-ripgrep)
   ("C-x C-r" . consult-recent-file)))
