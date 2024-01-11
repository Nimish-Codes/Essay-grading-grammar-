import streamlit as st
from sentence_transformers import SentenceTransformer, util
import language_tool_python
import requests.exceptions

def initialize_language_tool():
    try:
        return language_tool_python.LanguageTool('en-US')
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Error initializing LanguageTool: {e}")

# Load Sentence Transformer model
model = SentenceTransformer('paraphrase-distilroberta-base')

tool = initialize_language_tool()

def process_and_grade_essay(essay):
    # Step 1: Extract faults, grammar mistakes, and suggestions
    faults = []

    if tool:
        grammar_mistakes = tool.check(essay)
        corrected_essay = tool.correct(essay)

        # Provide more detailed feedback for each grammar mistake
        detailed_feedback = []
        for match in grammar_mistakes:
            # Use match.fromy and match.fromycol for line and column numbers
            detailed_feedback.append(f"Error at line {match.fromy}, column {match.fromycol}: {match.message}")

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

    # Step 2: Provide overall feedback using Sentence Transformer
    embeddings = model.encode([essay])
    reference_embedding = model.encode(["A well-structured and coherent essay."])
    similarity = util.pytorch_cos_sim(embeddings, reference_embedding)[0][0].item()

    feedback = "Overall, your essay could benefit from the following improvements:\n"
    feedback += f"Similarity to a well-structured essay: {similarity:.2%}"

    # Include overall feedback in the result
    result['feedback'] = feedback

    # Return the result
    return result

# Streamlit UI
st.title("Advanced Essay Processing and Grading App")
st.warning("This app finds, corrects word errors, and provides additional features to enhance your essay.")

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

    # Additional Features
    st.subheader("Additional Features:")

    # Word Counter
    word_count = len(user_essay.split())
    st.write(f"Word Count: {word_count}")

    # Plagiarism Detection (Simple example with a predefined phrase)
    predefined_phrase = "This is a sample phrase for plagiarism detection."
    plagiarism_detected = predefined_phrase.lower() in user_essay.lower()
    st.write(f"Plagiarism Detected: {plagiarism_detected}")

    # Language Selection
    selected_language = st.selectbox("Select Language:", ["English", "Spanish", "French"])
    st.write(f"Selected Language: {selected_language}")

    # Summary Generator
    summary = " ".join(user_essay.split()[:30])  # Extract the first 30 words as a summary
    st.subheader("Summary:")
    st.write(summary)
