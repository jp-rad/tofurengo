# See here for image contents: https://github.com/devcontainers/images/tree/main/src/python
# Available image variants: https://github.com/devcontainers/templates/blob/main/src/python/devcontainer-template.json
ARG VARIANT="3"
FROM mcr.microsoft.com/devcontainers/python:1-${VARIANT}

# Remove deprecated Yarn APT repository if present
RUN rm -f /etc/apt/sources.list.d/yarn.list \
    && rm -f /usr/share/keyrings/yarn.gpg \
    && rm -f /etc/apt/trusted.gpg.d/yarn.gpg

# [Option] Install Node.js
ARG INSTALL_NODE="true"
ARG NODE_VERSION="lts/*"
RUN if [ "${INSTALL_NODE}" = "true" ]; then su vscode -c "umask 0002 && . /usr/local/share/nvm/nvm.sh && nvm install ${NODE_VERSION} 2>&1"; fi

# [Optional] If your pip requirements rarely change, uncomment this section to add them to the image.
# COPY requirements.txt /tmp/pip-tmp/
# RUN pip3 --disable-pip-version-check --no-cache-dir install -r /tmp/pip-tmp/requirements.txt \
#    && rm -rf /tmp/pip-tmp

# [Optional] Uncomment this section to install additional OS packages.
# RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
#     && apt-get -y install --no-install-recommends <your-package-list-here>

# [Optional] Uncomment this line to install global node packages.
# RUN su vscode -c "source /usr/local/share/nvm/nvm.sh && npm install -g <your-package-here>" 2>&1

# # [Optional] Uncomment this section to install additional OS packages.
# RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
#     && apt-get -y install --no-install-recommends \
#     libreoffice \
#     # pycairo - relatorio
#     libcairo2-dev pkg-config python3-dev \
#     # texexec - relatorio
#     context


# mdbtools provides the CLI utilities (mdb-export, mdb-tables, mdb-sql)
# required by tools/loaders/load_dwpi_mdb.py for reading Access .mdb files.
# Version depends on the base image; check available versions with:
#   apt-cache madison mdbtools
# For Japanese table names (e.g., "Moji Zokusei Jisho"), mdbtools >= 0.9.2 is recommended.
RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
    && apt-get -y install --no-install-recommends \
    mdbtools

# Create directory and set permission
RUN mkdir /home/vscode/dev \ 
    && chown -R vscode:vscode /home/vscode/dev
RUN mkdir /home/vscode/dev/.vscode \
    && chown vscode:vscode /home/vscode/dev/.vscode
RUN mkdir /home/vscode/.vscode-server \
    && chown vscode:vscode /home/vscode/.vscode-server

# [Optional] If your pip requirements rarely change, uncomment this section to add them to the image.
COPY ./dev/requirements_dev.txt /tmp/pip-tmp/
RUN pip3 --disable-pip-version-check --no-cache-dir install --upgrade -r /tmp/pip-tmp/requirements_dev.txt \
    && rm -rf /tmp/pip-tmp
