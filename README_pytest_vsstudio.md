# Running Pytest in a Dockerized Environment with VS Studio  

## Introduction  

This guide provides detailed instructions on how to set up, build, and run pytest tests using Docker and VS Studio inside the `ghini-desktop` repository. This setup ensures a reproducible and consistent test environment across different systems.

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

### **2. Install Visual Studio Code (VS Studio)**  
- Download and install [VS Studio](https://code.visualstudio.com/Download).  

### **3. Install Required VS Studio Extensions**  
- Open VS Studio and install the following extensions:  
  1. **Docker** (by Microsoft)  
  2. **Python** (by Microsoft)  
  3. **Dev Containers** (optional, for an integrated Docker dev environment)  

---

## Repository Structure  

After cloning the repository, your directory should look like this:  

```
ghini-desktop/
├── bauble/
│   ├── images/
│   ├── plugins/
│   │   ├── abcd/
│   │   ├── garden/
│   │   ├── imex/
│   │   ├── plants/
│   │   │   └── default/
│   │   ├── report/
│   │   │   ├── jinja2/
│   │   │   ├── mako/
│   │   │   ├── templates/
│   │   │   └── xsl/
│   │   │       └── label_example/
│   │   ├── tag/
│   │   └── users/
│   ├── test/
│   └── utils/
├── data/
├── debian/
├── doc/
│   ├── images/
│   │   ├── icons/
│   │   ├── schemas/
│   │   └── screenshots/
│   ├── _static/
│   └── _templates/
├── misc/
├── nsis/
│   ├── Include/
│   └── Plugins/
│       ├── amd64-unicode/
│       ├── x86-ansi/
│       └── x86-unicode/
├── packages/
│   ├── bauble-installer_1.0-1/
│   │   ├── DEBIAN/
│   │   └── usr/
│   │       └── bin/
│   ├── jaunty/
│   ├── karmic/
│   ├── lucid/
│   ├── maverick/
│   │   └── source/
│   ├── natty/
│   │   └── source/
│   └── oneiric/
│       └── source/
├── po/
└── scripts/
```

> **Mounted Volumes:**  
> - `/home/chris/debug/tmp/ghini-desktop` (local) → `/app` (inside Docker)  
> - Modifications to local files reflect inside the container automatically.

---

## Running the Tests in VS Studio  

Follow these steps to build the Docker image and run the tests:  

### **1. Open the Repository in VS Studio**  
- Open VS Studio.  
- Click **"File" > "Open Folder"** and select the `ghini-desktop` directory.  

### **2. Build the Docker Test Image**  
- Press `Ctrl+Shift+P` to open the **Command Palette**.  
- Type **"Tasks: Run Task"** and select it.  
- From the list, select **"Build Docker Test Image"**.  
- Wait for the build process to complete. The output will be displayed in the **Terminal**.  

### **3. Run the Tests**  
- Click on the **"Run and Debug"** button in the left sidebar (or press `Ctrl+Shift+D`).  
- In the dropdown at the top, select **"Python: Attach to Test Container (ghini.desktop)"**.  
- Click the green **"Start Debugging"** button (or press `F5`).  
- The **DEBUG CONSOLE** will display the test output.  

> **Note:** This setup attaches to a running Docker container and executes pytest with debugpy for interactive debugging.

---

## Modifying Test Parameters  

### **Changing Pytest Arguments**  
The pytest arguments are defined in `tasks.json` under the `PYTEST_ARGS` environment variable. To modify test behavior:  

1. Open `.vscode/tasks.json`.  
2. Locate the `PYTEST_ARGS` section:  

    ```json
    {
        "label": "Run Pytest",
        "type": "shell",
        "command": "docker exec ghini_test pytest -rs -s $PYTEST_ARGS",
        "problemMatcher": []
    }
    ```
3. Change `$PYTEST_ARGS` to your desired parameters, e.g.,  
    ```json
    "command": "docker exec ghini_test pytest -rs -s --maxfail=3 --disable-warnings"
    ```

### **Common Pytest Arguments**  
- `-s` → Show print output in console  
- `-rs` → Show summary of test skips, fails, and xfails  
- `--maxfail=3` → Stop after 3 failures  
- `--disable-warnings` → Suppress warnings  

---

## Troubleshooting  

| Issue | Solution |
|-------|---------|
| `docker: command not found` | Ensure Docker is installed and added to `PATH`. |
| `Permission denied while accessing Docker` | Run `sudo usermod -aG docker $USER` and restart your system. |
| `pytest not found in container` | Ensure pytest is installed inside Docker: `pip install pytest`. |
| Debugger not attaching | Ensure port `5678` is exposed in Docker and the container is running. |

---

## Conclusion  

This guide provides a structured workflow for running pytest inside a Docker container using VS Studio. By following these steps, you ensure a consistent test environment that is easy to set up and debug.  

For further improvements, consider:  
- Using **VS Studio Dev Containers** for seamless integration.  
- Automating test runs with GitHub Actions or CI/CD pipelines.  

Happy Testing! 🚀  
