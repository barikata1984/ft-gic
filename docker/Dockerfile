# =============================================================================
# Isaac Sim 5.1.0 Development Container
# =============================================================================
# Base: NVIDIA Isaac Sim 5.1.0 (NGC official image)
# Adds:  Dev tooling, non-root user, extra Python packages
#
# Prerequisites:
#   docker login nvcr.io  (NGC API key required)
#
# Build:  docker compose build
# Run:    docker compose up -d
# Attach: docker compose exec isaac-sim zsh
#
# Simulation (headless):
#   /isaac-sim/python.sh /workspace/scripts/simulate_rope.py
# =============================================================================

FROM nvcr.io/nvidia/isaac-sim:5.1.0

# Build steps run as root
USER root

ENV DEBIAN_FRONTEND=noninteractive

# ---- System packages --------------------------------------------------------
RUN apt-get update && apt-get install -y --no-install-recommends \
        # Shell & terminal
        zsh \
        tmux \
        # VCS & build essentials
        git \
        git-lfs \
        curl \
        wget \
        unzip \
        build-essential \
        # Editor (fallback)
        nano \
        vim \
        # Utilities
        sudo \
        gosu \
        locales \
        ca-certificates \
        openssh-client \
        less \
        jq \
    && locale-gen en_US.UTF-8 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

ENV LANG=en_US.UTF-8
ENV LC_ALL=en_US.UTF-8

# ---- Expose Isaac Sim's Python wrapper on PATH ------------------------------
# /isaac-sim/python.sh sets up the correct LD_LIBRARY_PATH and PYTHONPATH
ENV PATH="/isaac-sim:${PATH}"

# ---- Fix permissions on /isaac-sim ------------------------------------------
# NGC image may ship with o-x on the directory or .sh files.
# chmod the directory (traversal) and all .sh files while still root.
RUN chmod o+rx /isaac-sim \
    && find /isaac-sim -maxdepth 2 -name "*.sh" -exec chmod a+rx {} \;

# ---- Pre-create kit cache/data directories with runtime-user ownership ------
# Kit --portable モードは /isaac-sim/kit/{cache,data,logs} に書き込む。
# isaac-sim ユーザー(uid=1234)所有で HOST_UID が異なると失敗するため、
# ビルド時に作成して HOST_UID に chown しておく。
ARG HOST_UID=1000
ARG HOST_GID=1000
RUN mkdir -p /isaac-sim/kit/cache /isaac-sim/kit/data /isaac-sim/kit/logs \
    && chown ${HOST_UID}:${HOST_GID} \
         /isaac-sim/kit/cache \
         /isaac-sim/kit/data \
         /isaac-sim/kit/logs

# ---- Make Isaac Sim's Python the default python / python3 / pip -------------
# python.sh sets LD_LIBRARY_PATH and PYTHONPATH before calling the real binary,
# so wrapping it here gives every downstream call the correct Isaac Sim env.
RUN printf '#!/bin/bash\nexec /isaac-sim/python.sh "$@"\n' \
        > /usr/local/bin/python3 \
    && chmod +x /usr/local/bin/python3 \
    && ln -sf /usr/local/bin/python3 /usr/local/bin/python \
    && printf '#!/bin/bash\nexec /isaac-sim/python.sh -m pip "$@"\n' \
        > /usr/local/bin/pip3 \
    && chmod +x /usr/local/bin/pip3 \
    && ln -sf /usr/local/bin/pip3 /usr/local/bin/pip

# ---- Extra Python packages (into Isaac Sim's environment) -------------------
COPY requirements.txt /tmp/requirements.txt
RUN /isaac-sim/python.sh -m pip install --no-cache-dir -r /tmp/requirements.txt \
    && rm /tmp/requirements.txt

# ---- Non-root user (UID/GID injected at build time) ------------------------
ARG HOST_UID=1000
ARG HOST_GID=1000
ARG HOST_USER=developer

RUN if getent group ${HOST_GID} >/dev/null 2>&1; then \
        existing_grp=$(getent group ${HOST_GID} | cut -d: -f1); \
        [ "$existing_grp" != "${HOST_USER}" ] && groupmod -n ${HOST_USER} "$existing_grp"; \
    else \
        groupadd -g ${HOST_GID} ${HOST_USER}; \
    fi \
    && if getent passwd ${HOST_UID} >/dev/null 2>&1; then \
         existing_usr=$(getent passwd ${HOST_UID} | cut -d: -f1); \
         usermod -l ${HOST_USER} -s /bin/zsh -g ${HOST_GID} \
                 -d /home/${HOST_USER} -m "$existing_usr"; \
       else \
         useradd -m -s /bin/zsh -u ${HOST_UID} -g ${HOST_GID} ${HOST_USER}; \
       fi \
    && echo "${HOST_USER} ALL=(ALL) NOPASSWD:ALL" \
       >> /etc/sudoers.d/${HOST_USER} \
    && chmod 0440 /etc/sudoers.d/${HOST_USER}

# ---- Entrypoint -------------------------------------------------------------
COPY entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

WORKDIR /workspace
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
CMD ["sleep", "infinity"]
