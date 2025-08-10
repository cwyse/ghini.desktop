#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# Update package list
apt-get update

# Install missing dependencies
MISSING=''

if ! command -v msgfmt >/dev/null 2>&1; then
    MISSING="$MISSING gettext"
fi
if ! command -v python3 >/dev/null 2>&1; then
    MISSING="$MISSING python3-minimal"
fi
if ! python3 -c 'import gi; gi.require_version' >/dev/null 2>&1; then
    MISSING="$MISSING python3-gi"
fi
if ! python3 -c 'import gi; gi.require_version("Clutter", "1.0"); gi.require_version("GtkClutter", "1.0"); from bauble.gtkinit import Clutter, GtkClutter' >/dev/null 2>&1; then
    MISSING="$MISSING gir1.2-gtkclutter-1.0"
fi
if ! python3 -c 'import gi; gi.require_version("Champlain", "0.12"); from bauble.gtkinit import Champlain' >/dev/null 2>&1; then
    MISSING="$MISSING gir1.2-champlain-0.12"
fi
if ! python3 -c 'import lxml' >/dev/null 2>&1; then
    MISSING="$MISSING python3-lxml"
fi
if ! command -v git >/dev/null 2>&1; then
    MISSING="$MISSING git"
fi
if ! command -v virtualenv >/dev/null 2>&1; then
    MISSING="$MISSING virtualenv"
fi
if ! command -v xslt-config >/dev/null 2>&1; then
    MISSING="$MISSING libxslt1-dev"
fi
if ! command -v pkg-config >/dev/null 2>&1; then
    MISSING="$MISSING pkg-config"
fi
if ! pkg-config --cflags jpeg >/dev/null 2>&1; then
    MISSING="$MISSING libjpeg-dev"
fi
if ! command -v gcc >/dev/null 2>&1; then
    MISSING="$MISSING build-essential"
fi
PYTHONHCOUNT=$(find /usr/include/python3* /usr/local/include/python3* -name Python.h 2>/dev/null | wc -l)
if [ "$PYTHONHCOUNT" = "0" ]; then
    MISSING="$MISSING libpython3-dev"
fi

if [ "$MISSING" != "" ]; then
    echo "Installing missing dependencies: $MISSING"
    apt-get install -y --no-install-recommends $MISSING
fi

# Set up environment variables
export HOME=/root
export LINE=ghini-3.1

# Clone ghini.desktop repository
mkdir -p $HOME/Local/github/Ghini
cd $HOME/Local/github/Ghini
git clone https://github.com/Ghini/ghini.desktop
cd ghini.desktop
git checkout $LINE

# Create virtual environment
mkdir -p $HOME/.virtualenvs
virtualenv --python python3 $HOME/.virtualenvs/$LINE --system-site-packages
. $HOME/.virtualenvs/$LINE/bin/activate

# Install PostgreSQL adapter
pip install psycopg2

# Build and install Ghini
python setup.py build
python setup.py install

# Clean up
rm -rf $HOME/.cache/pip
