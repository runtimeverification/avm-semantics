ARG K_DISTRO=jammy
ARG K_VERSION
FROM runtimeverificationinc/kframework-k:ubuntu-${K_DISTRO}-${K_VERSION}

RUN    apt-get update            \
    && apt-get upgrade --yes     \
    && apt-get install --yes     \
            cmake                \
            curl                 \
            debhelper            \
            default-jdk-headless \
            graphviz             \
            libcrypto++-dev      \
            libcurl4-openssl-dev \
            libmsgpack-dev       \
            libprocps-dev        \
            libsecp256k1-dev     \
            libssl-dev           \
            libyaml-dev          \
            maven                \
            pkg-config           \
            zlib1g-dev

ARG USER_ID=1000
ARG GROUP_ID=1000
RUN groupadd -g $GROUP_ID user && useradd -m -u $USER_ID -s /bin/sh -g user user

# Install pyenv
ENV PYTHON_VERSION 3.10.6
ENV PYENV_ROOT /home/user/.pyenv
ENV PATH $PYENV_ROOT/shims:$PYENV_ROOT/bin:$PATH
RUN set -ex \
    && curl https://pyenv.run | bash \
    && pyenv install $PYTHON_VERSION \
    && pyenv global $PYTHON_VERSION  \
    && pyenv rehash

RUN    curl -sSL https://install.python-poetry.org | POETRY_HOME=/usr python3 - \
    && poetry --version
RUN poetry config virtualenvs.in-project true
RUN poetry config virtualenvs.prefer-active-python true

