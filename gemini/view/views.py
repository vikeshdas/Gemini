from rest_framework.views import APIView
from django.http import JsonResponse, HttpRequest
from langchain.text_splitter import RecursiveCharacterTextSplitter
from ..settings import GOOGLE_API_KEY
from langchain_google_genai import GoogleGenerativeAIEmbeddings
import google.generativeai as genai
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from PyPDF2 import PdfReader
from langchain.vectorstores import FAISS
from langchain.chains.question_answering import load_qa_chain

class Gemini(APIView):

    def post(self, request: HttpRequest):
        try:
            genai.configure(api_key=GOOGLE_API_KEY)

            pdf_docs = request.FILES.getlist('pdf')
            text = ""
            if len(pdf_docs)==0:
                return JsonResponse({"error": "No PDF files uploaded."}, status=400)
            
            for pdf in pdf_docs:
                if pdf.content_type != 'application/pdf':
                    return JsonResponse({"error": "Invalid file"}, status=400)
            
            print("LENTH OF PDF IS: ",len(pdf_docs))
            for pdf in pdf_docs:
                pdf_reader = PdfReader(pdf)
                for page in pdf_reader.pages:
                    text += page.extract_text()

            text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
            text_chunks = text_splitter.split_text(text)

            embeddings = GoogleGenerativeAIEmbeddings(model = "models/embedding-001")
            vector_store = FAISS.from_texts(text_chunks, embedding=embeddings)
            vector_store.save_local("faiss_index")

            return JsonResponse({"message": "Operation successful"}, safe=False)
        
        except Exception as e:

            return JsonResponse({"error": f"Failed to process PDF: {str(e)}"}, status=500)

    def get(self, request: HttpRequest):
        prompt_template = """
        Answer the question as detailed as possible from the provided context, make sure to provide all the details, if the answer is not in
        provided context just say, "answer is not available in the context", don't provide the wrong answer\n\n
        Context:\n {context}?\n
        Question: \n{question}\n

        Answer:
        """
        model = ChatGoogleGenerativeAI(model="gemini-pro",
                             temperature=0.3)
        user_question=request.GET.get("question")
        prompt = PromptTemplate(template = prompt_template, input_variables = ["context", "question"])
        chain = load_qa_chain(model, chain_type="stuff", prompt=prompt)

        embeddings = GoogleGenerativeAIEmbeddings(model = "models/embedding-001")
    
        new_db = FAISS.load_local("faiss_index", embeddings,allow_dangerous_deserialization=True)
        docs = new_db.similarity_search(user_question)

        
        response = chain(
            {"input_documents":docs, "question": user_question}
            , return_only_outputs=True)

        return JsonResponse(response)