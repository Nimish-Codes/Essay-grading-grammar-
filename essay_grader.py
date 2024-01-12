import streamlit as st
import spacy
import language_tool_python
import requests.exceptions

pip install language-tool-python

# Function to initialize LanguageTool
def initialize_language_tool():
    try:
        return language_tool_python.LanguageTool('en-US')
    except requests.exceptions.RequestException as e:
        print(f"Error initializing LanguageTool: {e}")
        return None

# Load spacy model and add the 'sentencizer' component
nlp = spacy.load("en_core_web_sm")
sentencizer = nlp.add_pipe('sentencizer')

tool = initialize_language_tool()

# Function to process and grade essay
def process_and_grade_essay(essay):
    # Processing steps as in your original code...
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
    has_introduction = any(sent.text.lower().startswith('introduction') for sent in doc.sents)
    has_body = any(sent.text.lower().startswith('body') for sent in doc.sents)
    has_conclusion = any(sent.text.lower().startswith('conclusion') for sent in doc.sents)

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

    # Return the result
    return result

# Streamlit app
st.title("Essay Grader")

# User input for the essay
user_essay = st.text_area("Enter your essay here:")

# Process and grade the essay when a button is clicked
if st.button("Grade Essay"):
    result = process_and_grade_essay(user_essay)

    # Display results on the app
    st.subheader("Grammar Mistakes:")
    st.write(result['grammar_mistakes'])

    st.subheader("Detailed Feedback:")
    st.write(result['detailed_feedback'])

    st.subheader("Feedback:")
    st.write(result['feedback'])

    st.subheader("Corrected Essay:")
    st.write(result['corrected_essay'])
