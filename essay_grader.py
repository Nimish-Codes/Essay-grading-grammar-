import streamlit as st
from streamlit_analytics import with_databricks

# Create a Streamlit app
app = st.empty()

# Define a function to run the notebook
@st.cache(allow_output_mutation=True)
def run_notebook(path):
    with open(path, 'r') as notebook:
        code = notebook.read()
    return with_databricks(code)

# Run the notebook
path = 'essay grader.ipynb'
result = run_notebook(path)

# Display the result in the Streamlit app
app.pydeck_chart(result)

