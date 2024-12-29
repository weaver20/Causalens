# Causal DAG Summarization Tool

**Causal DAG Summarization Tool** is a Python-based application designed to simplify and summarize complex causal Directed Acyclic Graphs (DAGs). It helps researchers and data scientists working in causal inference, particularly with high-dimensional data, by providing a streamlined interface to transform complex DAGs into more interpretable summarized graphs.

This tool integrates:
- A Streamlit-based UI for user interaction.
- NetworkX and PyVis for graph manipulation and visualization.
- Support for uploading `.dot` files representing causal DAGs.
- Configurable parameters for summarization.
- Placeholder logic for causal effect computation, ready to be integrated with your backend algorithms.

---

## Key Features

- **Upload or Generate Causal DAGs:**  
  Upload your `.dot` file (representing a causal DAG) or generate a placeholder DAG if none is provided.

- **Parameter Configuration:**  
  Set a size constraint and a semantic similarity threshold to control the graph summarization process.

- **Summarized Graph Visualization:**  
  View the original and summarized DAG side-by-side interactively in your browser using PyVis and NetworkX.

- **Graph Editing:**  
  Add or remove edges from the summarized graph using simple UI controls. The visualization updates in real-time.

- **Causal Effect Computation (Placeholder):**  
  Select two nodes and choose whether to compute causal effects on the original or summarized DAG. Currently a mock feature, it can be integrated with real causal inference methods.

---

## Installation

**Tested Environment:**  
- Python 3.11.5

### Prerequisites

1. **Python:**  
   Install Python 3.11.5 from [Python.org](https://www.python.org/downloads/).

2. **Graphviz:**  
   Install Graphviz from [Graphviz Downloads](https://graphviz.org/download/).  
   During installation, select the option to add Graphviz to your PATH.  
   Verify by running:
   ```bash
   dot -V
If it prints a version, Graphviz is correctly installed.

Microsoft Visual C++ Build Tools (Windows only):
If using Windows and installing pygraphviz directly via pip:
Install Microsoft C++ Build Tools.
In the installer, select the "Desktop development with C++" workload.
After installation, open the Developer Command Prompt for VS and run:
bash
Copy code
where cl.exe
If cl.exe is found, your environment is set.
If difficulties persist, consider:
bash
Copy code
pip install pipwin
pipwin install pygraphviz
or
bash
Copy code
conda install -c conda-forge pygraphviz
Steps to Install
Clone the Repository:

bash
Copy code
git clone https://github.com/<your-username>/causal-dag-summarization.git
cd causal-dag-summarization
Create and Activate a Virtual Environment:

bash
Copy code
python -m venv venv
source venv/bin/activate
On Windows:

bash
Copy code
venv\Scripts\activate
Install Dependencies:

bash
Copy code
pip install -r requirements.txt
If pygraphviz fails, ensure Graphviz is on PATH, or use pipwin or conda as described above.

Usage
Run the Application:

bash
Copy code
streamlit run app.py
Open the URL provided by Streamlit (usually http://localhost:8501) in your browser.

Upload or Generate a DAG: In the sidebar, upload a .dot file describing your causal DAG.
If no .dot file is available, click "Generate DAG" to load a placeholder.

Set Parameters and Summarize: Adjust the size constraint and semantic similarity threshold in the sidebar, then click "Summarize Data" to produce a summarized DAG.

Edit Summarized Graph: Use the sidebar to specify edges to add or remove from the summarized DAG. The graph visualization updates immediately.

Compute Causal Effects: Select two nodes and choose whether to compute causal effects on the original or summarized graph. Currently returns a placeholder value; integrate your causal inference logic here.

Project Structure
Copy code
causal-dag-summarization/
  app.py
  graph_utils.py
  summarization.py
  visualization.py
  requirements.txt
  .gitignore
  README.md
app.py: Main Streamlit app logic and UI.
graph_utils.py: Functions to load .dot files and generate placeholder DAGs.
summarization.py: Placeholder DAG summarization logic.
visualization.py: PyVis-based graph visualization functions.
requirements.txt: Python dependencies.
.gitignore: Ignored files and directories.
README.md: This documentation.
Troubleshooting
PyGraphviz Installation Errors on Windows:
Confirm Graphviz is installed and on PATH.
Ensure cl.exe is available by installing the "Desktop development with C++" workload.
If issues persist, use pipwin or conda as described above.

Causal Effect Computation:
The implementation is a placeholder. Integrate your causal inference backend to produce real computations.

Contributing
Contributions are welcome!

Fork the repository, create a new branch for your changes.
Submit a pull request.
Ensure your code is documented and tested.
License
This project is licensed under the MIT License.

Contact
For questions, support, or collaboration, please open a GitHub issue in this repository.