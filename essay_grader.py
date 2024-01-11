import streamlit as st
import spacy
import language_tool_python
import requests.exceptions

def download_spacy_model(model_name):
    try:
        from spacy.cli import download
        download(model_name)
    except Exception as e:
        raise RuntimeError(f"Error downloading spaCy model: {e}")

def download_spacy_model(model_name):
    try:
        from spacy.cli import download
        download(model_name)
    except Exception as e:
        st.error(f"Error downloading spaCy model: {e}")
        # st.stop()

# Download spaCy model if not already downloaded
download_spacy_model("en_core_web_sm")

# Initialize LanguageTool
def initialize_language_tool():
    try:
        return language_tool_python.LanguageTool('en-US')
    except requests.exceptions.RequestException as e:
        st.error(f"Error initializing LanguageTool: {e}")
        return None

# Load spaCy model and add the 'sentencizer' component
nlp = spacy.load("en_core_web_sm")
sentencizer = nlp.add_pipe('sentencizer')

tool = initialize_language_tool()

def process_and_grade_essay(essay):
    # Step 1: Process the essay using spaCy
    doc = nlp(essay)

    # Step 2: Extract faults, grammar mistakes, and suggestions
    faults = []

    if tool:
        grammar_mistakes = tool.check(essay)
        corrected_essay = tool.correct(essay)

        # Provide more detailed feedback for each grammar mistake
        detailed_feedback = []
        for match in grammar_mistakes:
            if hasattr(match, 'fromx') and hasattr(match, 'tox'):
                # Use match.fromx and match.tox for character indices
                detailed_feedback.append(f"Error from character {match.fromx} to {match.tox}: {match.message}")
            elif hasattr(match, 'fromy') and hasattr(match, 'toy'):
                # Use match.fromy and match.toy for line and column numbers
                detailed_feedback.append(f"Error at line {match.fromy}, column {match.fromycol}: {match.message}")
            else:
                detailed_feedback.append(f"Error: {match.message}")

        # Include detailed feedback in the result
        result = {
            'grammar_mistakes': grammar_mistakes,
            'detailed_feedback': detailed_feedback,
            'corrected_essay': corrected_essay
        }
    else:
        # Provide a default feedback if LanguageTool initialization fails
        result = {
            'grammar_mistakes': [],
            'detailed_feedback': ["Error initializing LanguageTool. Please check your internet connection."],
            'corrected_essay': essay
        }

    # Step 3: Provide feedback on essay structure and content
    has_title = any(sent.text.lower().startswith('title') for sent in doc.sents)
    has_introduction = any(sent.text.lower().startswith('introduction') for sent in doc.sents)
    has_body = any(sent.text.lower().startswith('body') for sent in doc.sents)
    has_conclusion = any(sent.text.lower().startswith('conclusion') for sent in doc.sents)

    if not has_title:
        faults.append("The essay lacks a title.")
      
    if not has_introduction:
        faults.append("The essay lacks an introduction.")

    if not has_body:
        faults.append("The essay lacks a body section.")

    if not has_conclusion:
        faults.append("The essay lacks a conclusion.")

    # Step 4: Provide overall feedback
    feedback = "Overall, your essay could benefit from the following improvements:\n"
    feedback += "\n".join(faults)

    # Include overall feedback in the result
    result['feedback'] = feedback

    # Step 5: Return the result
    return result

# Streamlit UI
st.title("Essay Processing and Grading App")
st.warning(f"This app finds, corrects word errors \n\n Write your essay with title, introduction, body and conclusion like, title: your text and do same for introduction: body: and conclusion: \n For example \n title: This is title \n\n introduction: This \n is \n introduction \n\n body: this \n is\n body \n\n conclusion: this\n is\n conclusion")

# Input textarea for the user to enter their essay
user_essay = st.text_area("Enter your essay here:", value='', height=400)

# Button to trigger essay processing and grading
if st.button("Process and Grade Essay"):
    # Process and grade the essay
    result = process_and_grade_essay(user_essay)

    # Display results
    st.subheader("Grammar Mistakes:")
    st.write(result['grammar_mistakes'])

    st.subheader("Detailed Feedback:")
    st.write(result['detailed_feedback'])

    st.subheader("Feedback:")
    st.write(result['feedback'])

    st.subheader("Corrected Essay:")
    st.write(result['corrected_essay'])
