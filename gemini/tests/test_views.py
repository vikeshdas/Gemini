import os
from django.test import TestCase, Client
from django.urls import reverse

class GeminiViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.upload_url = reverse('upload-pdf')  # Match the path name
        self.ask_question_url = reverse('ask-question') 
        self.test_files_dir = os.path.join(os.path.dirname(__file__), 'test_files')

    def test_upload_single_pdf(self):
        pdf_paths = [
            os.path.join(self.test_files_dir, 'CNN.pdf')
        ]
        
        files = {'pdf': [open(pdf_path, 'rb') for pdf_path in pdf_paths]}

        response = self.client.post(self.upload_url, files, format='multipart')

        self.assertEqual(response.status_code, 200)
        self.assertIn("Operation successful", response.content.decode())
    
    def test_upload_multiple_pdf(self):
        pdf_paths = [
            os.path.join(self.test_files_dir, 'CNN.pdf'),
            os.path.join(self.test_files_dir, 'Google_Cloud_Platform.pdf'),
        ]
        
        files = {'pdf': [open(pdf_path, 'rb') for pdf_path in pdf_paths]}

        response = self.client.post(self.upload_url, files, format='multipart')

        self.assertEqual(response.status_code, 200)
        self.assertIn("Operation successful", response.content.decode())
    
    def test_upload_no_pdfs(self):
        response = self.client.post(self.upload_url, {}, format='multipart')
        self.assertEqual(response.status_code, 400)
        self.assertIn("No PDF files uploaded.", response.content.decode())  

    def test_upload_invalid_pdf(self):
        pdf_paths = [
            os.path.join(self.test_files_dir, 'sample.txt')
        ]
        
        files = {'pdf': [open(pdf_path, 'rb') for pdf_path in pdf_paths]}

        response = self.client.post(self.upload_url, files, format='multipart')

        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid file", response.content.decode())


