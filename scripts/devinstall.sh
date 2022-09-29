#!/bin/bash

if [ $# -ne 0 ]
then
    VERSION=$1
    LINE=ghini-$1
else
    VERSION=3.1-dev
    LINE=ghini-3.1-dev
fi

PG=1
#echo missing in vanilla ubuntu - to run 'pip install bauble'
#echo libxslt1-dev python-all-dev gettext

pyenv local 3.5.9-debug
pyenv virtualenv -f 3.5.9-debug $LINE
pyenv local $LINE
pyenv virtualenv-init -
i#pip install --ignore-installed PyGObject
#pip install vext
#pip install vext.gi
#pip install lxml
#while true
#do
#    MISSING=''
#    if ! sudo --version >/dev/null 2>&1; then
#        MISSING="$MISSING sudo"
#    fi
#    if ! msgfmt --version >/dev/null 2>&1; then
#        MISSING="$MISSING gettext"
#    fi
#    if ! python3 --version >/dev/null 2>&1; then
#        MISSING="$MISSING python3-minimal"
#    fi
#    if ! python3 -c 'import gi; gi.require_version' >/dev/null 2>&1; then
#        MISSING="$MISSING python3-gi python3-gi-cairo gir1.2-gtk-3.0"
#    fi
#    if ! python3 -c 'import gi; gi.require_version("Clutter", "1.0"); gi.require_version("GtkClutter", "1.0"); from gi.repository import Clutter, GtkClutter' >/dev/null 2>&1; then
#        MISSING="$MISSING gir1.2-gtkclutter"
#    fi
#    if ! python3 -c 'import gi; gi.require_version("Clutter", "1.0"); gi.require_version("GtkClutter", "1.0"); from gi.repository import Clutter, GtkClutter; gi.require_version("Champlain", "0.12"); from gi.repository import GtkChamplain; GtkClutter.init([]); from gi.repository import Champlain' >/dev/null 2>&1; then
#        MISSING="$MISSING gir1.2-gtkchamplain-0.12"
#    fi
#    if ! python3 -c 'import lxml' >/dev/null 2>&1; then
#        MISSING="$MISSING python3-lxml"
#    fi
#    if ! git help >/dev/null 2>&1; then
#        MISSING="$MISSING git"
#    fi
#    if ! virtualenv --help >/dev/null 2>&1; then
#        MISSING="$MISSING virtualenv"
#    fi
#    if ! xslt-config --help >/dev/null 2>&1; then
#        MISSING="$MISSING libxslt1-dev"
#    fi
#   # if ! pkg-config --help >/dev/null 2>&1; then
#        MISSING="$MISSING pkg-config"
#    fi
#    if ! pkg-config --cflags jpeg --help >/dev/null 2>&1; then
#        MISSING="$MISSING libjpeg-dev"
#    fi
#    if ! gcc --version >/dev/null 2>&1; then
#        MISSING="$MISSING build-essential"
#    fi
#    PYTHONHCOUNT=$(find /usr/include/python3* /usr/local/include/python3* -name Python.h 2>/dev/null | wc -l)
#    if [ "$PYTHONHCOUNT" = "0" ]; then
#        MISSING="$MISSING libpython3-all-dev"
#    fi
#
#    # forget password, please.
#    sudo -k
#
#    if [ "$MISSING" == "" ]
#    then
#        break;
#    else
#        echo 'Guessing package names, if you get in a loop, please double check.'
#        echo 'In Debian terms, you need to solve the following dependencies:'
#        echo '------------------------------------------------------------------'
#        echo $MISSING
#        echo '------------------------------------------------------------------'
#        echo 'Then restart the devinstall.sh script'
#        echo
#        if [ -x /usr/bin/apt-get ]
#        then
#            echo 'you are on a debian-like system, I should know how to proceed'
#            echo sudo apt-get -y install $MISSING xapp
#        elif [ -x /usr/bin/pacman ]
#        then
#            echo 'your system looks like Archlinux, I give it a try'
#            MISSING=$(echo $MISSING |
#                          sed -e 's/build-essential/gcc make libc-dev/' |
#                          sed -e 's/virtualenv/python-virtualenv/' |
#                          sed -e 's/python3-lxml/python-lxml/' |
#                          sed -e 's/libjpeg-dev/libjpeg-turbo/' |
#                          sed -e 's/python3-gi/python-gobject/' |
#                          sed -e 's/gir1.2-gtkclutter/clutter-gtk/' |
#                          sed -e 's/gir1.2-gtkchamplain-0.12/libchamplain/')
#            sudo pacman -S $MISSING
#        elif [ -x /usr/bin/rpm ]
#        then
#            echo 'your system looks like RedHat.'
#            exit 1
#        else
#            echo 'so sorry, I have no clue about your system.'
#            exit 1
#        fi
#        echo -n 'press <ENTER> to re-run devinstall.sh, or Ctrl-C to stop'
#        read
#    fi
#done

if [ -d $HOME/Local/github/Ghini/ghini.desktop ]
then
    echo "ghini checkout already in place"
    cd $HOME/Local/github/Ghini
else
    mkdir -p $HOME/Local/github/Ghini >/dev/null 2>&1
    cd $HOME/Local/github/Ghini
    git clone https://github.com/Ghini/ghini.desktop
fi
cd ghini.desktop

git checkout $LINE

if [ ! -z $PG ]
then
    echo 'installing postgresql adapter'
    pyenv exec pip install psycopg2 ;
fi

pyenv exec aptitude install python3-gi python3-gi-cairo gir1.2-gtk-3.0 xapp python3-minimal gettext gir1.2-gtkclutter gir1.2-gtkchamplain-0.12 git libxslt1-dev pkg-config libjpeg-dev build-essential libjpeg-dev libpython3-all-dev
pyenv exec pip install sphinx==1.7.9
pyenv exec pip install python-dateutil==2.7.3
pyenv exec pip install pyparsing==2.2.0
pyenv exec pip install fibra==0.0.20
pyenv exec pip install requests==2.25.1
pyenv exec pip install gdata-python3==3.0.1
pyenv exec pip install jinja2==2.10
pyenv exec pip install mako==1.0.7
pyenv exec pip install pyqrcode==1.2.1
pyenv exec pip install Pillow==2.3.0
pyenv exec pip install raven==6.7.0
pyenv exec pip install SQLAlchemy==1.2.7
pyenv exec pip install lxml==4.5.0
pyenv exec pip install gobject
pyenv exec pip install PyGObject
pyenv exec pip install 2to3 

if [ ! -z $MYSQL ]
then
    echo 'installing mysql adapter'
    pip install mysqlclient ;    
fi

pyenv exec python setup.py build
pyenv exec python setup.py install
mkdir -p $HOME/bin 2>/dev/null
cat <<EOF > $HOME/bin/ghini
#!/bin/bash

GITHOME=$HOME/Local/github/Ghini/ghini.desktop/
pyenv activate $LINE

while getopts us:mp f
do
  case \$f in
    u)  cd \$GITHOME
        BUILD=1
        END=1
        ;;
    s)  cd \$GITHOME
        git checkout ghini-\$OPTARG || exit 1
        BUILD=1
        END=1
        ;;
    m)  pip install mysqlclient
        END=1
        ;;
    p)  pip install psycopg2
        END=1
        ;;
  esac
done

if [ ! -z "\$BUILD" ]
then
    git pull
    python setup.py build
    python setup.py install
fi

if [ ! -z "\$END" ]
then
    exit 1
fi

ghini
EOF
chmod +x $HOME/bin/ghini

echo your local installation is now complete.
echo enter your password to make Ghini available to other users.

sudo groupadd ghini 2>/dev/null 
sudo usermod -a -G ghini $(whoami)
chmod -R g-w+rX,o-rwx $HOME/.pyenv/versions/$LINE
sudo chgrp -R ghini $HOME/.pyenv/versions/$LINE
cat <<EOF | sudo tee /usr/local/bin/ghini > /dev/null
#!/bin/bash
pyenv activate $LINE
$PYENV_ROOT/versions/$LINE/bin/ghini
EOF
sudo chmod +x /usr/local/bin/ghini

sudo mkdir -p /usr/local/share/applications/ >/dev/null 2>&1
cat <<EOF | sudo tee /usr/local/share/applications/ghini.desktop > /dev/null
#!/bin/bash
[Desktop Entry]
Type=Application
Name=Ghini Desktop
Version=$VERSION
GenericName=Biodiversity Manager
Icon=$PYENV_ROOT/versions/$LINE/share/icons/hicolor/scalable/apps/ghini.svg
TryExec=/usr/local/bin/ghini
Exec=/usr/local/bin/ghini
Terminal=false
StartupNotify=false
Categories=Qt;Education;Science;Geography;
Keywords=botany;botanic;
EOF
