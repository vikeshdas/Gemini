import streamlit as st
import requests

UPLOAD_URL = 'http://localhost:8000/upload-pdf/'  
ASK_URL = 'http://localhost:8000/ask-question/' 

def upload_pdf():
    """Function to upload PDFs to Django API"""
    st.header("Upload PDFs")
    
    pdf_files = st.file_uploader("Choose PDF files", type="pdf", accept_multiple_files=True)
    
    if pdf_files:  
        files = [('pdf', (pdf.name, pdf, 'application/pdf')) for pdf in pdf_files]
        
        try:
            response = requests.post(UPLOAD_URL, files=files)
            if response.status_code == 200:
                st.success("PDFs uploaded successfully!")
            else:
                st.error(f"Failed to upload PDFs: {response.json().get('error')}")
        except Exception as e:
            st.error(f"Error uploading PDFs: {str(e)}")


def ask_question():
    """Function to ask a question and get an answer"""
    st.header("Ask a Question")

    question = st.text_input("Ask your question")
    if question:
        try:
            response = requests.get(ASK_URL, params={'question': question})
            if response.status_code == 200:
                answer = response.json()
                st.write("Answer: ", answer['output_text'])
            else:
                st.error(f"Failed to get an answer: {response.json().get('error')}")
        except Exception as e:
            st.error(f"Error asking question: {str(e)}")

def main():
    st.title("PDF Question Answering System")

    tab1, tab2 = st.tabs(["Upload PDF", "Ask Question"])
    
    with tab1:
        upload_pdf()

    with tab2:
        ask_question()

if __name__ == "__main__":
    main()
