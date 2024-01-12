import streamlit as st
from nbconvert import PythonExporter
import nbformat

# Define a function to run and display a Jupyter Notebook
def run_and_display_notebook(notebook_path):
    with open(notebook_path, 'r', encoding='utf-8') as notebook_file:
        notebook_content = notebook_file.read()

    notebook = nbformat.reads(notebook_content, as_version=4)
    exporter = PythonExporter()
    python_code, _ = exporter.from_notebook_node(notebook)

    # Run the notebook code
    exec(python_code)

# Run and display the Jupyter Notebook
notebook_path = 'essay grader.ipynb'
run_and_display_notebook(notebook_path)
