#!/bin/bash
set -e
# =============================================================================
# Container entrypoint — GIC (nvidia/cuda:12.1.0-devel-ubuntu22.04)
#
# - Bootstraps zsh config for the runtime user on first run
# - Ensures user home directories exist with correct ownership
# - Drops to non-root user via gosu
#
# Deliberately omits Isaac Sim-specific steps (cache chowns, editable install).
# =============================================================================

TARGET_USER="${HOST_USER:-developer}"
TARGET_HOME=$(getent passwd "${TARGET_USER}" 2>/dev/null | cut -d: -f6 || echo "/home/${TARGET_USER}")
TARGET_GROUP=$(id -gn "${TARGET_USER}" 2>/dev/null || echo "${TARGET_USER}")

# ---- zsh bootstrap (only on first container start) --------------------------
if [ ! -f "${TARGET_HOME}/.zshrc" ]; then
    mkdir -p "${TARGET_HOME}"
    cat > "${TARGET_HOME}/.zshrc" << 'ZSHRC'
autoload -Uz compinit && compinit
autoload -Uz vcs_info
precmd() { vcs_info }
zstyle ':vcs_info:git:*' formats ' (%b)'
setopt PROMPT_SUBST
PROMPT='%F{cyan}%~%f${vcs_info_msg_0_} %F{yellow}[gic]%f %F{green}>%f '

HISTFILE=~/.zsh_history
HISTSIZE=10000
SAVEHIST=10000
setopt SHARE_HISTORY HIST_IGNORE_DUPS

alias ll='ls -lah --color=auto'
alias la='ls -A --color=auto'

# GIC repo is expected at /workspace/gic
alias cdgic='cd /workspace/gic'
ZSHRC
    chown "${TARGET_USER}:${TARGET_GROUP}" "${TARGET_HOME}/.zshrc"
fi

# ---- Ensure standard user dirs exist with correct ownership -----------------
for d in "${TARGET_HOME}/.cache" \
         "${TARGET_HOME}/.local" \
         "${TARGET_HOME}/.config" \
         "${TARGET_HOME}/.claude"; do
    mkdir -p "$d"
    chown "${TARGET_USER}:${TARGET_GROUP}" "$d" 2>/dev/null || true
done

# ---- Drop to non-root user and exec command ---------------------------------
if [ "$(id -u)" = "0" ] && [ "${TARGET_USER}" != "root" ]; then
    exec gosu "${TARGET_USER}" "$@"
else
    exec "$@"
fi
