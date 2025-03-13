# Running Pytest in a Docker Container from the Command Line

## System Dependencies (Host Machine)  

The goal of this setup is to **minimize host dependencies** while keeping the entire testing environment **inside Docker**.  
On the host machine, you only need:

### **Required Host Packages**  
```sh
sudo apt update && sudo apt install -y --no-install-recommends     docker.io     docker-buildx-plugin     x11-xserver-utils  # Required for GUI applications inside Docker
```

### **Why These Are Needed**  
| Package | Purpose |
|---------|---------|
| `docker.io` | Enables containerized execution of tests |
| `docker-buildx-plugin` | Required for advanced multi-platform builds |
| `x11-xserver-utils` | Allows GUI applications (if needed) to display from the container |

---

## Prerequisites  

### **1. Install Docker & BuildX (if not already installed)**  
Ensure you have **Docker** and **BuildX** installed:

  ```sh
sudo apt install -y docker.io docker-buildx-plugin
sudo systemctl enable --now docker
  ```

> **Note:** Ensure your user has permission to run Docker without `sudo`:  
> ```sh
> sudo usermod -aG docker $USER
> ```

### **2. Clone the Repository**  
Ensure you are in the desired directory and clone the repository:  

```sh
git clone git@gitlab.com:cwyse/ghini-desktop.git
cd ghini-desktop
```

---

## Building the Docker Image  

To build the Docker test image, navigate to the **root of the repository** and execute:  

```sh
          docker buildx build --no-cache                                                   \
                              --ssh default                                                \
                              --progress=plain                                             \
                              --build-arg COMMIT=$(git rev-parse HEAD)                     \
                              --build-arg BUILD_DATE=$(date -u +'%Y-%m-%dT%H:%M:%SZ')      \
                              --build-arg USER_ID=$(id -u)                                 \
                              --build-arg GROUP_ID=$(id -g)                                \
                              --load -f Dockerfile.test                                    \
                              -t ghini-desktop-test:latest .
```

### **Dependencies Handled in Docker**  

The **Docker container** will install the following system dependencies **internally**:

```dockerfile
RUN apt-get update && apt-get install -y --no-install-recommends     libgirepository1.0-dev     libgtk-3-dev     libglib2.0-dev     libcairo2-dev     python3-gi     gir1.2-gtk-3.0     gir1.2-gtkchamplain-0.12     gir1.2-gtkclutter-1.0     python3-venv     python3-pip     python3-setuptools     python3-wheel     libpq-dev  # PostgreSQL libraries for psycopg2
```

> **Why are these inside Docker?**  
> These are application-level dependencies that should remain isolated from the host system.  
> No need to install them manually!  

---

## Running the Tests  

Once the image is built, run the container with the following command:

```sh
          xhost + &&                                                   \
          PYTEST_ARGS='--maxfail=1 -s -v'                              \
          docker run --rm -it                                          \
                     -p 5678:5678                                      \
                     -e DEBUG=false                                    \
                     -e USER=ghini                                     \
                     -e DISPLAY=$DISPLAY                               \
                     -e PYTEST_ARGS=$PYTEST_ARGS                       \
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
                     --name ghini_test                                 \
                     ghini-desktop-test:latest pytest $PYTEST_ARGS     \
                     || true
```

---

## Running a Shell Inside the Container  

To enter the running container interactively:

```sh
docker exec -it ghini_test /bin/bash
```

Once inside, you can manually run:

```sh
pytest -rs -s
```

---

## Conclusion  

This guide provides a structured workflow for running pytest inside a Docker container using command-line tools.  
By following these steps, you ensure a **fully isolated, consistent** test environment.

### **Final Thoughts**
- ✅ **Minimal host dependencies** → Only Docker & BuildX required.  
- ✅ **No need for PyGObject on the host** → Installed inside Docker.  
- ✅ **Database & GTK dependencies remain in the container**.  

For further improvements, consider:  
- Using **CI/CD Pipelines** to automate tests in GitLab.  
- Implementing **Docker Compose** for better environment management.  

Happy Testing! 🚀  
