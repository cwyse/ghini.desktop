#!/bin/bash

sudo apt update -y
sudo apt install -y make build-essential libssl-dev zlib1g-dev libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm libncurses5-dev libncursesw5-dev xz-utils tk-dev libffi-dev liblzma-dev python3-openssl git
if [ ! -d ~/.pyenv ]; then 
    git clone https://github.com/pyenv/pyenv.git ~/.pyenv
fi
snippet=$(mktemp)
echo 'export PYENV_ROOT="$HOME/.pyenv"' > ${snippet} 2>&1
echo 'export PATH="$PYENV_ROOT/bin:$PATH"' >> ${snippet} 2>&1
echo -e 'if command -v pyenv 1>/dev/null 2>&1; then\n eval "$(pyenv init -)"\nfi' >> ${snippet} 2>&1
if ! grep PYENV_ROOT ~/.bashrc > /dev/null 2>&1; then
    cat ${snippet} >> ~/.bashrc
fi
cat ${snippet}
eval "$(cat ${snippet})"
pyenv versions
if [ ! -d $(pyenv root)/plugins/pyenv-virtualenv ]; then
    git clone https://github.com/pyenv/pyenv-virtualenv.git $(pyenv root)/plugins/pyenv-virtualenv
fi
echo 'eval "$(pyenv virtualenv-init -)"' > ${snippet}
cat ${snippet}
if ! grep 'virtualenv-init' ~/.bashrc > /dev/null 2>&1; then 
    cat ${snippet} >> ~/.bashrc
fi
eval "$(cat ${snippet})"
pyenv install -f -s -g 3.5.9

