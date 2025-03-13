# Running Pytest in a Docker Container from the Command Line

## Introduction  

This guide provides detailed instructions on how to build and run pytest tests inside a Docker container from the command line. This ensures a reproducible and isolated testing environment.

---

## Prerequisites  

Before running the tests, ensure you have the following installed on your system:

### **1. Install Docker**  
- **Ubuntu/Debian**:  
  ```sh
  sudo apt update
  sudo apt install -y docker.io
  sudo systemctl enable --now docker
  ```
- **Arch Linux**:  
  ```sh
  sudo pacman -S docker
  sudo systemctl enable --now docker
  ```
- **macOS**:  
  - Install [Docker Desktop](https://www.docker.com/products/docker-desktop)  
- **Windows**:  
  - Install [Docker Desktop](https://www.docker.com/products/docker-desktop)  
  - Ensure **WSL 2** is enabled and running.  

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
docker buildx build --no-cache --ssh default --progress=plain     --build-arg COMMIT=$(git rev-parse HEAD)     --build-arg BUILD_DATE=$(date -u +'%Y-%m-%dT%H:%M:%SZ')     --build-arg USER_ID=$(id -u)     --build-arg GROUP_ID=$(id -g)     --load -f Dockerfile.test -t ghini-desktop-test:latest .
```

---

## Running the Tests  

Once the image is built, run the container with the following command:

```sh
docker run --rm -it     -p 5678:5678     -e DEBUG=false     -e USER=ghini     -e DISPLAY=$DISPLAY     -e DB_HOST=postgres.wysechoice.net     -e DB_PORT=5432     -e DB_NAME=ghini_test3     -e DB_USER=ghini     -e DB_SSLMODE=prefer     -e KRB5_CONFIG=/krb5/krb5.conf     -e KRB5_CLIENT_KTNAME=/krb5/krb5.keytab     -e NO_AT_BRIDGE=1     -v /tmp/.X11-unix:/tmp/.X11-unix     -v $HOME/krb5:/krb5:ro     -v $HOME/.bauble/3.1:/home/ghini/.bauble/3.1     -v $HOME/debug/ghini.desktop:/app     -v /usr/lib/dri:/usr/lib/dri     --device /dev/dri:/dev/dri     --user $(id -u):$(id -g)     --name ghini_test     ghini-desktop-test:latest pytest && true
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

## Automating the Process  

To simplify test execution, create a shell script (`run_tests.sh`):

```sh
#!/bin/bash
echo "Building Docker test image..."
docker buildx build --no-cache --ssh default --progress=plain     --build-arg COMMIT=$(git rev-parse HEAD)     --build-arg BUILD_DATE=$(date -u +'%Y-%m-%dT%H:%M:%SZ')     --build-arg USER_ID=$(id -u)     --build-arg GROUP_ID=$(id -g)     --load -f Dockerfile.test -t ghini-desktop-test:latest .

echo "Running tests..."
docker run --rm -it -p 5678:5678 -e DEBUG=false     -e USER=ghini -e DISPLAY=$DISPLAY     -e DB_HOST=postgres.wysechoice.net -e DB_PORT=5432     -e DB_NAME=ghini_test3 -e DB_USER=ghini -e DB_SSLMODE=prefer     -e KRB5_CONFIG=/krb5/krb5.conf -e KRB5_CLIENT_KTNAME=/krb5/krb5.keytab     -e NO_AT_BRIDGE=1 -v /tmp/.X11-unix:/tmp/.X11-unix     -v $HOME/krb5:/krb5:ro -v $HOME/debug/ghini.desktop:/app     --device /dev/dri:/dev/dri --user $(id -u):$(id -g)     --name ghini_test ghini-desktop-test:latest pytest && true
```

Make it executable and run:

```sh
chmod +x run_tests.sh
./run_tests.sh
```

---

## Conclusion  

This guide provides a structured workflow for running pytest inside a Docker container using command-line tools. By following these steps, you ensure a consistent test environment that is easy to set up and debug.

For further improvements, consider:  
- Using **CI/CD Pipelines** to automate tests in GitLab.  
- Implementing **Docker Compose** for better environment management.  

Happy Testing! 🚀  
