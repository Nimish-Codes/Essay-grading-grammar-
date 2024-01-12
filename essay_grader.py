import streamlit as st
from transformers import BertTokenizer, BertForSequenceClassification
import torch
import requests.exceptions
import language_tool_python
from nltk.tokenize import sent_tokenize

def initialize_language_tool():
    try:
        return language_tool_python.LanguageTool('en-US')
    except requests.exceptions.RequestException as e:
        print(f"Error initializing LanguageTool: {e}")
        return None

def initialize_bert_model():
    try:
        model_name = "bert-base-uncased"
        tokenizer = BertTokenizer.from_pretrained(model_name)
        model = BertForSequenceClassification.from_pretrained(model_name)
        return tokenizer, model
    except requests.exceptions.RequestException as e:
        print(f"Error initializing BERT model: {e}")
        return None, None

tool = initialize_language_tool()
bert_tokenizer, bert_model = initialize_bert_model()

def tokenize_text(text):
    return sent_tokenize(text)

def process_and_grade_essay(essay):
    # Step 1: Tokenize the essay
    sentences = tokenize_text(essay)

    # Step 2: Extract faults, grammar mistakes, and suggestions
    faults = []

    if tool:
        grammar_mistakes = tool.check(essay)
        corrected_essay = tool.correct(essay)

        # Provide more detailed feedback for each grammar mistake
        detailed_feedback = []
        for match in grammar_mistakes:
            detailed_feedback.append(f"Error: {match.message}")

        # Include detailed feedback in the result
        result = {
            'grammar_mistakes': grammar_mistakes,
            'detailed_feedback': detailed_feedback,
            'corrected_essay': corrected_essay
        }
    else:
        result = {
            'grammar_mistakes': [],
            'detailed_feedback': ["Error initializing LanguageTool. Please check your internet connection."],
            'corrected_essay': essay
        }

    # Step 3: Use BERT model for essay grading
    if bert_tokenizer and bert_model:
        # Tokenize and encode the essay for BERT
        inputs = bert_tokenizer(essay, return_tensors="pt", truncation=True)
        # Perform classification using the BERT model
        outputs = bert_model(**inputs)
        # Get the predicted class (binary classification)
        predicted_class = torch.argmax(outputs.logits, dim=1).item()

        # Provide feedback based on predicted class
        if predicted_class == 0:
            faults.append("The essay is classified as negative.")
        else:
            faults.append("The essay is classified as positive.")

        # Include BERT feedback in the result
        result['bert_feedback'] = faults
    else:
        result['bert_feedback'] = ["Error initializing BERT model. Please check your internet connection."]

    # Step 4: Provide overall feedback
    has_title = any(sent.lower().startswith('title') for sent in sentences)
    has_introduction = any(sent.lower().startswith('introduction') for sent in sentences)
    has_body = any(sent.lower().startswith('body') for sent in sentences)
    has_conclusion = any(sent.lower().startswith('conclusion') for sent in sentences)

    if not has_title:
        faults.append("The essay lacks a title.")

    if not has_introduction:
        faults.append("The essay lacks an introduction.")

    if not has_body:
        faults.append("The essay lacks a body section.")

    if not has_conclusion:
        faults.append("The essay lacks a conclusion.")

    feedback = "Overall, your essay could benefit from the following improvements:\n"
    feedback += "\n".join(faults)

    # Include overall feedback in the result
    result['feedback'] = feedback

    # Step 5: Return the result
    return result

# Streamlit app
def main():
    st.title("Essay Grading App")

    # User input for the essay
    user_essay = st.text_area("Enter your essay:")

    # Process and grade the essay when the user clicks a button
    if st.button("Process and Grade"):
        result = process_and_grade_essay(user_essay)

        # Display results in the app
        st.subheader("Grammar Mistakes:")
        st.write(result['grammar_mistakes'])

        st.subheader("Detailed Feedback:")
        st.write(result['detailed_feedback'])

        st.subheader("Feedback:")
        st.write(result['feedback'])

        st.subheader("Corrected Essay:")
        st.write(result['corrected_essay'])

        st.subheader("BERT Feedback:")
        st.write(result['bert_feedback'])

# Run the Streamlit app
if __name__ == "__main__":
    main()
