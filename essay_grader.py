import streamlit as st
import spacy
import requests
import language_tool_python

# Download spaCy model if not already installed
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    st.info("Downloading spaCy model. This may take some time.")
    from spacy.cli import download
    download("en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")

# Function to initialize LanguageTool
def initialize_language_tool():
    try:
        return language_tool_python.LanguageTool('https://languagetool.org/api/v2')
    except Exception as e:
        print(f"Error initializing LanguageTool: {e}")
        return None

# Function to process and grade essay
def process_and_grade_essay(nlp, tool, essay):
    # Check for the presence of introduction, body, and conclusion sections
    has_introduction = any(sent.text.lower().startswith('introduction') for sent in nlp(essay).sents)
    has_body = any(sent.text.lower().startswith('body') for sent in nlp(essay).sents)
    has_conclusion = any(sent.text.lower().startswith('conclusion') for sent in nlp(essay).sents)

    faults = []

    if not has_introduction:
        faults.append("The essay lacks an introduction.")

    if not has_body:
        faults.append("The essay lacks a body section.")

    if not has_conclusion:
        faults.append("The essay lacks a conclusion.")

    # Use LanguageTool API for grammar checking
    language_tool_url = "https://languagetool.org/api/v2/check"
    data = {"text": essay}
    response = requests.post(language_tool_url, data=data)
    grammar_mistakes = response.json()

    # Display results
    st.subheader("Grammar Mistakes:")
    st.write(grammar_mistakes)

    st.subheader("Structure and Content Feedback:")
    st.write(faults)

# Streamlit app
st.title("Essay Grader")

# User input for the essay
user_essay = st.text_area("Enter your essay here:")

# Process and grade the essay when a button is clicked
if st.button("Grade Essay"):
    tool = initialize_language_tool()

    if tool:
        process_and_grade_essay(nlp, tool, user_essay)
    else:
        st.warning("Error initializing LanguageTool. Please check your internet connection.")
