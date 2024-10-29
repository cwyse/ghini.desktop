# syntax=docker/dockerfile:1.2

# Dockerfile

# Stage 1: Build Stage
FROM debian:bullseye AS build

# Configuration is stored in $HOME/.bauble/3.1/config

#
# Cut and pastable comments
#
ENV DOCKER_BUILD_CMD="\
          docker buildx build --ssh default                                                \
                              --build-arg REPO_COMMIT=$(git rev-parse ghini-3.1-dev-cjw)   \
                              --build-arg USER_ID=$(id -u)                                 \
                              --build-arg GROUP_ID=$(id -g)                                \
                              --load                                                       \
                              -t ghini-desktop:latest .                                    "

ENV DOCKER_RUN_CMD="\
          docker run --rm -it                                          \
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
                     -v /usr/lib/dri:/usr/lib/dri                      \
                     --device /dev/dri:/dev/dri                        \
                     --user $(id -u):$(id -g)                          \
                     ghini-desktop:latest bash -c ghini                "


## Set environment variables to suppress debconf warnings
ENV DEBIAN_FRONTEND=noninteractive

# Set up environment variables
ENV HOME=/root
ENV LINE=ghini-3.1-dev-cjw
ENV VIRTUAL_ENV=/opt/venv/$LINE
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
ENV USER=root

# Define build argument for cache busting
ARG REPO_COMMIT

# Install necessary system packages for building
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gettext \
    git \
    pkg-config \
    python3 \
    python3-dev \
    python3-venv \
    libpython3-dev \
    libjpeg-dev \
    libpq-dev \
    libxslt1-dev \
    zlib1g-dev \
    libcairo2 \
    libcairo2-dev \
    libgirepository1.0-dev \
    gir1.2-gtk-3.0 \
    gir1.2-gtkclutter-1.0 \
    gir1.2-champlain-0.12 \
    gir1.2-gtkchamplain-0.12 \
    krb5-user \
    libkrb5-dev \
    openssh-client \
    libcanberra-gtk-module \
    libcanberra-gtk3-module \
    gdk-pixbuf2.0-0 \
    libgdk-pixbuf2.0-dev \
    libglib2.0-dev \
    libgtk2.0-dev \
    libgl1-mesa-glx \
    libgl1-mesa-dri \
    && rm -rf /var/lib/apt/lists/*

# Configure SSH for GitLab
RUN mkdir -p $HOME/.ssh && chmod 700 $HOME/.ssh

# Add GitLab to known_hosts to prevent host key verification prompts
RUN ssh-keyscan gitlab.com >> $HOME/.ssh/known_hosts

# Clone ghini-desktop repository using SSH mount
RUN --mount=type=ssh \
    mkdir -p $HOME/Local/github/Ghini \
    && cd $HOME/Local/github/Ghini \
    && git clone -b $LINE git@gitlab.com:cwyse/ghini-desktop.git ghini-desktop && \
    dummy=$REPO_COMMIT


# Set the working directory to the cloned repository
WORKDIR $HOME/Local/github/Ghini/ghini-desktop

# Create and activate virtual environment, install dependencies
RUN python3 -m venv $VIRTUAL_ENV \
    && . $VIRTUAL_ENV/bin/activate \
    && pip install --upgrade pip wheel \
    && pip install 'setuptools<58.0.0' \
    && pip install PyGObject \
    && pip install psycopg2 \
    && pip install . \
    && pip install SQLAlchemy==1.2.7 alembic \
    && pip install 'sqlalchemy-diff==0.1.3' || echo "sqlalchemy-diff version incompatible, skipping" \
    && rm -rf $HOME/.cache/pip

# Initialize Alembic configuration (optional: modify alembic.ini for project setup)
RUN alembic init alembic

# Example configuration: Update alembic.ini with the database URL (if required)
RUN sed -i 's|sqlalchemy.url = .*|sqlalchemy.url = postgresql://192.168.40.32:9yuzebes@localhost:5432/ghini_test3|' alembic.ini
# Note: Replace 'username:password@localhost:5432/your_database' with actual DB credentials

# Stage 2: Runtime Stage
FROM debian:bullseye

# Add build arguments for user ID and group ID
ARG USER_ID
ARG GROUP_ID

# Set environment variables to suppress debconf warnings
ENV DEBIAN_FRONTEND=noninteractive

# Set up environment variables
ENV HOME=/home/ghini
ENV LINE=ghini-3.1-dev-cjw
ENV VIRTUAL_ENV=/opt/venv/$LINE
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
ENV USER=ghini
ENV NO_AT_BRIDGE=1

# Install necessary system packages for runtime
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    libpython3.9 \
    libjpeg62-turbo \
    libpq5 \
    libxslt1.1 \
    zlib1g \
    libcairo2 \
    libgirepository-1.0-1 \
    gir1.2-gtk-3.0 \
    gir1.2-gtkclutter-1.0 \
    gir1.2-champlain-0.12 \
    gir1.2-gtkchamplain-0.12 \
    krb5-user \
    libkrb5-3 \
    postgresql-client \
    libcanberra-gtk-module \
    libcanberra-gtk3-module \
    gdk-pixbuf2.0-0 \
    libgdk-pixbuf2.0-dev \
    libglib2.0-dev \
    libgtk2.0-dev \
    libgl1-mesa-glx \
    libgl1-mesa-dri \
    mesa-utils \
    at-spi2-core \
    libgdk-pixbuf2.0-bin \
    libgdk-pixbuf2.0-common \
    shared-mime-info \
    librsvg2-common \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Update gdk-pixbuf loaders cache
RUN /usr/lib/x86_64-linux-gnu/gdk-pixbuf-2.0/gdk-pixbuf-query-loaders --update-cache

# Create a group and user with the specified UID and GID
RUN groupadd --gid $GROUP_ID ghini && \
    useradd --uid $USER_ID --gid ghini --create-home ghini

# Create virtualenv directory
RUN mkdir -p /opt/venv

# Copy virtual environment from build stage with correct ownership
COPY --from=build --chown=ghini:ghini $VIRTUAL_ENV $VIRTUAL_ENV

# Ensure /app directory exists
RUN mkdir -p /app

# Copy application code from build stage with correct ownership
COPY --from=build --chown=ghini:ghini /root/Local/github/Ghini/ghini-desktop /app

# Switch to the ghini user
USER ghini

# Set the working directory
WORKDIR /app

# Set entrypoint
CMD ["ghini"]
