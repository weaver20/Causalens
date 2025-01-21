

<h1 align="center" style="font-weight: bold;">CaGreS - Causal DAG Summarization 💻</h1>

<p align="center">
<a href="#tech">Technologies</a>
<a href="#started">Getting Started</a>

 
</p>


<p align="center">CaGreS (Causal Graph Reduction and Summarization) is a demo tool designed to demonstrate how large causal DAGs (Directed Acyclic Graphs) can be summarized into smaller graphs while preserving core causal structure. This approach helps users work with high-dimensional DAGs more effectively and conduct causal inference without being overwhelmed by too many nodes or edges.

Key Features

- <b>Interactive UI:</b> Built with Streamlit, offering an intuitive interface for uploading or generating DAGs.
- <b>Configurable Summarization:</b> Size Constraint: Limit the number of nodes in the resulting summary DAG.
- <b>Semantic Threshold:</b> Cluster nodes only if they have sufficient semantic similarity.
- <b>Graph Editing:</b> Add or remove edges on the original DAG—ideal for correcting minor errors or exploring hypothetical changes.
- <b>Causal Inference:</b> Compute Average Treatment Effects (ATE) and other causal measures on both the original and summarized DAG for comparison.
- <b>Robustness:</b> Summaries remain informative even if the input DAG has missing or redundant edges.</p>


<p align="center">
<a href="https://github.com/weaver20/CasualDAG_Sum">📱 Visit this Project</a>
</p>


<h2 id="technologies">💻 Technologies</h2>

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![NetworkX](https://img.shields.io/badge/NetworkX-1f5a3f.svg?style=for-the-badge)
![PyVis](https://img.shields.io/badge/PyVis-3776AB.svg?style=for-the-badge)
![DoWhy](https://img.shields.io/badge/DoWhy-FF2A17E.svg?style=for-the-badge)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)

These libraries and frameworks together power the CaGreS demo tool, ensuring a seamless experience from data import to summarization and causal inference.

<h2 id="started">🚀 Getting started</h2>

Choose your platform of installation:
- [Windows](#windows) ![Windows](https://img.icons8.com/fluency/28/windows-11.png)
- [Linux](#linux) ![Linux](https://img.icons8.com/color/28/linux--v1.png)
- [macOS](#macos) ![Apple](https://img.icons8.com/office/28/mac-os.png)
- [Docker](#docker) ![Docker](https://img.icons8.com/fluency/28/docker.png)

<h3>Prerequisites</h3>

- **Git 2+**: Ensure you have Git installed and configured.
- **Python 3.11**: Required for the Streamlit app and data manipulations (above versions of Python were not tested).
- **C/C++ Compiler** (on Windows, you typically need the [Build Tools for Visual Studio](https://visualstudio.microsoft.com/downloads/#build-tools-for-visual-studio) or a full Visual Studio installation) if you plan to install `pygraphviz` via pip (it compiles native code).
- **Docker** *(optional)*: If you prefer running the tool in a container (recommended for Windows users).

<h3>Cloning</h3>

```bash
git clone https://github.com/weaver20/CasualDAG_Sum.git
cd /CasualDAG_Sum
```
This downloads the code and moves you into the project directory.

<h3>Starting</h3>

### Windows
1. **Open Windows `PowerShell`**.
   
2. **Create a virtual environment** (named `venv` for example):
   ```bash
   python -m venv venv
   ```
   
3. **Activate** the virtual environment:
   ```bash
   venv\Scripts\activate
   ```
   
4. **Installing System-Level Graphviz:** you must install the system-level Graphviz **with development headers.**
    * **Download the Graphviz installer for Windows**  [from the official Graphviz website.](https://graphviz.org/)
    * **Run the installer** and select a **Complete** or **Custom** installation that includes the **C headers** (development libraries).
    * By default, it installs to something like: `C:\Program Files\Graphviz`, Inside this folder, you should see:
        * `bin\` (contains `dot.exe`, etc.)
        * `include\graphviz` (should contain `cgraph.h`)
        * `lib\` or `lib64\` (contains `.lib` files for linking)
    * **Add Graphviz** `bin` folder to **PATH** (ensure to restart the `PowerShell` terminal afterwards).
      
5. **Once **Graphviz (with headers)** is installed and on your system, you can install PyGraphviz:**
   ```bash
   pip install pygraphviz
   ```
   * If that fails with an error like `graphviz/cgraph.h: No such file or directory`, it means the compiler can’t find the headers. Try the following:
   
   * Add Graphviz’s `include` and `lib` folders to your environment variables so MSVC can see them:
      ```powershell
      $Env:INCLUDE = "C:\Program Files\Graphviz\include;$Env:INCLUDE"
      $Env:LIB = "C:\Program Files\Graphviz\lib;$Env:LIB"
      ```
   * **Re-install** with no cache (to force a rebuild):
      ```bash
      pip install --no-cache-dir --force-reinstall pygraphviz
      ```
   * If it still can’t find the headers, you can specify them directly:
      ```bash
      pip install --no-cache-dir pygraphviz \
       --global-option=build_ext \
       --global-option="-IC:\Program Files\Graphviz\include" \
       --global-option="-LC:\Program Files\Graphviz\lib"
      ```
   * If installation succeeds, open a `Python` shell and execute:
      ```python
      import pygraphviz
      print(pygraphviz.__version__)
      ```
   Check the output, if there are no errors it means `pygraphviz` has been successfully installed and is now usable.

6. **Check Python version, then install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
   
7. **Start the streamlit app:**
   ```bash
   python -m streamlit run app.py --server.port 8081 --server.address localhost
   ```

### Linux 
1. **Open a terminal and install Python if needed:**
   ```bash
   sudo apt-get install python3-pip
   ```
2. **Install Graphviz and Dev Headers:**
   * **Dbian/Ubuntu:**
      ```bash
      sudo apt-get update
      sudo apt-get install build-essential graphviz libgraphviz-dev pkg-config
      ```
   * **Fedora/CentOS/RHEL:**
       ```bash
      sudo dnf install graphviz graphviz-devel
      ```
      This ensures both the runtime `(dot, etc.)` and the development headers (like `cgraph.h`).
3. **Install PyGraphviz:**
   ```bash
   pip install pygraphviz
   ```
   * If it still can’t find headers, you may need to manually specify:
     ```bash
     pip install pygraphviz --no-cache-dir \
     --global-option=build_ext \
     --global-option="-I/usr/include/graphviz" \
     --global-option="-L/usr/lib"
     ```
     Adjust paths for your distro if needed.
     
3. **Install PyVis:**
   ```bash
    pip install pyvis
   ```
4. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
5. **Start the streamlit app:**
   ```bash
   python -m streamlit run app.py --server.port 8081 --server.address localhost
   ```

### macOS
1. **Install Homebrew** (if you don’t have it yet):
   ```bash
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```
2. **Install Graphhviz:**
   ```bash
   brew install graphviz
   ```
   This includes the development headers by default.
   
4. **Install PyGraphviz** (if needed):
   ```bash
   pip install pygraphviz
   ```
   * If you encounter missing header errors, ensure you have `Xcode Command Line Tools` installed:
      ```bash
      xcode-select --install
      ```
   * Sometimes specifying include/lib paths is required:
      ```bash
      pip install pygraphviz --no-cache-dir \
       --global-option=build_ext \
       --global-option="-I/usr/local/include/graphviz" \
       --global-option="-L/usr/local/lib"
      ```
      (Adjust paths if `brew` installed Graphviz elsewhere—often under `/opt/homebrew` on Apple Silicon or `/usr/local` on Intel.)
     
5. **Install PyVis:**
   ```bash
   pip install pyvis
   ```
   
6. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
   
7. **Start the streamlit app:**
   ```bash
   python -m streamlit run app.py --server.port 8081 --server.address localhost
   ```

### Docker
1. Build the Docker image:
   ```bash
   docker build -t your-image-name .
   ```
   
2. Run the container:
   ```bash
   docker run -p 8501:8501 your-image-name
   ```
   
3. Access it through the browser at `http://localhost:8501` or at `http://0.0.0.0:8501`.

* The `Dockerfile` is configured to expose `PORT 8501` as an input to the container in order to communicate with the Streamlit application, but feel free to change it according to your desire.
* Running the app on a container prevents changes to reflect instantly (in case you test any changes within the source code on your local repository). In case you would like to test changes you will be required to re-build the `Docker` image and re-run the `Docker` container.

<h2 id="contribute">📫 Contribute</h2>

Contributions are **highly appreciated**! If you’d like to help:

1. **Fork** this repository and create a new branch for your feature or bug fix.
2. **Make** your changes, ensuring they align with our coding style and add relevant tests if possible.
3. **Commit** your code with clear messages.
4. **Open** a pull request describing the changes you’ve made and their motivation.

For major changes or big new features, feel free to **open an Issue** first to discuss your idea and gather feedback from maintainers and the community. We look forward to collaborating with you!


<h3>Documentations that might help</h3>

[📝 How to create a Pull Request](https://www.atlassian.com/br/git/tutorials/making-a-pull-request)

[💾 Commit pattern](https://gist.github.com/joshbuchea/6f47e86d2510bce28f8e7f42ae84c716)
