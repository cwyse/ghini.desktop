# syntax=docker/dockerfile:1.4

# Dockerfile 

# Stage 1: Build Stage
FROM debian:bullseye AS build

# Configuration is stored in $HOME/.bauble/3.1/config

# Environment setup and commands for Docker build and run
ENV DOCKER_BUILD_CMD="\
          docker buildx build --no-cache                                                   \
                              --ssh default                                                \
                              --progress=plain                                             \
                              --build-arg COMMIT=$(git rev-parse HEAD)                     \
                              --build-arg BUILD_DATE=$(date -u +'%Y-%m-%dT%H:%M:%SZ')      \
                              --build-arg USER_ID=$(id -u)                                 \
                              --build-arg GROUP_ID=$(id -g)                                \
                              --load -f Dockerfile                                         \
                              -t ghini-desktop:latest .                                    "

ENV DOCKER_RUN_CMD="\
          xhost + &&                                                   \
          docker run --rm -it                                          \
                     -p 5678:5678                                      \
                     -e DEBUG=false                                    \
                     -e USER=ghini                                     \
                     -e DISPLAY=$DISPLAY                               \
                     -e DB_HOST=postgres.wysechoice.net                \
                     -e DB_PORT=5432                                   \
                     -e DB_NAME=ghini_test3                            \
                     -e DB_USER=ghini                                  \
                     -e DB_SSLMODE=prefer                              \
                     -e KRB5_CONFIG=/krb5/krb5.conf                    \
                     -e KRB5_CLIENT_KTNAME=/krb5/krb5.keytab           \
                     -e NO_AT_BRIDGE=1                                 \
                     -v /tmp/.X11-unix:/tmp/.X11-unix                  \
                     -v $HOME/krb5:/krb5:ro                            \
                     -v $HOME/.bauble/3.1:/home/ghini/.bauble/3.1      \
                     -v $HOME/debug/ghini.desktop:/app                 \
                     -v /usr/lib/dri:/usr/lib/dri                      \
                     --device /dev/dri:/dev/dri                        \
                     --user $(id -u):$(id -g)                          \
                     --name ghini                                      \
                     ghini-desktop:latest                              "


## Set environment variables to suppress debconf warnings
ENV DEBIAN_FRONTEND=noninteractive

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV HOME=/root
ENV LINE=migrate_to_1.3
ENV VIRTUAL_ENV=/opt/venv/$LINE
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
ENV USER=root
ENV PYTHONUSERBASE=$VIRTUAL_ENV
ENV PYTHONNOUSERSITE=0

# Install system packages for building
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gettext \
    git \
    gdk-pixbuf2.0-0 \
    gir1.2-champlain-0.12 \
    gir1.2-gtk-3.0 \
    gir1.2-gtkchamplain-0.12 \
    gir1.2-gtkclutter-1.0 \
    glade \
    gtk-update-icon-cache \
    krb5-user \
    libcairo2 \
    libcairo2-dev \
    libcanberra-gtk-module \
    libcanberra-gtk3-module \
    libffi-dev \
    libglib2.0-dev \
    libgl1-mesa-dri \
    libgl1-mesa-glx \
    libgirepository1.0-dev \
    libgdk-pixbuf2.0-dev \
    libgtk2.0-dev \
    libgtk-3-dev \
    libjpeg-dev \
    libkrb5-dev \
    libpq-dev \
    libpython3-dev \
    libxslt1-dev \
    openssh-client \
    pkg-config \
    python3 \
    python3-dev \
    python3-gi \
    python3-pip \
    python3-venv \
    shared-mime-info \
    xdg-utils \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

# SSH setup for GitLab
RUN mkdir -p $HOME/.ssh && chmod 700 $HOME/.ssh \
    && ssh-keyscan gitlab.com >> $HOME/.ssh/known_hosts

# Working directory for the application
WORKDIR /app

# Copy project files including .git for setuptools_scm to retrieve version
COPY . /app
COPY .git /app/.git

RUN ls -la /app/.git || echo "/app/.git not found"

# Set up Python virtual environment and install setuptools_scm to retrieve version
RUN python3 -m venv $VIRTUAL_ENV \
    && . $VIRTUAL_ENV/bin/activate \
    && pip install --upgrade pip wheel setuptools debugpy setuptools_scm

# Retrieve version from repo and store in a file
RUN . $VIRTUAL_ENV/bin/activate \
    && VERSION=$(python3 -c 'import setuptools_scm; print(setuptools_scm.get_version())') \
    && echo "$VERSION" > /VERSION

# Set up Python virtual environment and install the package
RUN . $VIRTUAL_ENV/bin/activate \
    && pip install .[dev,docs] --no-cache-dir


# Initialize Alembic with a preconfigured database URL
RUN . $VIRTUAL_ENV/bin/activate \
    && pip install alembic \
    && alembic init alembic \
    && sed -i 's|sqlalchemy.url = .*|sqlalchemy.url = postgresql://ghini:9yuzebes@192.168.40.32:5432/ghini_test3|' alembic.ini \
    && rm -rf $HOME/.cache/pip

# Stage 2: Runtime Stage
FROM debian:bullseye

# User and group configuration
ARG USER_ID
ARG GROUP_ID
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV HOME=/home/ghini
ENV LINE=migrate_to_1.3
ENV VIRTUAL_ENV=/opt/venv/$LINE
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
ENV USER=ghini
ENV NO_AT_BRIDGE=1

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    adwaita-icon-theme \
    at-spi2-core \
    gdk-pixbuf2.0-0 \
    gir1.2-champlain-0.12 \
    gir1.2-gtk-3.0 \
    gir1.2-gtkchamplain-0.12 \
    gir1.2-gtkclutter-1.0 \
    git \
    glade \
    gnome-icon-theme \    
    gtk-update-icon-cache \
    hicolor-icon-theme \
    krb5-user \
    libcairo2 \
    libcanberra-gtk-module \
    libcanberra-gtk3-module \
    libgdk-pixbuf2.0-bin \
    libgdk-pixbuf2.0-common \
    libgl1-mesa-dri \
    libgl1-mesa-glx \
    libglib2.0-dev \
    libgirepository-1.0-1 \
    libgtk2.0-dev \
    libglib2.0-dev \
    libgtk-3-dev \
    libjpeg62-turbo \
    libkrb5-3 \
    libpq5 \
    libpython3.9 \
    libxslt1.1 \
    librsvg2-common \
    mesa-utils \
    net-tools \
    postgresql-client \
    procps \
    python3 \
    shared-mime-info \
    vim \
    xdg-utils \
    zlib1g \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# GDK-pixbuf loaders cache
RUN /usr/lib/x86_64-linux-gnu/gdk-pixbuf-2.0/gdk-pixbuf-query-loaders --update-cache

# Create user and group
RUN groupadd --gid $GROUP_ID ghini && \
    useradd --uid $USER_ID --gid ghini --create-home ghini

# Copy virtual environment and application files from the build stage
COPY --from=build --chown=ghini:ghini $VIRTUAL_ENV $VIRTUAL_ENV
COPY --from=build --chown=ghini:ghini /app /app

# Copy VERSION file from build stage and use it as an ENV variable
#COPY --from=build /VERSION /VERSION
#RUN export VERSION=$(cat /VERSION)
#ENV VERSION=${VERSION}
COPY --from=build /VERSION /VERSION
ENV VERSION_FILE=/VERSION
RUN VERSION=$(cat $VERSION_FILE) && echo "VERSION=$VERSION" && echo "VERSION=$VERSION" > /VERSION_ENV
ENV VERSION="`cat /VERSION_ENV | cut -d= -f2`"

# Expose debug port for debugpy
EXPOSE 5678

RUN <<EOF
cat > $VIRTUAL_ENV/bin/ghini <<EOL
#!/bin/bash
GITHOME=/app
source $VIRTUAL_ENV/bin/activate

while getopts us:mp f
do
case $f in
 u)  cd $GITHOME
     BUILD=1
     END=1
     ;;
 s)  cd $GITHOME
     git checkout ghini-$OPTARG || exit 1
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

if [ ! -z \"$BUILD\" ]
then
 git pull
 python setup.py build
 python setup.py install
fi

if [ ! -z \"$END\" ]
then
 exit 1
fi

ghini
EOL
chmod +x $VIRTUAL_ENV/bin/ghini
chown ghini:ghini $VIRTUAL_ENV/bin/ghini
EOF

RUN <<EOF
cat > /usr/local/bin/ghini <<EOL
#!/bin/bash
source $VIRTUAL_ENV/bin/activate
exec $VIRTUAL_ENV/bin/ghini \"\$@\"
EOL
chmod +x /usr/local/bin/ghini
chown ghini:ghini /usr/local/bin/ghini
EOF

ENV PYTHONVERBOSE=1

RUN <<EOF
mkdir -p /usr/local/share/applications
cat > /usr/local/share/applications/ghini.desktop <<EOL
[Desktop Entry]
Type=Application
Name=Ghini Desktop
Version=$VERSION
GenericName=Biodiversity Manager
Icon=$VIRTUAL_ENV/share/icons/hicolor/scalable/apps/ghini.svg
TryExec=/usr/local/bin/ghini
Exec=/usr/local/bin/ghini
Terminal=false
StartupNotify=false
Categories=Qt;Education;Science;Geography;
Keywords=botany;botanic;
EOL
chown ghini:ghini /usr/local/share/applications/ghini.desktop
EOF

# Set build arguments for dynamic metadata
ARG COMMIT
ARG BUILD_DATE
ENV BUILD_DATE=${BUILD_DATE}

# OCI-compliant labels
LABEL org.opencontainers.image.title="Ghini Desktop Application" \
      org.opencontainers.image.description="Ghini Desktop Application for managing biodiversity data." \
      org.opencontainers.image.authors="Chris Wyse <chris.wyse@wysechoice.net>, Ross Demuth <rossdemuth123@gmail.com>, Mario Frasca <mario@anche.no>,  Brett Adams <brett@belizebotanic.org>" \
      org.opencontainers.image.url="https://gitlab.com/cwyse/ghini-desktop" \
      org.opencontainers.image.documentation="https://docs.ghini.io" \
      org.opencontainers.image.source="https://gitlab.com/cwyse/ghini-desktop" \
      org.opencontainers.image.licenses="GPLv2" \
      org.opencontainers.image.version="${VERSION}" \
      org.opencontainers.image.revision="${COMMIT}" \
      org.opencontainers.image.created="${BUILD_DATE}" \
      org.opencontainers.image.base.name="debian:bullseye"


# Set working directory and entry point
WORKDIR /app
ENV DEBUG=true

# CMD to run debugpy if DEBUG=true, else launch ghini
#CMD if [ "$DEBUG" = "true" ]; then \
#        python3 -m debugpy --wait-for-client --log-to debugpy.log --listen 0.0.0.0:5678 /app/scripts/ghini; \
#    else \
#        /app/scripts/ghini; \
#    fi

COPY --chown=ghini:ghini entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

# Switch to the non-root user
USER ghini

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]

